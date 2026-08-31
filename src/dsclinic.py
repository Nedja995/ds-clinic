import os
import datetime
import json
from google.genai import types as genai_types
from npy.core.utils import get_output_data_dirpath, get_input_data_dirpath
from npy.core.fileutils import find_input_documents, make_output_filepath, open_file_from_filepath
import pdf_maker
from models import (
    app_settings,
    get_credential,
    MedicalReportModel,
    GeminiModelConfig,
    AIServiceConfig,
    ClaudeModelConfig,
    ClaudeAIServiceConfig,
    MedicalReport,
)
from api_gemini import client as api_gemini_client
from api_gemini import utils as api_gemini_utils
from api_claude import client as api_claude_client

from npy.core.logger import setup_logger

logger = setup_logger()


class DSClinic:
    """Glavna logika za DSClinic aplikaciju."""

    def __init__(self, model_name: str | None = None):
        # ── settings ──────────────────────────────────────────────────────
        self.input_dir = app_settings.input_dir
        self.output_dir = get_output_data_dirpath()
        self.model_name = model_name or app_settings.ai_model_name
        logger.info(f"Initializing DSClinic with model: {self.model_name}, input_dir: {self.input_dir}, output_dir: {self.output_dir}")

        # ── API keys — sourced from OS keyring only (AD-11) ───────────────
        _gemini_key = get_credential("gemini") or ""
        if not _gemini_key:
            logger.warning(
                "Gemini API key is not set in OS keyring. "
                "Open Settings → AI → Google API Key and save your key."
            )

        _anthropic_key = get_credential("anthropic") or ""
        if not _anthropic_key:
            logger.warning(
                "Anthropic API key is not set in OS keyring. "
                "Open Settings → AI → Anthropic API Key and save your key."
            )

        # ── Gemini client ─────────────────────────────────────────────────
        self.client_config = AIServiceConfig(
            api_key=_gemini_key,
            model_settings=GeminiModelConfig(
                model_name=self.model_name,
                system_instruction=tuple(app_settings.ai_system_instructions),
                thinking_level=app_settings.ai_thinking_level,
                temperature=app_settings.ai_model_temperature,
                top_p=app_settings.ai_model_top_p,
                max_output_tokens=app_settings.ai_model_max_output_tokens,
            )
        )
        self.gemini_client = api_gemini_client.MedicalAnalyzerClient(config=self.client_config)

        # ── Claude client — only instantiated when key is available ───────
        self.claude_client: api_claude_client.ClaudeAnalyzerClient | None = None
        if _anthropic_key:
            try:
                self.claude_config = ClaudeAIServiceConfig(
                    api_key=_anthropic_key,
                    model_settings=ClaudeModelConfig(
                        model_name=app_settings.claude_model_name,
                        temperature=app_settings.ai_model_temperature,
                        top_p=app_settings.ai_model_top_p,
                        max_output_tokens=app_settings.ai_model_max_output_tokens,
                    )
                )
                self.claude_client = api_claude_client.ClaudeAnalyzerClient(config=self.claude_config)
                logger.info("ClaudeAnalyzerClient initialized successfully.")
            except Exception as e:
                logger.warning(f"ClaudeAnalyzerClient failed to initialize: {e}")
        else:
            logger.warning("Claude client not initialized — Anthropic API key not set in keyring.")

        self.report: MedicalReport | None = None

    def get_initial_analysis_report(self, scrubbed_files_map: dict[str, str] | None = None) -> MedicalReport:
        """Glavna funkcija za analizu nalaza."""
        logger.info("Starting initial analysis report generation...")
        if not os.path.exists(self.input_dir):
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        self.input_dir = app_settings.input_dir
        anonymization_enabled = app_settings.anonymization_on

        documents_filepaths = find_input_documents(self.input_dir)
        if not documents_filepaths:
            logger.info(f"Files not found in input directory: {self.input_dir}")

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
                                logger.info(f"PDF Page Mapping active: Loading {page_path} for Gemini")
                                part = api_gemini_utils.load_document_from_file(page_path)
                                if part:
                                    input_documents_parts.append(part)
                    continue

                target_filepath = doc_filepath
                if scrubbed_files_map and doc_filepath in scrubbed_files_map:
                    target_filepath = scrubbed_files_map[doc_filepath]
                    logger.info(f"Anonymization map active: Swapping {doc_filepath} -> {target_filepath}")
            else:
                target_filepath = doc_filepath
                logger.info(f"Anonymization disabled by user: Loading original asset path {target_filepath}")

            part = api_gemini_utils.load_document_from_file(target_filepath)
            if part:
                input_documents_parts.append(part)

        raw_question = app_settings.ai_initial_task_description
        cleaned_question = " ".join(raw_question.split())

        report_content: MedicalReportModel | None = self.gemini_client.initial_analysis_report_from_chat_stream(
            documents=input_documents_parts,
            question=cleaned_question
        )

        if report_content is None:
            raise RuntimeError(
                "Gemini returned an empty or unparseable response. "
                "Check the logs for raw API output. The analysis cannot continue."
            )

        self.report = MedicalReport(content=report_content)
        return self.report

    def ask_followup_question(self, question: str) -> str:
        if not self.report:
            raise ValueError("No initial report available. Please run analysis first.")
        return self.gemini_client.ask_followup_question(question)


def write_report_pdf(report: MedicalReport, output_dir: str | None = None) -> None:
    if output_dir is None:
        output_dir = get_output_data_dirpath()
    output_path = make_output_filepath(report.content.patient_name, "pdf", output_dir)
    pdf_maker.generate_report_pdf_at_filepath(
        report,
        output_filename=output_path
    )
