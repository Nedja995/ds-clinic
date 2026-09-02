"""
Session history and patient list sidebar view.

Owns: the leftmost sidebar pane, structured as a ttk.Notebook with two tabs:
  - "Sessions" — scrollable list of saved sessions, load/new-session controls.
  - "Patients" — scrollable list of patients, inline new-patient form, patient
    selection that filters the Sessions tab to that patient's sessions only.

Does NOT own: persistence, DB access, or business logic — those belong
exclusively to DSClinicViewModel. This View calls only:
  view_model.load_session(), view_model.new_session(),
  view_model.save_new_patient(), view_model.set_active_patient().
"""
from __future__ import annotations

from typing import Any

import tkinter as tk
from tkinter import ttk

from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.styles import (
    ACCENT, BORDER, PANEL, SIDEBAR_BG, SUBTLE, TEXT, WHITE,
    FB, FH, FS,
)
from npy.core.logger import setup_logger

logger = setup_logger()

# ── Index key constants — produced by JsonCollection from dot-path fields ──────
_S_KEY_ID      = "session_id"
_S_KEY_PATIENT = "report_content_patient_name"
_S_KEY_DATE    = "report_report_date"

_P_KEY_ID      = "patient_id"
_P_KEY_NAME    = "full_name"
_P_KEY_DATE    = "created_at"


