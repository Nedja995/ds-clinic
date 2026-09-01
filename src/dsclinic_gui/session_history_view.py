"""
Session history sidebar view.

Owns: the leftmost sidebar pane — a list of past sessions with patient name
and date, a "New Session" button, and selection-driven session loading.

Does NOT own: session persistence, DB access, or any analysis logic — those
belong exclusively to DSClinicViewModel. This View only calls
view_model.load_session() and view_model.new_session().
"""
from __future__ import annotations

from typing import Any

import tkinter as tk
from tkinter import ttk

from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.styles import (
    ACCENT, ACCENT_LT, ACCENT_DK, BG, BORDER, FOOTER_BG,
    PANEL, SUBTLE, TEXT, WHITE,
    F_UI, FB, FH, FI, FS, FSB,
)
from npy.core.logger import setup_logger

logger = setup_logger()

# Column key produced by JsonCollection for the dot-path "report.content.patient_name"
_KEY_PATIENT = "report_content_patient_name"
# Column key for "report.report_date"
_KEY_DATE    = "report_report_date"
# Primary key
_KEY_ID      = "session_id"


class SessionHistoryView(ttk.Frame):
    """
    Sidebar panel listing saved sessions.

    Subscribes to view_model.on_sessions_changed to rebuild the list whenever
    a new session is persisted. Clicking a row calls view_model.load_session();
    the "New Session" button calls view_model.new_session().

    Layout invariant: this widget is always the leftmost pane in MainContainerView.
    """

    def __init__(
        self,
        parent: tk.Misc,
        view_model: DSClinicViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self._vm = view_model
        self._setup_ui()
        self._vm.on_sessions_changed.subscribe(self._rebuild_list)
        # Populate immediately from whatever is already on disk.
        self._rebuild_list()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.configure(style="SidebarPanel.TFrame")

        # ── Header strip ──────────────────────────────────────────────────
        header = ttk.Frame(self, style="SidebarStrip.TFrame", height=30)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        ttk.Label(
            header,
            text="SESSIONS",
            style="SidebarTitle.TLabel",
            anchor="center",
        ).pack(fill="both", expand=True)

        # ── New Session button ─────────────────────────────────────────────
        ttk.Button(
            self,
            text="+ New Session",
            style="Accent.TButton",
            command=self._on_new_session,
        ).pack(fill="x", padx=4, pady=(4, 2))

        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=(2, 0))

        # ── Scrollable session list ────────────────────────────────────────
        list_wrap = ttk.Frame(self, style="SidebarPanel.TFrame")
        list_wrap.pack(fill="both", expand=True)

        # tk.Listbox: no ttk equivalent with per-item styling — kept intentionally.
        self._scrollbar = ttk.Scrollbar(list_wrap, orient="vertical")
        self._listbox = tk.Listbox(
            list_wrap,
            yscrollcommand=self._scrollbar.set,
            selectmode=tk.SINGLE,
            bg=PANEL,
            fg=TEXT,
            font=FS,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activestyle="none",
            selectbackground=ACCENT,
            selectforeground=WHITE,
            cursor="hand2",
        )
        self._scrollbar.config(command=self._listbox.yview)
        self._scrollbar.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_item_selected)

        # ── Empty-state label (shown when list is empty) ───────────────────
        self._lbl_empty = ttk.Label(
            list_wrap,
            text="No sessions yet.\nRun an analysis to\ncreate the first one.",
            style="SidebarEmpty.TLabel",
            anchor="center",
            justify="center",
        )

        # Parallel list mapping listbox index → session_id string.
        # Kept in sync with every _rebuild_list() call.
        self._session_ids: list[str] = []

    # ── List management ───────────────────────────────────────────────────────

    def _rebuild_list(self) -> None:
        """Repopulate the listbox from view_model.var_sessions_index."""
        self._listbox.delete(0, tk.END)
        self._session_ids.clear()

        entries = self._vm.var_sessions_index

        if not entries:
            self._lbl_empty.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            return

        self._lbl_empty.place_forget()

        for entry in entries:
            session_id = str(entry.get(_KEY_ID, ""))
            patient    = str(entry.get(_KEY_PATIENT, "") or "Unknown patient")
            date       = str(entry.get(_KEY_DATE,    "") or "")
            label      = f"{patient}\n{date}" if date else patient

            self._listbox.insert(tk.END, label)
            self._session_ids.append(session_id)

        logger.debug("SessionHistoryView: rebuilt list with %d entries.", len(entries))

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_item_selected(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        """Load the session the user clicked."""
        selection = self._listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self._session_ids):
            return
        session_id = self._session_ids[index]
        logger.debug("SessionHistoryView: user selected session %r.", session_id)
        self._vm.load_session(session_id)

    def _on_new_session(self) -> None:
        self._vm.new_session()
        # Deselect any highlighted row so the sidebar reflects the fresh state.
        self._listbox.selection_clear(0, tk.END)
