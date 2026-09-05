"""
src/dsclinic_gui/report_view_models.py — DSClinic main ViewModel.

Owns: DSClinicViewModel — all observable state, worker thread management,
      persistence, and provider routing for the main report/chat workflow.

Threading model:
  - Initial analysis: background thread → _analysis_queue (slow, 1 s poll).
  - Follow-up Q&A: background thread → _chat_queue (fast, 100 ms poll).
  - Reanalysis: reuses _run_task_initial_analyzis with an optional extra system
    instruction; result flows through _analysis_queue and _apply_analysis_event
    exactly as initial analysis, with var_reanalysis_summary set on completion
    so the View can add a labeled [Reanalysis] bubble.

Chat response → PDF filtering (v2.12.4):
  _session.chat_history is the single source of truth for all Q&A pairs.
  _model.chat_responses is derived by _rebuild_chat_responses() which
  filters chat_history to bot turns (odd indices) with include_in_report=True.
  set_message_inclusion(bot_index, value) updates the flag and rebuilds.

Does NOT own: UI widgets, dialogs, or tkinter imports beyond tk.StringVar /
BooleanVar / DoubleVar (the minimal observable primitives).
"""
import threading
import queue
import tkinter as tk
import os
import datetime
from typing import Optional, Any, Callable
from dataclasses import dataclass
import multiprocessing

from dsclinic_gui.settings.settings_view_model import SettingsViewModel
from npy.core.logger import setup_logger
from npy.core import utils, fileutils
from models import (
    app_settings,
    MedicalReport,
    MedicalReportModel,
    MedicalCriticalFindingModel,
    MedicalTherapyModel,
    PatientRecord,
)
from models.ai import ChatMessage, ChatSessionModel
from models.brand import brand_config
from db import AppDatabase
from dsclinic import DSClinic
from pdf_maker import generate_report_pdf_at_filepath
from npy.core.event_emitter import EventEmitter, ErrorMessageEvent
from models import TaskStatus, ProgressEvent
from providers import ProviderFactory, ProviderType
from dsclinic_gui.constants import QUEUE_POLL_INTERVAL_MS, CHAT_STREAM_POLL_INTERVAL_MS

logger = setup_logger()

# Maximum analyses per day on the trial subscription tier.
_TRIAL_DAILY_LIMIT: int = 3


# ── Events ─────────────────────────────────────────────────────────────

@dataclass
class ExportRequest:
    """Payload emitted by the ViewModel when a PDF export is ready to proceed."""
    default_filename: str
    default_dir: str