class SessionHistoryView(ttk.Frame):
    """
    Two-tab sidebar: Sessions and Patients.

    Sessions tab: lists all saved sessions (or the active patient's sessions
    when a patient filter is applied). Clicking a row restores that session.

    Patients tab: lists all saved patients. Clicking a patient filters the
    Sessions tab to show only that patient's sessions. A "New Patient" form
    at the bottom creates and persists a PatientRecord.

    Layout invariant: always the leftmost pane in MainContainerView.
    """

    def __init__(
        self,
        parent: tk.Misc,
        view_model: DSClinicViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._vm = view_model

        # patient_id of the currently selected patient for session filtering,
        # or empty string when showing all sessions.
        self._filter_patient_id: str = ""

        # session_ids belonging to the active patient filter. Rebuilt whenever
        # the patient selection changes or the patient index refreshes.
        self._filter_session_ids: set[str] = set()

        self._setup_ui()

        self._vm.on_sessions_changed.subscribe(self._rebuild_sessions)
        self._vm.on_patients_changed.subscribe(self._rebuild_patients)

        # Populate immediately from whatever is already on disk.
        self._rebuild_sessions()
        self._rebuild_patients()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.configure(style="SidebarPanel.TFrame")

        # ── Header strip ──────────────────────────────────────────────────
        header = ttk.Frame(self, style="SidebarStrip.TFrame", height=30)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        ttk.Label(
            header,
            text="HISTORY",
            style="SidebarTitle.TLabel",
            anchor="center",
        ).pack(fill="both", expand=True)

        # ── Notebook ──────────────────────────────────────────────────────
        self._notebook = ttk.Notebook(self)
        self._notebook.pack(fill="both", expand=True, padx=0, pady=0)

        self._tab_sessions = ttk.Frame(self._notebook, style="SidebarPanel.TFrame")
        self._tab_patients = ttk.Frame(self._notebook, style="SidebarPanel.TFrame")

        self._notebook.add(self._tab_sessions, text="Sessions")
        self._notebook.add(self._tab_patients, text="Patients")

        self._build_sessions_tab(self._tab_sessions)
        self._build_patients_tab(self._tab_patients)

    # ── Sessions tab ──────────────────────────────────────────────────────────

    def _build_sessions_tab(self, parent: ttk.Frame) -> None:
        # New Session button
        ttk.Button(
            parent,
            text="+ New Session",
            style="Accent.TButton",
            command=self._on_new_session,
        ).pack(fill="x", padx=4, pady=(4, 2))

        # Active filter indicator — hidden when no filter is applied.
        self._lbl_filter = ttk.Label(
            parent,
            text="",
            style="SidebarEmpty.TLabel",
            anchor="w",
        )
        self._lbl_filter.pack(fill="x", padx=6, pady=(0, 2))

        ttk.Separator(parent, orient="horizontal").pack(fill="x")

        # Scrollable session list
        list_wrap = ttk.Frame(parent, style="SidebarPanel.TFrame")
        list_wrap.pack(fill="both", expand=True)

        self._sessions_scrollbar = ttk.Scrollbar(list_wrap, orient="vertical")
        # tk.Listbox: no ttk equivalent with per-item styling — kept intentionally.
        self._sessions_listbox = tk.Listbox(
            list_wrap,
            yscrollcommand=self._sessions_scrollbar.set,
            selectmode=tk.SINGLE,
            bg=PANEL, fg=TEXT, font=FS,
            relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none",
            selectbackground=ACCENT,
            selectforeground=WHITE,
            cursor="hand2",
        )
        self._sessions_scrollbar.config(command=self._sessions_listbox.yview)
        self._sessions_scrollbar.pack(side="right", fill="y")
        self._sessions_listbox.pack(side="left", fill="both", expand=True)
        self._sessions_listbox.bind("<<ListboxSelect>>", self._on_session_selected)

        self._lbl_sessions_empty = ttk.Label(
            list_wrap,
            text="No sessions yet.\nRun an analysis to\ncreate the first one.",
            style="SidebarEmpty.TLabel",
            anchor="center",
            justify="center",
        )

        # Parallel index: listbox position → session_id.
        self._session_ids: list[str] = []

    # ── Patients tab ──────────────────────────────────────────────────────────

    def _build_patients_tab(self, parent: ttk.Frame) -> None:
        # Scrollable patient list
        list_wrap = ttk.Frame(parent, style="SidebarPanel.TFrame")
        list_wrap.pack(fill="both", expand=True)

        self._patients_scrollbar = ttk.Scrollbar(list_wrap, orient="vertical")
        self._patients_listbox = tk.Listbox(
            list_wrap,
            yscrollcommand=self._patients_scrollbar.set,
            selectmode=tk.SINGLE,
            bg=PANEL, fg=TEXT, font=FS,
            relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none",
            selectbackground=ACCENT,
            selectforeground=WHITE,
            cursor="hand2",
        )
        self._patients_scrollbar.config(command=self._patients_listbox.yview)
        self._patients_scrollbar.pack(side="right", fill="y")
        self._patients_listbox.pack(side="left", fill="both", expand=True)
        self._patients_listbox.bind("<<ListboxSelect>>", self._on_patient_selected)

        self._lbl_patients_empty = ttk.Label(
            list_wrap,
            text="No patients yet.\nAdd one below.",
            style="SidebarEmpty.TLabel",
            anchor="center",
            justify="center",
        )

        # Parallel index: listbox position → patient_id.
        self._patient_ids: list[str] = []

        # ── New Patient inline form ────────────────────────────────────────
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=(2, 0))

        form = ttk.Frame(parent, style="SidebarPanel.TFrame", padding=(6, 4))
        form.pack(fill="x", side="bottom")

        ttk.Label(form, text="New Patient", style="SidebarFormLabel.TLabel").pack(anchor="w")

        ttk.Label(form, text="Full name", style="SidebarEmpty.TLabel").pack(anchor="w", pady=(4, 0))
        self._ent_full_name = ttk.Entry(form, font=FS)
        self._ent_full_name.pack(fill="x", pady=(0, 4))

        ttk.Label(form, text="Date of birth (DD.MM.YYYY.)", style="SidebarEmpty.TLabel").pack(anchor="w")
        self._ent_dob = ttk.Entry(form, font=FS)
        self._ent_dob.pack(fill="x", pady=(0, 6))

        ttk.Button(
            form,
            text="Save Patient",
            style="Accent.TButton",
            command=self._on_save_patient,
        ).pack(fill="x")

    # ── Session list management ───────────────────────────────────────────────

    def _rebuild_sessions(self) -> None:
        """Repopulate the sessions listbox, applying the patient filter if set."""
        self._sessions_listbox.delete(0, tk.END)
        self._session_ids.clear()

        all_entries: list[dict[str, Any]] = self._vm.var_sessions_index

        # Apply patient filter when a patient is selected: only show sessions
        # whose session_id is in the patient's session_ids set.
        if self._filter_patient_id and self._filter_session_ids:
            entries = [
                e for e in all_entries
                if str(e.get(_S_KEY_ID, "")) in self._filter_session_ids
            ]
        else:
            entries = all_entries

        if not entries:
            self._lbl_sessions_empty.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            return

        self._lbl_sessions_empty.place_forget()

        for entry in entries:
            session_id = str(entry.get(_S_KEY_ID, ""))
            patient    = str(entry.get(_S_KEY_PATIENT, "") or "Unknown patient")
            date       = str(entry.get(_S_KEY_DATE,    "") or "")
            label      = f"{patient}\n{date}" if date else patient

            self._sessions_listbox.insert(tk.END, label)
            self._session_ids.append(session_id)

        logger.debug("SessionHistoryView: sessions rebuilt — %d entries shown.", len(entries))

    def _update_filter_label(self) -> None:
        """Update the filter indicator label above the sessions list."""
        if self._filter_patient_id:
            # Find the patient name from the current index.
            name = next(
                (
                    str(p.get(_P_KEY_NAME, ""))
                    for p in self._vm.var_patients_index
                    if str(p.get(_P_KEY_ID, "")) == self._filter_patient_id
                ),
                "Unknown",
            )
            self._lbl_filter.config(text=f"Filter: {name}")
        else:
            self._lbl_filter.config(text="")

    # ── Patient list management ───────────────────────────────────────────────

    def _rebuild_patients(self) -> None:
        """Repopulate the patients listbox from view_model.var_patients_index."""
        self._patients_listbox.delete(0, tk.END)
        self._patient_ids.clear()

        entries = self._vm.var_patients_index

        if not entries:
            self._lbl_patients_empty.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            return

        self._lbl_patients_empty.place_forget()

        for entry in entries:
            patient_id = str(entry.get(_P_KEY_ID,   ""))
            name       = str(entry.get(_P_KEY_NAME, "") or "Unknown patient")
            date       = str(entry.get(_P_KEY_DATE,  "") or "")
            label      = f"{name}\n{date}" if date else name

            self._patients_listbox.insert(tk.END, label)
            self._patient_ids.append(patient_id)

        # Restore the visual selection if the active filter is still in the list.
        if self._filter_patient_id and self._filter_patient_id in self._patient_ids:
            idx = self._patient_ids.index(self._filter_patient_id)
            self._patients_listbox.selection_set(idx)

        logger.debug("SessionHistoryView: patients rebuilt — %d entries.", len(entries))

    def _load_patient_session_ids(self, patient_id: str) -> set[str]:
        """Load the session_ids set for a patient directly from the DB.

        Uses a direct DB load rather than the index because session_ids are
        not included in the flat patient index entries.
        """
        try:
            patient = self._vm._db.patients.load(patient_id)
            if patient is not None:
                return set(patient.session_ids)
        except (OSError, Exception) as e:
            logger.error("Failed to load patient %r for filter: %s", patient_id, e)
        return set()

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_session_selected(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        """Load the session the user clicked."""
        selection = self._sessions_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self._session_ids):
            return
        session_id = self._session_ids[index]
        logger.debug("SessionHistoryView: user selected session %r.", session_id)
        self._vm.load_session(session_id)

    def _on_patient_selected(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        """Set the patient filter and switch to the Sessions tab.

        Clicking the already-selected patient clears the filter (toggle behaviour).
        """
        selection = self._patients_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self._patient_ids):
            return
        patient_id = self._patient_ids[index]

        if patient_id == self._filter_patient_id:
            # Toggle off — clear filter.
            self._filter_patient_id = ""
            self._filter_session_ids = set()
            self._patients_listbox.selection_clear(0, tk.END)
            self._vm.set_active_patient("")
        else:
            self._filter_patient_id = patient_id
            self._filter_session_ids = self._load_patient_session_ids(patient_id)
            self._vm.set_active_patient(patient_id)

        self._update_filter_label()
        self._rebuild_sessions()
        # Switch to Sessions tab so the user immediately sees the filtered list.
        self._notebook.select(self._tab_sessions)

    def _on_new_session(self) -> None:
        self._vm.new_session()
        self._sessions_listbox.selection_clear(0, tk.END)

    def _on_save_patient(self) -> None:
        """Validate the inline form and delegate to the ViewModel."""
        full_name = self._ent_full_name.get().strip()
        if not full_name:
            # Highlight the empty field — no messagebox to keep it lightweight.
            self._ent_full_name.focus_set()
            return

        dob = self._ent_dob.get().strip()
        self._vm.save_new_patient(full_name, dob)

        # Clear form fields after a successful save.
        self._ent_full_name.delete(0, tk.END)
        self._ent_dob.delete(0, tk.END)
