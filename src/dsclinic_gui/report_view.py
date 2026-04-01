"""
report_view.py  –  DS Clinic Analiza · View (MVC)
==================================================
Koristi ttk widgete svuda gde je to moguće.
Jedini izuzeci su:
  - tk.Canvas          – nema ttk ekvivalenta
  - scrolledtext.ScrolledText  – interni tk.Text, ne podržava ttk.Style
  - tk.StringVar / tk.IntVar   – uvek tk
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

from npy.core.logger import setup_logger
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel

from dsclinic_gui.styles import *
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.chat_session_view import ChatSessionView

logger = setup_logger()




# ─────────────────────────────────────────────────────────────────────────────

class MedicalReportView(ttk.Frame):
    """
    View for displaying and editing medical reports.
    """
    def __init__(self, parent: ttk.Misc, view_model: DSClinicViewModel, **kwargs: any) -> None:
        super().__init__(parent, **kwargs)
        self.view_model = view_model

        self.critical_finding_widgets: list[dict] = [] # Tracks widgets for rows
        self._row_parity = 0

        self._setup_ui()
        
        # Event Binding (MVVM)
        self.master.bind("<<VM_DataChanged>>", lambda e: self.update_view_from_viewmodel())
        
        self.view_model.var_status_title.trace_add("write", lambda *args: self.update_view_from_viewmodel())
        self.view_model.var_is_analyzing.trace_add("write", lambda *args: self.update_view_from_viewmodel())
        # Initial Population
        self.update_view_from_viewmodel()
        
        
    # ─────────────────────────────────────────────────────────────────────────
    # Layout
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        logger.debug("Setting up UI...")
        self._build_toolbar(self)
        self._build_footer(self)   # pack bottom first so canvas fills the gap
        self._build_canvas(self)
        self._build_form()

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self, parent: tk.Widget):
        self.top_frame = ttk.Frame(parent, style="Toolbar.TFrame", padding=(0, 6))
        self.top_frame.pack(side="top", fill="x")

        # Bind directly to VM commands and properties
        self.btn_analyze = self._tooolbar_button(self.top_frame, textvariable=self.view_model.var_btn_analyze_text)
        self.btn_analyze.config(command=self.view_model.toggle_analysis)

        self.btn_submit = self._tooolbar_button(self.top_frame, text="Export")
        self.btn_submit.config(command=self._handle_export_click)

        self.btn_full_report = self._tooolbar_button(self.top_frame, text="Details", state="disabled")
        self.btn_settings    = self._tooolbar_button(self.top_frame, text="Settings", side="right")

        ttk.Frame(parent, style="Shadow.TFrame", height=2).pack(side="top", fill="x")

    def _tooolbar_button(self, parent, text="", textvariable=None,state="normal", side="left") -> ttk.Button:
        kw: dict = dict(style="Toolbar.TButton", state=state)
        btn = (ttk.Button(parent, textvariable=textvariable, **kw) if textvariable else ttk.Button(parent, text=text, **kw))
        btn.pack(side=side, padx=(6, 0) if side == "left" else (0, 6))
        return btn

    # ── Footer ────────────────────────────────────────────────────────────────

    def _build_footer(self, parent: tk.Widget):
        self.footer_frame = ttk.Frame(parent, style="Footer.TFrame")
        self.footer_frame.pack(side="bottom", fill="x")

        # Fixed-height host keeps progressbar slimmer than its natural size
        pb_host = ttk.Frame(self.footer_frame, style="PBHost.TFrame", height=6)
        pb_host.pack(fill="x", side="top")
        pb_host.pack_propagate(False)

        self.progress_bar = ttk.Progressbar(pb_host, mode="determinate", variable=self.view_model.var_progress_value)
        self.progress_bar.pack(fill="x", expand=True)

        ttk.Separator(self.footer_frame, orient="horizontal").pack(fill="x", side="top")

        status_row = ttk.Frame(self.footer_frame, style="Footer.TFrame", padding=(8, 3))
        status_row.pack(fill="x")

        self.lbl_footer_status = ttk.Label(status_row, textvariable=self.view_model.var_status_title, style="StatusKey.TLabel")
        self.lbl_footer_status.pack(side="left")

        self.lbl_status_details = ttk.Label(status_row, textvariable=self.view_model.var_status_detail, style="StatusVal.TLabel", anchor="w")
        self.lbl_status_details.pack(side="left", fill="x", expand=True, padx=(5, 0))

    # ── Scrollable canvas ─────────────────────────────────────────────────────

    def _build_canvas(self, parent: tk.Widget):
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True)

        # tk.Canvas: no ttk equivalent, kept intentionally
        self.main_canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        self.scrollbar   = ttk.Scrollbar(wrap, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all"))
        )

        self._win_id = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfigure(
                self._win_id, width=e.width)
        )

        def _wheel(ev):
            delta = (int(-1 * ev.delta / 120) if ev.delta else (-1 if ev.num == 4 else 1))
            self.main_canvas.yview_scroll(delta, "units")

        self.main_canvas.bind_all("<MouseWheel>", _wheel)
        self.main_canvas.bind_all("<Button-4>",   _wheel)
        self.main_canvas.bind_all("<Button-5>",   _wheel)

        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    # ── Form ──────────────────────────────────────────────────────────────────

    def _build_form(self):
        sf  = self.scrollable_frame
        PAD = dict(padx=4, pady=8)

        # Card: Pacijent
        patient_card = self._card(sf, "Podaci o pacijentu")
        patient_card.pack(fill="x", **PAD)

        pr = ttk.Frame(patient_card, style="Panel.TFrame", padding=(12, 0, 12, 2))
        pr.pack(fill="x")

        ttk.Label(pr, text="Ime pacijenta:", style="FormLabel.TLabel").pack(side="left")
        self.ent_ime = ttk.Entry(pr, width=26, font=FI, textvariable=self.view_model.var_patient_name)
        self.ent_ime.pack(side="left", padx=(6, 28), ipady=2, pady=4)

        ttk.Label(pr, text="Datum:", style="FormLabel.TLabel").pack(side="left")
        self.ent_datum = ttk.Entry(pr, width=14, font=FI, textvariable=self.view_model.var_report_date)
        self.ent_datum.pack(side="left", padx=(6, 0), ipady=2, pady=4)

        # Card: Terapija
        therapy_card = self._card(sf, "Preporučena terapija i savet")
        therapy_card.pack(fill="x", **PAD)

        self.txt_terapija = self._scrolled_text(therapy_card, height=9)
        self.txt_terapija.pack(fill="x", padx=0, pady=(0, 0))

        # Card: Nalazi
        nalazi_card = self._card(sf, "Nalazi")
        nalazi_card.pack(fill="x", **PAD)

        th = ttk.Frame(nalazi_card, style="THead.TFrame", height=26)
        th.pack(fill="x", padx=0, pady=(0, 2))
        th.pack_propagate(False)
        ttk.Label(th, text="Mišljenje / Objašnjenje", style="THeadLabel.TLabel").place(relx=0.0, rely=0, relwidth=0.595, relheight=1.0)
        ttk.Label(th, text="Parametar i vrednost", style="THeadLabel.TLabel").place(relx=0.61, rely=0, relwidth=0.37, relheight=1.0)

        self.nalazi_container = ttk.Frame(nalazi_card, style="Rows.TFrame")
        self.nalazi_container.pack(fill="x", padx=0)

        self.btn_dodaj_nalaz = ttk.Button(
            nalazi_card, text="＋   Dodaj novi nalaz",
            style="Accent.TButton",
            command=lambda: [self.update_viewmodel_from_view(), self.view_model.add_finding(), self.update_view_from_viewmodel()]
        )
        self.btn_dodaj_nalaz.pack(fill="x", padx=2, pady=(4, 4))

        ttk.Frame(sf, height=24).pack()

    # ─────────────────────────────────────────────────────────────────────────
    # Widget factories
    # ─────────────────────────────────────────────────────────────────────────

    def _card(self, parent, title: str) -> ttk.Frame:
        outer = ttk.Frame(parent, style="Card.TFrame")
        strip = ttk.Frame(outer, style="Strip.TFrame", height=30)
        strip.pack(fill="x")
        strip.pack_propagate(False)
        ttk.Label(strip, text=title.upper(), style="CardTitle.TLabel").pack(fill="both", expand=True)
        return outer

    def _scrolled_text(self, parent, height=5, bg=PANEL) -> scrolledtext.ScrolledText:
        """
        scrolledtext.ScrolledText wraps tk.Text — ttk.Style cannot theme
        tk.Text internals, so widget-level options are correct here.
        """
        t = scrolledtext.ScrolledText(
            parent, font=FI, bg=bg, fg=TEXT,
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            wrap="word", undo=True, height=height,
            insertbackground=ACCENT,
            selectbackground=ACCENT, selectforeground=WHITE,
            padx=6, pady=4
        )
        t.bind("<FocusIn>",  lambda _: t.config(highlightbackground=ACCENT))
        t.bind("<FocusOut>", lambda _: t.config(highlightbackground=BORDER))
        return t

    # ─────────────────────────────────────────────────────────────────────────
    # Nalazi rows
    # ─────────────────────────────────────────────────────────────────────────

    def _render_finding_row(self, index: int, finding: MedicalCriticalFindingModel):
        """Renders a single row based on VM data."""
        logger.debug(f"Rendering finding row {index}: {finding.parametar_and_value}")
        self._row_parity += 1
        
        row_style = "RowA.TFrame" if self._row_parity % 2 else "RowB.TFrame"
        row_bg    = ROW_A         if self._row_parity % 2 else ROW_B

        row_frame = ttk.Frame(self.nalazi_container, style=row_style, height=72)
        row_frame.pack(fill="x", pady=(0, 0))
        row_frame.pack_propagate(False)

        ent_m = self._scrolled_text(row_frame, height=1, bg=row_bg)
        ent_m.insert("1.0", finding.expertsko_misljenje)
        ent_m.place(relx=0.0, rely=0.06, relwidth=0.595, relheight=0.88)

        ent_p = self._scrolled_text(row_frame, height=1, bg=row_bg)
        ent_p.insert("1.0", finding.parametar_and_value)
        ent_p.place(relx=0.610, rely=0.06, relwidth=0.295, relheight=0.88)

        btn_ukloni = ttk.Button(
            row_frame, text="✕", style="Danger.TButton",
            command=lambda i=index: [self.update_viewmodel_from_view(), self.view_model.remove_finding(i), self.update_view_from_viewmodel()]
        )
        btn_ukloni.place(relx=0.918, rely=0.15, relwidth=0.074, relheight=0.70)

        self.critical_finding_widgets.append({
            "frame":      row_frame,
            "parametar":  ent_p,
            "misljenje":  ent_m,
        })

    # ─────────────────────────────────────────────────────────────────────────
    # MVVM Bindings
    # ─────────────────────────────────────────────────────────────────────────

    def _handle_export_click(self):
        # 1. Sync Text widgets -> VM
        self.update_viewmodel_from_view()
        # 2. Call VM Export
        self.view_model.save_report()

    def update_viewmodel_from_view(self):
        """Extracts data from complex widgets (ScrolledText) and updates the VM."""
        logger.debug("Updating ViewModel from View...")
        # Therapy Text
        self.view_model.therapy_text_content = self.txt_terapija.get("1.0", tk.END).strip()
        
        # Findings List
        for i, widgets in enumerate(self.critical_finding_widgets):
            if i < len(self.view_model.findings):
                self.view_model.findings[i].expertsko_misljenje = widgets["misljenje"].get("1.0", tk.END).strip()
                self.view_model.findings[i].parametar_and_value = widgets["parametar"].get("1.0", tk.END).strip()

    def update_view_from_viewmodel(self):
        """Updates complex widgets based on current VM state."""
        
        logger.debug("Updating View from ViewModel...")
        # Therapy Text
        self.txt_terapija.delete("1.0", tk.END)
        self.txt_terapija.insert("1.0", self.view_model.therapy_text_content)
        
        # Findings Rows (Rebuild completely)
        # Cleanup old
        for w in self.critical_finding_widgets:
            w["frame"].destroy()
        self.critical_finding_widgets.clear()
        
        # Rebuild
        for i, finding in enumerate(self.view_model.findings):
            self._render_finding_row(i, finding)