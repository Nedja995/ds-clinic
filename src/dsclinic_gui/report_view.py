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
from typing import TYPE_CHECKING

from npy.core.logger import setup_logger
from models import MedicalReport, MedicalReportModel, MedicalCriticalFindingModel

if TYPE_CHECKING:
    from dsclinic_gui.report_view_models import DSClinicViewModel

logger = setup_logger()


# ── Palette ───────────────────────────────────────────────────────────────────
BG        = "#F0F4F8"
PANEL     = "#FFFFFF"
TOOLBAR   = "#1E2D3D"
TB_BTN    = "#2A3F55"
TB_HOV    = "#3A5570"
TB_DIS    = "#1A2B38"
TB_DIS_FG = "#4A6070"
ACCENT    = "#1A6FA8"
ACCENT_DK = "#145A8A"
ACCENT_LT = "#E8F1F8"
BORDER    = "#C8D8E8"
TEXT      = "#1C2B3A"
SUBTLE    = "#6B7D8E"
DANGER    = "#C62828"
DANGER_LT = "#FDECEA"
FOOTER_BG = "#E8EEF4"
THEAD_BG  = "#DCE8F0"
ROW_A     = "#F5F8FB"
ROW_B     = "#FFFFFF"
WHITE     = "#FFFFFF"
SHADOW    = "#0D1B2A"
PB_TRACK  = "#C8D8E8"

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_UI = "Segoe UI"
FL   = (F_UI, 10, "bold")
FI   = (F_UI, 10)
FB   = (F_UI, 9,  "bold")
FH   = (F_UI, 8,  "bold")
FS   = (F_UI, 9)
FSB  = (F_UI, 9,  "bold")


# ─────────────────────────────────────────────────────────────────────────────