class DSClinicViewModel:

    def __init__(
        self,
        schedule_poll_fn: Callable[[int, Callable[[], None]], Any],
        model: Optional[MedicalReport] = None,
    ) -> None:
        self.schedule_poll_fn = schedule_poll_fn
        self._model: MedicalReport = model or MedicalReport()

        self._db: AppDatabase = AppDatabase()
        self._session: ChatSessionModel = ChatSessionModel(report=self._model)
        self._pending_question: str = ""
        self._streaming_buffer: str = ""
        self._active_patient_id: str = ""

        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings: list[MedicalCriticalFindingModel] = self._model.content.critical_findings
        self.therapy_data: list[MedicalTherapyModel] = self._model.therapies

        self.var_patient_name = tk.StringVar(value=self._model.content.patient_name)
        self.var_report_date = tk.StringVar(value=self._model.report_date)
        self.var_input_dir = tk.StringVar(value=self._model.input_dir)

        self.var_sessions_index: list[dict[str, Any]] = self._db.sessions.list_index()
        self.var_patients_index: list[dict[str, Any]] = self._db.patients.list_index()

        self.var_initial_question = tk.StringVar(value="")

        # var_response: set once at FINISHED — View traces it to call
        # append_chat_response() for persistence. Does NOT drive bubble creation.
        self.var_response = tk.StringVar(value="")

        # var_chunk: set on every CHUNK event with fully accumulated text so far.
        self.var_chunk = tk.StringVar(value="")

        # var_additional_prompt: extra instruction for reanalysis (v2.12.3).
        self.var_additional_prompt = tk.StringVar(
            value=app_settings.ai_initial_task_description
        )

        # var_reanalysis_summary: set on reanalysis completion to trigger the
        # View's labeled [Reanalysis] bubble (v2.12.3).
        self.var_reanalysis_summary = tk.StringVar(value="")

        self.var_status_title = tk.StringVar(value="IDLE")
        self.var_status_detail = tk.StringVar(value="Ready")
        self.var_progress_value = tk.DoubleVar(value=0.0)
        self.var_is_analyzing = tk.BooleanVar(value=False)
        self.var_btn_analyze_text = tk.StringVar(value=_("Analyze"))  # type: ignore[name-defined]

        self._analysis_queue: queue.Queue[ProgressEvent] = queue.Queue()
        self._chat_queue: queue.Queue[ProgressEvent] = queue.Queue()
        self._cancel_event: threading.Event = threading.Event()
        self._worker_thread: threading.Thread | None = None
        self._is_reanalysis: bool = False

        self.on_vm_data_changed:    EventEmitter = EventEmitter()
        self.on_show_error_message: EventEmitter = EventEmitter()
        self.on_export_requested:   EventEmitter = EventEmitter()
        self.on_export_succeeded:   EventEmitter = EventEmitter()
        self.on_sessions_changed:   EventEmitter = EventEmitter()
        self.on_patients_changed:   EventEmitter = EventEmitter()

        self.dsclinicapp = DSClinic(model_name=app_settings.ai_model_name)

        _initial_provider = (
            self.dsclinicapp.active_provider.provider_type().value
            if self.dsclinicapp.active_provider is not None
            else ""
        )
        self.var_active_provider = tk.StringVar(value=_initial_provider)

    def _update_viewmodel_from_model(self) -> None:
        logger.debug("Updating ViewModel from Model...")
        self.therapy_text_content = self._model.content.recommended_therapy_and_advice
        self.findings             = self._model.content.critical_findings
        self.var_patient_name.set(self._model.content.patient_name)
        self.var_report_date.set(self._model.report_date)
        self.var_input_dir.set(self._model.input_dir)

    def _update_model_from_viewmodel(self) -> None:
        logger.debug("Updating Model from ViewModel...")
        self._model.content.patient_name                   = self.var_patient_name.get()
        self._model.report_date                            = self.var_report_date.get()
        self._model.input_dir                              = self.var_input_dir.get()
        self._model.content.recommended_therapy_and_advice = self.therapy_text_content
        self._model.content.critical_findings              = self.findings
        self._model.therapies                              = self.therapy_data

    # ── Provider selector ─────────────────────────────────────────────────────

    def available_provider_names(self) -> list[str]:
        """Return display names of all currently available providers."""
        try:
            return [p.value for p in ProviderFactory.available_providers()]
        except Exception as exc:
            logger.error("Failed to query available providers: %s", exc)
            return []

    def set_provider_by_name(self, name: str) -> None:
        """Switch the active provider by ProviderType.value display name."""
        if not name:
            return
        try:
            provider_type = ProviderType(name)
            self.dsclinicapp.set_active_provider(provider_type)
            self.var_active_provider.set(name)
            logger.info("Active provider switched to %r via selector.", name)
        except ValueError as exc:
            logger.warning("Provider switch failed: %s", exc)
            self.on_show_error_message.emit(ErrorMessageEvent(
                title="Provider Unavailable",
                message=str(exc),
            ))
            if self.dsclinicapp.active_provider is not None:
                self.var_active_provider.set(
                    self.dsclinicapp.active_provider.provider_type().value
                )

    # ── Chat response filtering (v2.12.4) ─────────────────────────────────────

    def _rebuild_chat_responses(self) -> None:
        """Rebuild _model.chat_responses from filtered chat_history bot turns.

        Bot messages occupy odd indices in chat_history (0=user, 1=bot, 2=user,
        3=bot …). Only bot messages with include_in_report=True are written to
        _model.chat_responses, which is what pdf_maker reads for the PDF export.

        Called after any mutation to chat_history or include_in_report flags so
        _model.chat_responses is always consistent with the filter state.
        """
        bot_messages = [
            msg for i, msg in enumerate(self._session.chat_history)
            if i % 2 == 1  # odd index = bot response
        ]
        self._model.chat_responses = [
            msg.content for msg in bot_messages if msg.include_in_report
        ]
        logger.debug(
            "_rebuild_chat_responses: %d bot messages, %d included in report.",
            len(bot_messages),
            len(self._model.chat_responses),
        )

    def set_message_inclusion(self, bot_index: int, value: bool) -> None:
        """Toggle include_in_report on a specific bot message by its bot-turn index.

        bot_index is the 0-based index into bot messages only (not chat_history).
        The corresponding chat_history index is 2*bot_index + 1.

        Called by the View's Checkbutton trace on each bot bubble. Out-of-range
        indices are silently ignored — the View may call this briefly before the
        ViewModel's history is fully populated on session load.
        """
        history_index = 2 * bot_index + 1
        if history_index >= len(self._session.chat_history):
            logger.warning(
                "set_message_inclusion: history_index %d out of range (%d entries) — ignored.",
                history_index, len(self._session.chat_history),
            )
            return

        self._session.chat_history[history_index].include_in_report = value
        self._rebuild_chat_responses()
        logger.debug(
            "Bot message %d include_in_report set to %s.", bot_index, value
        )

    # ── Persistence helpers ───────────────────────────────────────────────────

    def _persist_report(self, report: MedicalReport) -> None:
        try:
            self._db.reports.save(report.report_id, report)
            logger.info("Report %r auto-saved to AppDatabase.", report.report_id)
        except (OSError, Exception) as e:
            logger.error("Failed to auto-save report %r: %s", report.report_id, e, exc_info=True)

    def _persist_session(self) -> None:
        self._session.report = self._model
        try:
            self._db.sessions.save(self._session.session_id, self._session)
            logger.info("Session %r auto-saved to AppDatabase.", self._session.session_id)
        except (OSError, Exception) as e:
            logger.error("Failed to auto-save session %r: %s", self._session.session_id, e, exc_info=True)

        if self._active_patient_id:
            self._link_session_to_patient(self._session.session_id, self._active_patient_id)

        self._refresh_sessions_index()

    def _link_session_to_patient(self, session_id: str, patient_id: str) -> None:
        try:
            patient = self._db.patients.load(patient_id)
            if patient is None:
                logger.warning("Cannot link session: patient %r not found.", patient_id)
                return
            if session_id not in patient.session_ids:
                patient.session_ids.insert(0, session_id)
                self._db.patients.save(patient_id, patient)
                logger.debug("Linked session %r to patient %r.", session_id, patient_id)
                self._refresh_patients_index()
        except (OSError, Exception) as e:
            logger.error("Failed to link session %r to patient %r: %s", session_id, patient_id, e, exc_info=True)

    def _refresh_sessions_index(self) -> None:
        try:
            self.var_sessions_index = self._db.sessions.list_index()
        except (OSError, Exception) as e:
            logger.error("Failed to refresh sessions index: %s", e, exc_info=True)
            self.var_sessions_index = []
        self.on_sessions_changed.emit()

    def _refresh_patients_index(self) -> None:
        try:
            self.var_patients_index = self._db.patients.list_index()
        except (OSError, Exception) as e:
            logger.error("Failed to refresh patients index: %s", e, exc_info=True)
            self.var_patients_index = []
        self.on_patients_changed.emit()

    # ── Patient management ────────────────────────────────────────────────────

    def save_new_patient(self, full_name: str, date_of_birth: str) -> None:
        full_name = full_name.strip()
        if not full_name:
            logger.warning("save_new_patient called with empty full_name — ignored.")
            return
        patient = PatientRecord(full_name=full_name, date_of_birth=date_of_birth.strip())
        try:
            self._db.patients.save(patient.patient_id, patient)
            logger.info("New patient %r (%r) saved.", patient.patient_id, patient.full_name)
        except (OSError, Exception) as e:
            logger.error("Failed to save new patient: %s", e, exc_info=True)
            self.on_show_error_message.emit(ErrorMessageEvent(title="Save Failed", message=f"Could not save patient record: {e}"))
            return
        self._refresh_patients_index()

    def set_active_patient(self, patient_id: str) -> None:
        self._active_patient_id = patient_id
        logger.debug("Active patient set to %r.", patient_id or "(none)")

    # ── Session management ────────────────────────────────────────────────────

    def load_session(self, session_id: str) -> None:
        if self.var_is_analyzing.get():
            logger.warning("Cannot load session while analysis is running.")
            return
        try:
            loaded_session = self._db.sessions.load(session_id)
        except (OSError, Exception) as e:
            logger.error("Failed to load session %r: %s", session_id, e, exc_info=True)
            self.on_show_error_message.emit(ErrorMessageEvent(title="Load Failed", message=f"Could not load session: {e}"))
            return
        if loaded_session is None:
            self.on_show_error_message.emit(ErrorMessageEvent(title="Not Found", message=f"Session {session_id!r} not found on disk."))
            return
        self._session = loaded_session
        self._model = loaded_session.report
        self._pending_question = ""
        self._update_viewmodel_from_model()
        self.on_vm_data_changed.emit()
        logger.info("Session %r loaded and restored.", session_id)

    def new_session(self) -> None:
        if self.var_is_analyzing.get():
            logger.warning("Cannot start new session while analysis is running.")
            return
        self._model = MedicalReport()
        self._session = ChatSessionModel(report=self._model)
        self._pending_question = ""
        self._streaming_buffer = ""
        self.therapy_text_content = ""
        self.findings = []
        self.therapy_data = []
        self.var_patient_name.set(self._model.content.patient_name)
        self.var_report_date.set(self._model.report_date)
        self.var_input_dir.set(self._model.input_dir)
        self.var_response.set("")
        self.var_chunk.set("")
        self.var_initial_question.set("")
        self.var_additional_prompt.set(app_settings.ai_initial_task_description)
        self.var_reanalysis_summary.set("")
        self.var_status_title.set("IDLE")
        self.var_status_detail.set("Ready")
        self.var_progress_value.set(0.0)
        self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
        self.on_vm_data_changed.emit()
        logger.info("New session started.")

    # --- Logic: Data Management ---

    def add_finding(self) -> None:
        self.findings.append(MedicalCriticalFindingModel())

    def remove_finding(self, index: int) -> None:
        if 0 <= index < len(self.findings):
            self.findings.pop(index)

    def add_therapy(self) -> None:
        self.therapy_data.append(MedicalTherapyModel())

    def remove_therapy(self, index: int) -> None:
        if 0 <= index < len(self.therapy_data):
            self.therapy_data.pop(index)

    # --- Logic: Chat ---

    def append_chat_response(self, text: str) -> None:
        """Synchronise _model.chat_responses after the View acknowledges a bot bubble.

        Called by ChatSessionView._on_response_finalised() when var_response is
        set. Instead of directly appending, we rebuild from chat_history so that
        include_in_report flags on any previously toggled messages are respected.
        The text argument is ignored — chat_history is the source of truth.
        """
        self._rebuild_chat_responses()

    # --- Logic: Analysis ---

    def toggle_analysis(self) -> None:
        if not self.var_is_analyzing.get():
            self._start_analysis()
        else:
            self._cancel_analysis()

    def reanalyze(self) -> None:
        """Re-run initial analysis with the current additional prompt as extra context."""
        if self.var_is_analyzing.get():
            logger.warning("reanalyze() called while a task is already running — ignored.")
            return

        additional_prompt = self.var_additional_prompt.get().strip()

        if not brand_config.is_feature_allowed("unlimited_sessions"):
            today_str = datetime.date.today().isoformat()
            try:
                all_sessions = self._db.sessions.list_index()
                todays_count = sum(
                    1 for s in all_sessions
                    if str(s.get("created_at", "")).startswith(today_str)
                )
            except (OSError, Exception) as e:
                logger.warning("Could not count today's sessions for trial limit check: %s", e)
                todays_count = 0

            if todays_count >= _TRIAL_DAILY_LIMIT:
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Trial Limit Reached",
                    message=(
                        f"Your trial plan allows {_TRIAL_DAILY_LIMIT} analyses per day. "
                        "Upgrade to Standard or Enterprise to remove this limit."
                    ),
                ))
                return

        self._is_reanalysis = True
        self.var_is_analyzing.set(True)
        self.var_status_title.set("Reanalyzing")
        self.var_status_detail.set("Running reanalysis with updated prompt...")
        self.var_progress_value.set(0)
        self._cancel_event.clear()

        self._worker_thread = threading.Thread(
            target=self._run_task_initial_analyzis,
            args=(self._analysis_queue, self._cancel_event, additional_prompt),
            daemon=True,
            name="dsclinic-reanalyze-thread",
        )
        self._worker_thread.start()
        self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_analysis_queue)
        logger.info("Reanalysis launched with additional_prompt=%r", additional_prompt[:80])

    def _reset_task_state(self) -> None:
        self._cancel_event.clear()
        self._analysis_queue = queue.Queue()
        self._is_reanalysis = False
        self.var_is_analyzing.set(False)
        self.var_status_title.set("Cancelling")
        self.var_status_detail.set("Cancelling analysis...")

    def _start_analysis(self) -> None:
        if not brand_config.is_feature_allowed("unlimited_sessions"):
            today_str = datetime.date.today().isoformat()
            try:
                all_sessions = self._db.sessions.list_index()
                todays_count = sum(
                    1 for s in all_sessions
                    if str(s.get("created_at", "")).startswith(today_str)
                )
            except (OSError, Exception) as e:
                logger.warning("Could not count today's sessions for trial limit check: %s", e)
                todays_count = 0

            if todays_count >= _TRIAL_DAILY_LIMIT:
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Trial Limit Reached",
                    message=(
                        f"Your trial plan allows {_TRIAL_DAILY_LIMIT} analyses per day. "
                        "Upgrade to Standard or Enterprise to remove this limit."
                    ),
                ))
                logger.info("Trial daily limit reached (%d/%d) — analysis blocked.", todays_count, _TRIAL_DAILY_LIMIT)
                return

        self._is_reanalysis = False
        self.var_is_analyzing.set(True)
        self.var_btn_analyze_text.set("Cancel")
        self.var_status_title.set("Running")
        self.var_status_detail.set("Running heavy task...")
        self.var_progress_value.set(0)
        self._cancel_event.clear()

        self._worker_thread = threading.Thread(
            target=self._run_task_initial_analyzis,
            args=(self._analysis_queue, self._cancel_event),
            daemon=True,
            name="dsclinic-gemini-thread",
        )
        self._worker_thread.start()
        self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_analysis_queue)

    def _cancel_analysis(self) -> None:
        self._reset_task_state()
        self._cancel_event.set()

    def _run_task_initial_analyzis(
        self,
        output_queue: queue.Queue[ProgressEvent],
        cancel_event: threading.Event,
        additional_prompt: str = "",
    ) -> None:
        try:
            output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Finding local medical files..."))

            input_dir = self.var_input_dir.get()
            from npy.core.fileutils import find_input_documents
            documents_filepaths = find_input_documents(input_dir)

            scrubbed_files_map: dict[str, str] = {}
            anonymization_enabled = app_settings.anonymization_on

            if documents_filepaths and anonymization_enabled:
                output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Initializing local privacy layers..."))

                mp_input_queue: multiprocessing.Queue[Any] = multiprocessing.Queue()
                mp_output_queue: multiprocessing.Queue[Any] = multiprocessing.Queue()

                from dsclinic_gui.redaction_worker import redaction_worker_process
                worker = multiprocessing.Process(
                    target=redaction_worker_process,
                    args=(mp_input_queue, mp_output_queue),
                    daemon=True,
                )
                worker.start()

                for doc_path in documents_filepaths:
                    parent_dir = os.path.dirname(doc_path)
                    filename = os.path.basename(doc_path)
                    base, ext = os.path.splitext(filename)

                    anonymized_subfolder = os.path.join(parent_dir, "ANONIMIZOVANO")
                    if not os.path.exists(anonymized_subfolder):
                        os.makedirs(anonymized_subfolder, exist_ok=True)

                    scrubbed_path = os.path.join(anonymized_subfolder, f"{base}_scrubbed{ext}")
                    scrubbed_files_map[doc_path] = scrubbed_path
                    mp_input_queue.put({"input_path": doc_path, "output_path": scrubbed_path})

                files_processed = 0
                scrubbed_text_data_list: list[str] = []

                while files_processed < len(documents_filepaths) and not cancel_event.is_set():
                    try:
                        process_result = mp_output_queue.get(timeout=0.2)
                        if process_result.get("status") == "DOWNLOADING_MODELS":
                            output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message=process_result.get("message")))
                            continue
                        if process_result.get("status") == "ERROR":
                            raise Exception(f"Local Scrub Failure: {process_result.get('error_message')}")
                        if process_result.get("status") == "SUCCESS":
                            if "sanitized_text" in process_result:
                                scrubbed_text_data_list.append(process_result["sanitized_text"])
                            files_processed += 1
                            output_queue.put(ProgressEvent(
                                status=TaskStatus.RUNNING,
                                message=f"Locally scrubbed {files_processed}/{len(documents_filepaths)} files...",
                            ))
                    except queue.Empty:
                        continue

                mp_input_queue.put(None)
                worker.join()

            elif documents_filepaths and not anonymization_enabled:
                output_queue.put(ProgressEvent(status=TaskStatus.RUNNING, message="Bypassing local data obfuscation layer..."))

            if cancel_event.is_set():
                output_queue.put(ProgressEvent(status=TaskStatus.CANCELED, message="Analysis cancelled."))
                return

            output_queue.put(ProgressEvent(status=TaskStatus.PROGRESS, message="Sending safely anonymized data to AI provider...", elapsed_seconds=2))

            report: MedicalReport = self.dsclinicapp.get_initial_analysis_report(
                scrubbed_files_map=scrubbed_files_map,
                additional_prompt=additional_prompt,
            )
            output_queue.put(ProgressEvent(status=TaskStatus.FINISHED, message="Analysis complete", result=report))

        except Exception as e:
            logger.critical(f"Error during analysis: {str(e)}", exc_info=True)
            output_queue.put(ProgressEvent(status=TaskStatus.FAILED, message="Task failed", result=str(e)))

    def followup_question_submit(self) -> None:
        question = self.var_initial_question.get().strip()
        if not question or self.var_is_analyzing.get():
            return

        self.var_initial_question.set("")
        self.var_is_analyzing.set(True)
        self.var_status_title.set("Chatting")
        self.var_status_detail.set("Waiting for AI response...")
        self.var_progress_value.set(0)
        self._streaming_buffer = ""
        self.var_chunk.set("")
        self._pending_question = question

        self._worker_thread = threading.Thread(
            target=self._run_task_followup_question,
            args=(question, self._chat_queue),
            daemon=True,
            name="dsclinic-chat-thread",
        )
        self._worker_thread.start()
        self.schedule_poll_fn(CHAT_STREAM_POLL_INTERVAL_MS, self._poll_chat_queue)

    def _run_task_followup_question(self, question: str, output_queue: queue.Queue[ProgressEvent]) -> None:
        try:
            accumulated: str = ""
            for chunk in self.dsclinicapp.active_provider.ask(question):  # type: ignore[union-attr]
                accumulated += chunk
                output_queue.put(ProgressEvent(status=TaskStatus.CHUNK, message=accumulated))
            output_queue.put(ProgressEvent(status=TaskStatus.FINISHED, result=accumulated))
        except Exception as e:
            logger.error(f"Error in chat followup: {e}", exc_info=True)
            output_queue.put(ProgressEvent(status=TaskStatus.FAILED, message=str(e), result=str(e)))

    # ── Queue pollers ─────────────────────────────────────────────────────────

    def _poll_analysis_queue(self) -> None:
        task_still_running = True
        try:
            while True:
                event: ProgressEvent = self._analysis_queue.get_nowait()
                task_still_running = self._apply_analysis_event(event)
        except queue.Empty:
            pass
        if task_still_running:
            self.schedule_poll_fn(QUEUE_POLL_INTERVAL_MS, self._poll_analysis_queue)

    def _poll_chat_queue(self) -> None:
        task_still_running = True
        try:
            while True:
                event: ProgressEvent = self._chat_queue.get_nowait()
                task_still_running = self._apply_chat_event(event)
        except queue.Empty:
            pass
        if task_still_running:
            self.schedule_poll_fn(CHAT_STREAM_POLL_INTERVAL_MS, self._poll_chat_queue)

    def _apply_analysis_event(self, progress_event: ProgressEvent) -> bool:
        logger.debug(f"Applying analysis ProgressEvent: {progress_event}")
        match progress_event.status:
            case TaskStatus.RUNNING:
                self.var_status_title.set("Starting analysis...")
                self.var_status_detail.set(f"Task: {progress_event.message}")
                self.var_progress_value.set(0)
                return True

            case TaskStatus.PROGRESS:
                self.var_status_title.set("Analyzing...")
                self.var_status_detail.set(f"progress: {progress_event.message}, elapsed_seconds: {progress_event.elapsed_seconds}")
                self.var_progress_value.set((progress_event.elapsed_seconds / 10) * 100)
                return True

            case TaskStatus.FINISHED:
                if progress_event.result and isinstance(progress_event.result, MedicalReport):
                    self._model = progress_event.result
                    self._update_viewmodel_from_model()
                    self.var_progress_value.set(100)
                    self.var_status_detail.set("Analysis completed successfully.")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                    self.on_vm_data_changed.emit()

                    if self._is_reanalysis:
                        summary = self._model.content.patient_name or "Reanalysis complete"
                        self.var_reanalysis_summary.set(summary)
                        self._is_reanalysis = False

                    self._persist_report(self._model)
                    self._session = ChatSessionModel(report=self._model)
                    self._persist_session()

                else:
                    error_msg = f"Unexpected result type in ProgressEvent: {type(progress_event.result)}. Expected MedicalReport."
                    logger.error(error_msg)
                    self.show_error_message("Error", error_msg)
                    self.var_status_title.set("Finished")
                    self.var_progress_value.set(50)
                    self.var_status_detail.set("Analysis Failed with error: 'Unexpected result type.'")
                    self.var_is_analyzing.set(False)
                    self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                    self._is_reanalysis = False
                return False

            case TaskStatus.CANCELED:
                self.var_is_analyzing.set(False)
                self.var_status_title.set("Cancelled")
                self.var_status_detail.set("✖ " + progress_event.message)
                self._is_reanalysis = False
                return False

            case TaskStatus.FAILED:
                self.var_is_analyzing.set(False)
                self.var_btn_analyze_text.set(_("Analyze"))  # type: ignore[name-defined]
                error_msg = f"Analysis failed with error: {progress_event.result}"
                logger.error(error_msg)
                self.var_status_title.set("Failed")
                self.var_status_detail.set("✖ " + progress_event.message)
                self.on_show_error_message.emit(ErrorMessageEvent(
                    title="Analysis Failed",
                    message=error_msg if error_msg else "An unknown error occurred.",
                ))
                self._is_reanalysis = False
                return False

            case _:
                error_msg = f"Received analysis ProgressEvent with unknown status: {progress_event.status}"
                logger.error(error_msg)
                self.on_show_error_message.emit(ErrorMessageEvent(title="Error", message=error_msg))
                return True

    def _apply_chat_event(self, progress_event: ProgressEvent) -> bool:
        logger.debug(f"Applying chat ProgressEvent: {progress_event}")
        match progress_event.status:
            case TaskStatus.CHUNK:
                self._streaming_buffer = progress_event.message
                self.var_chunk.set(progress_event.message)
                return True

            case TaskStatus.FINISHED:
                answer = progress_event.result if isinstance(progress_event.result, str) else ""
                self.var_response.set(answer)
                self.var_is_analyzing.set(False)
                self.var_status_title.set("Ready")
                self.var_status_detail.set("Chat response received.")
                self.var_progress_value.set(100)

                # Persist Q&A pair in chat_history (include_in_report=True by default).
                # _rebuild_chat_responses() is called by append_chat_response() when
                # the View's var_response trace fires — no double-call needed here.
                if self._pending_question:
                    self._session.chat_history.append(ChatMessage(content=self._pending_question))
                    self._session.chat_history.append(ChatMessage(content=answer))
                    self._pending_question = ""
                self._persist_session()
                return False

            case TaskStatus.FAILED:
                self.var_is_analyzing.set(False)
                error_msg = f"Chat failed: {progress_event.message}"
                logger.error(error_msg)
                self.var_status_title.set("Failed")
                self.var_status_detail.set("✖ " + progress_event.message)
                self.on_show_error_message.emit(ErrorMessageEvent(title="Chat Failed", message=error_msg))
                return False

            case _:
                logger.error("Unexpected status in chat queue: %s", progress_event.status)
                return True

    # Logic: View Updates / Error Handling / Export

    def update_view_from_viewmodel(self) -> None:
        self.on_vm_data_changed.emit()

    def show_error_message(self, title: str, message: str) -> None:
        self.on_show_error_message.emit(ErrorMessageEvent(title=title, message=message))

    def prepare_export(self) -> None:
        """Step 1 of the export flow — emits ExportRequest so View shows file dialog."""
        self._update_model_from_viewmodel()
        patient_slug = self.var_patient_name.get().replace(".", " ").replace("/", "")
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        default_name = f"NALAZ_{patient_slug}_{timestamp_str}.pdf"
        output_dir = utils.get_output_data_dirpath()
        self.on_export_requested.emit(ExportRequest(default_filename=default_name, default_dir=output_dir))

    def execute_export(self, output_filepath: str) -> None:
        """Step 2 of the export flow — generates PDF, emits error on failure."""
        self.var_status_title.set("Exporting")
        self.var_status_detail.set(f"Generating PDF at {output_filepath}...")

        try:
            generate_report_pdf_at_filepath(self._model, output_filename=output_filepath)
        except Exception as e:
            error_msg = f"PDF export failed: {e}"
            logger.error(error_msg, exc_info=True)
            self.var_status_title.set("Export Failed")
            self.var_status_detail.set("✖ PDF generation error.")
            self.on_show_error_message.emit(ErrorMessageEvent(title="Export Failed", message=error_msg))
            return

        self.var_status_title.set("Saved")
        self.var_status_detail.set("PDF Saved Successfully")
        self.on_export_succeeded.emit(output_filepath)
