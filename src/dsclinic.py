"""
src/dsclinic.py — DSClinic core application logic.

Owns: DSClinic — provider lifecycle, document loading, analysis orchestration,
      and follow-up Q&A routing.

The provider-facing interface routes exclusively through LLMProvider / ProviderFactory
(AD-19). Direct SDK client imports no longer exist in this module — all
provider-specific knowledge is encapsulated in src/providers/.

Does NOT own: UI threading, queue communication, or PDF rendering. Those belong
to the ViewModel layer and pdf_maker.py respectively.
"""

import os
from google.genai import types as genai_types
from npy.core.utils import get_output_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath
import pdf_maker
from models import (
    app_settings,
    MedicalReport,
    MedicalReportModel,
)
from api_gemini import utils as api_gemini_utils
from providers import LLMProvider, ProviderFactory, ProviderRequest, ProviderType
from npy.core.logger import setup_logger

logger = setup_logger()


class DSClinic:
    """
    Core application logic for DSClinic.

    Manages the active LLMProvider, document loading/anonymization, and
    delegates all AI calls through the LLMProvider interface. Provider
    construction is handled by ProviderFactory — this class never imports
    or instantiates SDK clients directly.

    active_provider is None only during the brief startup window where no
    provider key is configured. All call sites guard against this and raise
    a RuntimeError with a user-readable Settings navigation hint.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self.input_dir = app_settings.input_dir
        self.output_dir = get_output_data_dirpath()
        # model_name override is kept for CLI compatibility; providers read
        # app_settings.ai_model_name internally by default.
        self.model_name = model_name or app_settings.ai_model_name
        logger.info(
            f"[DSClinic] Initializing — model override: {self.model_name}, "
            f"input_dir: {self.input_dir}"
        )

        self.report: MedicalReport | None = None

        # ── Provider bootstrap — use highest-priority available provider ──
        # Providers read their own keys from keyring; we never touch credentials here.
        self.active_provider: LLMProvider | None = None
        available = ProviderFactory.available_providers()
        if available:
            try:
                self.active_provider = ProviderFactory.create(available[0])
                logger.info(f"[DSClinic] Active provider: {available[0].value}")
            except Exception as exc:
                logger.warning(f"[DSClinic] Failed to construct default provider: {exc}")
        else:
            logger.warning(
                "[DSClinic] No providers available at startup. "
                "Set at least one API key in Settings → AI."
            )

    # ── Provider management ────────────────────────────────────────────────

    def set_active_provider(self, provider_type: ProviderType) -> None:
        """
        Switch the active provider at runtime.

        Raises ValueError when the requested provider is not available
        (key absent, daemon not running, etc.) so the caller (e.g. the
        provider selector in the chat toolbar — v2.12.2) can surface a
        user-readable error without crashing.
        """
        provider = ProviderFactory.create(provider_type)
        if not provider.is_available():
            raise ValueError(
                f"Provider '{provider_type.value}' is not available. "
                "Check that the required API key is set in Settings → AI."
            )
        self.active_provider = provider
        logger.info(f"[DSClinic] Active provider switched to: {provider_type.value}")

    # ── Analysis ───────────────────────────────────────────────────────────

    def get_initial_analysis_report(
        self,
        scrubbed_files_map: dict[str, str] | None = None,
        additional_prompt: str = "",
    ) -> MedicalReport:
        """
        Load documents, apply anonymization, build a ProviderRequest, and
        run the initial structured analysis via the active provider.

        additional_prompt is appended to system_instructions when non-empty.
        This is the only difference between a normal analysis and a reanalysis
        (v2.12.3) — the full document loading and anonymization pipeline runs
        identically in both cases.

        Document loading produces genai_types.Part objects — this is
        currently Gemini-format because api_gemini_utils owns the file →
        Part conversion. When additional provider document formats are
        needed (v2.9.x / v2.12.x), a document adapter layer will be
        introduced. For now GeminiProvider and ClaudeProvider both receive
        the same parts list; GeminiProvider uses them natively, and Claude
        support via a different document format is a future concern.
        """
        if self.active_provider is None:
            raise RuntimeError(
                "No AI provider is available. "
                "Set at least one API key in Settings → AI."
            )

        logger.info("[DSClinic] Starting initial analysis report generation...")

        self.input_dir = app_settings.input_dir
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        anonymization_enabled = app_settings.anonymization_on
        documents_filepaths = find_input_documents(self.input_dir)
        if not documents_filepaths:
            logger.info(f"[DSClinic] No files found in input directory: {self.input_dir}")

        # ── Document loading & anonymization ─────────────────────────────
        input_documents_parts: list[genai_types.Part] = []

        for doc_filepath in documents_filepaths:
            if "ANONIMIZOVANO" in doc_filepath or "_scrubbed" in doc_filepath:
                continue

            if anonymization_enabled:
                if doc_filepath.lower().endswith('.pdf'):
                    parent_dir = os.path.dirname(doc_filepath)
                    filename = os.path.basename(doc_filepath)
                    base, _ = os.path.splitext(filename)
                    anonymized_subfolder = os.path.join(parent_dir, "ANONIMIZOVANO")

                    if os.path.exists(anonymized_subfolder):
                        for file in os.listdir(anonymized_subfolder):
                            if file.startswith(f"{base}_scrubbed_page_") and file.lower().endswith('.jpg'):
                                page_path = os.path.join(anonymized_subfolder, file)
                                logger.info(f"[DSClinic] PDF anonymized page: {page_path}")
                                part = api_gemini_utils.load_document_from_file(page_path)
                                if part:
                                    input_documents_parts.append(part)
                    continue

                target_filepath = doc_filepath
                if scrubbed_files_map and doc_filepath in scrubbed_files_map:
                    target_filepath = scrubbed_files_map[doc_filepath]
                    logger.info(f"[DSClinic] Anonymization map: {doc_filepath} → {target_filepath}")
            else:
                target_filepath = doc_filepath
                logger.info(f"[DSClinic] Anonymization disabled — loading original: {target_filepath}")

            part = api_gemini_utils.load_document_from_file(target_filepath)
            if part:
                input_documents_parts.append(part)

        # Normalise whitespace — keeps config.json readable as multiline text
        # while keeping the API prompt compact and token-efficient (AD per GEMINI.md §3.D).
        raw_question = app_settings.ai_initial_task_description
        cleaned_question = " ".join(raw_question.split())

        # Build system instructions: base config list + optional additional prompt.
        # The additional prompt is appended rather than replacing so the base
        # instructions (JSON schema, language, formatting rules) always apply.
        system_instructions = list(app_settings.ai_system_instructions)
        if additional_prompt:
            cleaned_additional = " ".join(additional_prompt.split())
            system_instructions.append(cleaned_additional)
            logger.info(
                "[DSClinic] Additional prompt appended to system instructions (%d chars).",
                len(cleaned_additional),
            )

        request = ProviderRequest(
            documents=input_documents_parts,
            question=cleaned_question,
            system_instructions=system_instructions,
            temperature=app_settings.ai_model_temperature,
            max_tokens=app_settings.ai_model_max_output_tokens,
        )

        report_content: MedicalReportModel = self.active_provider.analyze(request)

        self.report = MedicalReport(content=report_content)
        return self.report

    # ── Follow-up Q&A ─────────────────────────────────────────────────────

    def ask_followup_question(self, question: str) -> str:
        """
        Stream a follow-up question through the active provider and return
        the accumulated full response string.

        The Iterator[str] contract on LLMProvider.ask() allows the chat view
        to consume chunks as they arrive (v2.12.1). Here we accumulate for
        compatibility with the existing ViewModel polling pattern.
        """
        if self.active_provider is None:
            raise RuntimeError(
                "No AI provider is available. "
                "Set at least one API key in Settings → AI."
            )
        if not self.report:
            raise ValueError("No initial report available. Run analysis first.")

        result: str = "".join(self.active_provider.ask(question))
        return result


def write_report_pdf(report: MedicalReport, output_dir: str | None = None) -> None:
    if output_dir is None:
        output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.content.patient_name, "pdf", output_dir)
    pdf_maker.generate_report_pdf_at_filepath(
        report,
        output_filename=output_path,
    )