class ChatSessionView(ttk.Frame):
    def __init__(self, parent, view: 'DSClinicView', vm: 'DSClinicViewModel', **kwargs):
        super().__init__(parent, **kwargs)
        self.view = view
        self.vm = vm
        self.configure(style="Panel.TFrame", padding=10)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        # Proportions: 30%, 40%, 15% -> ~6, 8, 3
        self.rowconfigure(1, weight=6)
        self.rowconfigure(3, weight=8)
        self.rowconfigure(4, weight=3)

        # --- Initial Question ---
        ttk.Label(self, text="Inicijalno pitanje:", style="FormLabel.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.txt_initial_question = self.view._scrolled_text(self, height=1)
        self.txt_initial_question.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # --- Response ---
        ttk.Label(self, text="Odgovor:", style="FormLabel.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.txt_response = self.view._scrolled_text(self, height=1)
        self.txt_response.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        # --- Follow-up Question ---
        follow_up_frame = ttk.Frame(self, style="Panel.TFrame")
        follow_up_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        follow_up_frame.columnconfigure(1, weight=1)
        follow_up_frame.rowconfigure(0, weight=1)

        ttk.Label(
            follow_up_frame, text="Pitanje:", style="FormLabel.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.txt_follow_up = self.view._scrolled_text(follow_up_frame, height=1)
        self.txt_follow_up.grid(row=0, column=1, sticky="nsew")

        ask_button = ttk.Button(
            follow_up_frame, text="Ask", style="Accent.TButton",
            # command=... # TODO: Add command
        )
        ask_button.grid(row=0, column=2, sticky="e", padx=(6, 0))


# ─────────────────────────────────────────────────────────────────────────────

class DSClinicView:
    def __init__(self, root: tk.Tk, viewModel: DSClinicViewModel):
        self.root = root
        self.vm = viewModel
        self.root.title("DS Clinic Analiza")
        self.root.minsize(640, 520)

        w, h = 1480, 820
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

        self.finding_widgets: list[dict] = [] # Tracks widgets for rows
        self._row_parity = 0

        self._build_styles()
        self._setup_ui()
        
        # Event Binding (MVVM)
        self.root.bind("<<VM_DataChanged>>", lambda e: self.refresh_view_from_vm())
        
        # Initial Population
        self.refresh_view_from_vm()

    # ─────────────────────────────────────────────────────────────────────────
    # ttk.Style  (single source of truth for all colors / fonts)
    # ─────────────────────────────────────────────────────────────────────────

    def _build_styles(self):
        s = ttk.Style()
        # 'clam' honours background/foreground overrides cross-platform
        s.theme_use("clam")

        # ── Generic ──────────────────────────────────────────────────────
        s.configure(".",        background=BG, font=FI)
        s.configure("TFrame",   background=BG)
        s.configure("TLabel",   background=BG, foreground=TEXT, font=FI)

        # ── Named frames ─────────────────────────────────────────────────
        s.configure("Toolbar.TFrame",  background=TOOLBAR)
        s.configure("Shadow.TFrame",   background=SHADOW)
        s.configure("Panel.TFrame",    background=PANEL)
        s.configure("Footer.TFrame",   background=FOOTER_BG)
        s.configure("PBHost.TFrame",   background=PB_TRACK)
        s.configure("Card.TFrame",     background=PANEL)
        s.configure("Strip.TFrame",    background=ACCENT)
        s.configure("THead.TFrame",    background=THEAD_BG)
        s.configure("RowA.TFrame",     background=ROW_A)
        s.configure("RowB.TFrame",     background=ROW_B)
        s.configure("Rows.TFrame",     background=BG)

        # ── Labels ───────────────────────────────────────────────────────
        s.configure("CardTitle.TLabel",
                    background=ACCENT, foreground=WHITE,
                    font=FL, padding=(12, 0))
        s.configure("FormLabel.TLabel",
                    background=PANEL, foreground=TEXT, font=FL)
        s.configure("THeadLabel.TLabel",
                    background=THEAD_BG, foreground=SUBTLE,
                    font=FH, anchor="w", padding=(6, 0))
        s.configure("StatusKey.TLabel",
                    background=FOOTER_BG, foreground=DANGER, font=FSB)
        s.configure("StatusVal.TLabel",
                    background=FOOTER_BG, foreground=TEXT, font=FS)

        # ── Toolbar buttons ───────────────────────────────────────────────
        s.configure("Toolbar.TButton",
                    background=TB_BTN, foreground=WHITE,
                    font=FB, relief="flat", borderwidth=0,
                    padding=(14, 5), focusthickness=0)
        s.map("Toolbar.TButton",
              background=[("disabled", TB_DIS),    ("active", TB_HOV)],
              foreground=[("disabled", TB_DIS_FG),  ("active", WHITE)])

        # ── Accent button (+ Dodaj nalaz) ─────────────────────────────────
        s.configure("Accent.TButton",
                    background=ACCENT, foreground=WHITE,
                    font=FB, relief="flat", borderwidth=0,
                    padding=(0, 8), focusthickness=0)
        s.map("Accent.TButton",
              background=[("active", ACCENT_DK)],
              foreground=[("active", WHITE)])

        # ── Danger button (✕ remove row) ──────────────────────────────────
        s.configure("Danger.TButton",
                    background=DANGER_LT, foreground=DANGER,
                    font=(F_UI, 10, "bold"), relief="flat", borderwidth=0,
                    padding=(0, 0), focusthickness=0)
        s.map("Danger.TButton",
              background=[("active", DANGER)],
              foreground=[("active", WHITE)])

        # ── Entry ─────────────────────────────────────────────────────────
        s.configure("TEntry",
                    fieldbackground=PANEL, foreground=TEXT,
                    bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                    selectbackground=ACCENT, selectforeground=WHITE,
                    padding=(4, 3))
        s.map("TEntry",
              bordercolor=[("focus", ACCENT)],
              lightcolor=[("focus", ACCENT)],
              darkcolor=[("focus", ACCENT)])

        # ── Scrollbar ─────────────────────────────────────────────────────
        s.configure("TScrollbar",
                    background=BORDER, troughcolor=BG,
                    bordercolor=BG, arrowcolor=SUBTLE,
                    relief="flat", borderwidth=0)
        s.map("TScrollbar",
              background=[("active", ACCENT)])

        # ── Progressbar ───────────────────────────────────────────────────
        s.configure("TProgressbar",
                    troughcolor=PB_TRACK, background=ACCENT,
                    borderwidth=0, relief="flat")

        # ── Separator ─────────────────────────────────────────────────────
        s.configure("TSeparator", background=BORDER)

    # ─────────────────────────────────────────────────────────────────────────
    # Layout
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_ui(self):
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # --- Left Pane (Report View) ---
        left_pane = ttk.Frame(self.paned_window, style="TFrame")
        self.paned_window.add(left_pane, weight=3)

        self._build_toolbar(left_pane)
        self._build_footer(left_pane)   # pack bottom first so canvas fills the gap
        self._build_canvas(left_pane)
        self._build_form()

        # --- Right Pane (Chat View) ---
        right_pane = ChatSessionView(self.paned_window, self, self.vm)
        self.paned_window.add(right_pane, weight=2)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self, parent: tk.Widget):
        self.top_frame = ttk.Frame(parent, style="Toolbar.TFrame", padding=(0, 6))
        self.top_frame.pack(side="top", fill="x")

        # Bind directly to VM commands and properties
        self.btn_analyze = self._tb_btn(self.top_frame, textvariable=self.vm.btn_analyze_text)
        self.btn_analyze.config(command=self.vm.toggle_analysis)

        self.btn_submit = self._tb_btn(self.top_frame, text="Export")
        self.btn_submit.config(command=self._handle_export_click)

        self.btn_full_report = self._tb_btn(self.top_frame, text="Details", state="disabled")
        self.btn_settings    = self._tb_btn(self.top_frame, text="Settings", side="right")

        ttk.Frame(parent, style="Shadow.TFrame", height=2).pack(side="top", fill="x")

    def _tb_btn(self, parent, text="", textvariable=None,state="normal", side="left") -> ttk.Button:
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

        self.progress_bar = ttk.Progressbar(pb_host, mode="determinate", variable=self.vm.progress_value)
        self.progress_bar.pack(fill="x", expand=True)

        ttk.Separator(self.footer_frame, orient="horizontal").pack(fill="x", side="top")

        status_row = ttk.Frame(self.footer_frame, style="Footer.TFrame", padding=(8, 3))
        status_row.pack(fill="x")

        self.lbl_footer_status = ttk.Label(status_row, textvariable=self.vm.status_title, style="StatusKey.TLabel")
        self.lbl_footer_status.pack(side="left")

        self.lbl_status_details = ttk.Label(status_row, textvariable=self.vm.status_detail, style="StatusVal.TLabel", anchor="w")
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
        PAD = dict(padx=16, pady=8)

        # Card: Pacijent
        patient_card = self._card(sf, "Podaci o pacijentu")
        patient_card.pack(fill="x", **PAD)

        pr = ttk.Frame(patient_card, style="Panel.TFrame", padding=(12, 0, 12, 2))
        pr.pack(fill="x")

        ttk.Label(pr, text="Ime pacijenta:", style="FormLabel.TLabel").pack(side="left")
        self.ent_ime = ttk.Entry(pr, width=36, font=FI, textvariable=self.vm.patient_name)
        self.ent_ime.pack(side="left", padx=(6, 28), ipady=2, pady=4)

        ttk.Label(pr, text="Datum:", style="FormLabel.TLabel").pack(side="left")
        self.ent_datum = ttk.Entry(pr, width=14, font=FI, textvariable=self.vm.report_date)
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
            command=lambda: [self.sync_view_to_vm(), self.vm.add_finding()]
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
            padx=6, pady=4,
        )
        t.bind("<FocusIn>",  lambda _: t.config(highlightbackground=ACCENT))
        t.bind("<FocusOut>", lambda _: t.config(highlightbackground=BORDER))
        return t

    # ─────────────────────────────────────────────────────────────────────────
    # Nalazi rows
    # ─────────────────────────────────────────────────────────────────────────

    def _render_finding_row(self, index: int, finding: MedicalCriticalFindingModel):
        """Renders a single row based on VM data."""
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
            command=lambda i=index: [self.sync_view_to_vm(), self.vm.remove_finding(i)]
        )
        btn_ukloni.place(relx=0.918, rely=0.15, relwidth=0.074, relheight=0.70)

        self.finding_widgets.append({
            "frame":      row_frame,
            "parametar":  ent_p,
            "misljenje":  ent_m,
        })

    # ─────────────────────────────────────────────────────────────────────────
    # MVVM Bindings
    # ─────────────────────────────────────────────────────────────────────────

    def _handle_export_click(self):
        # 1. Sync Text widgets -> VM
        self.sync_view_to_vm()
        # 2. Call VM Export
        self.vm.save_report()

    def sync_view_to_vm(self):
        """Extracts data from complex widgets (ScrolledText) and updates the VM."""
        # Therapy Text
        self.vm.therapy_text_content = self.txt_terapija.get("1.0", tk.END).strip()
        
        # Findings List
        for i, widgets in enumerate(self.finding_widgets):
            if i < len(self.vm.findings):
                self.vm.findings[i].expertsko_misljenje = widgets["misljenje"].get("1.0", tk.END).strip()
                self.vm.findings[i].parametar_and_value = widgets["parametar"].get("1.0", tk.END).strip()

    def refresh_view_from_vm(self):
        """Updates complex widgets based on current VM state."""
        # Therapy Text
        self.txt_terapija.delete("1.0", tk.END)
        self.txt_terapija.insert("1.0", self.vm.therapy_text_content)
        
        # Findings Rows (Rebuild completely)
        # Cleanup old
        for w in self.finding_widgets:
            w["frame"].destroy()
        self.finding_widgets.clear()
        
        # Rebuild
        for i, finding in enumerate(self.vm.findings):
            self._render_finding_row(i, finding)