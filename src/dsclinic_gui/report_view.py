import tkinter as tk
from tkinter import ttk, scrolledtext
from logger import setup_logger
from models import MedicalReportModel, MedicalCriticalFindingModel
 
logger = setup_logger()
 
# ── Palette ──────────────────────────────────────────────────────────────────
BG        = "#F0F4F8"
PANEL     = "#FFFFFF"
TOOLBAR   = "#1E2D3D"
TB_BTN    = "#2A3F55"
TB_HOV    = "#3A5570"
TB_DIS    = "#1A2B38"
ACCENT    = "#1A6FA8"
ACCENT_DK = "#145A8A"
BORDER    = "#C8D8E8"
TEXT      = "#1C2B3A"
SUBTLE    = "#6B7D8E"
SUCCESS   = "#2E7D32"
DANGER    = "#C62828"
FOOTER_BG = "#E8EEF4"
THEAD_BG  = "#DCE8F0"
ROW_A     = "#F5F8FB"
ROW_B     = "#FFFFFF"
WHITE     = "#FFFFFF"
ACCENT_LT = "#E8F1F8"
 
FL  = ("Segoe UI", 10, "bold")   # form label
FI  = ("Segoe UI", 10)           # input text
FB  = ("Segoe UI", 9,  "bold")   # button
FH  = ("Segoe UI", 8,  "bold")   # table header
FS  = ("Segoe UI", 9)            # status
FSB = ("Segoe UI", 9,  "bold")   # status bold
 
 
class DSClinicView:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("DS Clinic Analiza")
        self.root.minsize(640, 520)
        self.root.configure(bg=BG)
 
        w, h = 980, 820
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
 
        self.nalazi_rows: list[dict] = []
        self._row_parity = 0  # alternating row colors
 
        self._setup_ui()
 
    # ─────────────────────────────────────────────────────────────────────────
    # Layout assembly
    # ─────────────────────────────────────────────────────────────────────────
 
    def _setup_ui(self):
        self._build_toolbar()   # top
        self._build_footer()    # bottom (pack before canvas → canvas fills gap)
        self._build_canvas()    # center scrollable area
        self._build_form()      # content inside canvas
 
    # ── Toolbar ───────────────────────────────────────────────────────────────
 
    def _build_toolbar(self):
        self.top_frame = tk.Frame(self.root, bg=TOOLBAR, pady=6)
        self.top_frame.pack(side="top", fill="x")
 
        self.var_btn_analyze = tk.StringVar(value="Analyze")
        self.btn_analyze = self._tb_button(
            self.top_frame, textvariable=self.var_btn_analyze
        )
        self.btn_submit      = self._tb_button(self.top_frame, text="Export")
        self.btn_full_report = self._tb_button(self.top_frame, text="Details",
                                               state="disabled")
        self.btn_settings    = self._tb_button(self.top_frame, text="Settings",
                                               side="right")
 
        # bottom shadow line under toolbar
        tk.Frame(self.root, bg="#0D1B2A", height=2).pack(side="top", fill="x")
 
    def _tb_button(self, parent, text="", textvariable=None,
                   state="normal", side="left") -> tk.Button:
        is_dis = state == "disabled"
        kw = dict(
            master=parent, font=FB,
            bg=TB_DIS if is_dis else TB_BTN,
            fg="#4A6070" if is_dis else WHITE,
            activebackground=TB_HOV, activeforeground=WHITE,
            disabledforeground="#4A6070",
            relief="flat", bd=0,
            padx=14, pady=5,
            cursor="arrow" if is_dis else "hand2",
            state=state,
        )
        btn = tk.Button(**kw, textvariable=textvariable) if textvariable \
              else tk.Button(**kw, text=text)
        btn.pack(side=side, padx=(6, 0) if side == "left" else (0, 6))
 
        if not is_dis:
            btn.bind("<Enter>", lambda _: btn.config(bg=TB_HOV))
            btn.bind("<Leave>", lambda _: btn.config(bg=TB_BTN))
        return btn
 
    # ── Footer ────────────────────────────────────────────────────────────────
 
    def _build_footer(self):
        self.footer_frame = tk.Frame(self.root, bg=FOOTER_BG)
        self.footer_frame.pack(side="bottom", fill="x")
 
        # ── Progress bar — fixed-height host frame ─────────────────────────
        pb_host = tk.Frame(self.footer_frame, bg="#C8D8E8", height=6)
        pb_host.pack(fill="x", side="top")
        pb_host.pack_propagate(False)  # prevents frame from resizing to fit bar
 
        self.progress_bar = ttk.Progressbar(pb_host, mode="determinate")
        self.progress_bar.pack(fill="x", expand=True)
 
        # Thin separator line above text row
        tk.Frame(self.footer_frame, bg=BORDER, height=1).pack(fill="x")
 
        # ── Status text row ────────────────────────────────────────────────
        status_row = tk.Frame(self.footer_frame, bg=FOOTER_BG, pady=4)
        status_row.pack(fill="x", padx=8)
 
        self.lbl_footer_status = tk.Label(
            status_row, text="STATUS:", font=FSB,
            bg=FOOTER_BG, fg=DANGER
        )
        self.lbl_footer_status.pack(side="left")
 
        self.var_status = tk.StringVar(value="Idle")
        self.lbl_status_details = tk.Label(
            status_row, textvariable=self.var_status,
            font=FS, bg=FOOTER_BG, fg=TEXT, anchor="w"
        )
        self.lbl_status_details.pack(side="left", fill="x", expand=True,
                                     padx=(5, 0))
 
    # ── Scrollable canvas ─────────────────────────────────────────────────────
 
    def _build_canvas(self):
        wrap = tk.Frame(self.root, bg=BG)
        wrap.pack(fill="both", expand=True)
 
        self.main_canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        self.scrollbar   = ttk.Scrollbar(wrap, orient="vertical",
                                         command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg=BG)
 
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )
 
        self._win_id = self.main_canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
 
        # Keep inner frame width in sync with canvas
        self.main_canvas.bind(
            "<Configure>",
            lambda e: self.main_canvas.itemconfigure(self._win_id, width=e.width)
        )
 
        # Mouse-wheel scroll (Windows + Linux)
        def _wheel(ev):
            delta = (
                int(-1 * (ev.delta / 120)) if ev.delta
                else (-1 if ev.num == 4 else 1)
            )
            self.main_canvas.yview_scroll(delta, "units")
 
        self.main_canvas.bind_all("<MouseWheel>", _wheel)
        self.main_canvas.bind_all("<Button-4>",   _wheel)
        self.main_canvas.bind_all("<Button-5>",   _wheel)
 
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
 
    # ── Form content ──────────────────────────────────────────────────────────
 
    def _build_form(self):
        sf  = self.scrollable_frame
        PAD = dict(padx=16, pady=8)
 
        # ── Card: Pacijent ────────────────────────────────────────────────
        patient_card = self._card(sf, "Podaci o pacijentu")
        patient_card.pack(fill="x", **PAD)
 
        pr = tk.Frame(patient_card, bg=PANEL)
        pr.pack(fill="x", padx=12, pady=(0, 12))
 
        tk.Label(pr, text="Ime pacijenta:", font=FL, bg=PANEL, fg=TEXT).pack(side="left")
        self.ent_ime = self._entry(pr, width=36)
        self.ent_ime.pack(side="left", padx=(6, 28), ipadx=4, ipady=3)
 
        tk.Label(pr, text="Datum:", font=FL, bg=PANEL, fg=TEXT).pack(side="left")
        self.ent_datum = self._entry(pr, width=14)
        self.ent_datum.pack(side="left", padx=(6, 0), ipadx=4, ipady=3)
 
        # ── Card: Terapija ────────────────────────────────────────────────
        therapy_card = self._card(sf, "Preporučena terapija i savet")
        therapy_card.pack(fill="x", **PAD)
 
        self.txt_terapija = self._scrolled_text(therapy_card, height=9)
        self.txt_terapija.pack(fill="x", padx=12, pady=(0, 12))
 
        # ── Card: Nalazi ──────────────────────────────────────────────────
        nalazi_card = self._card(sf, "Nalazi")
        nalazi_card.pack(fill="x", **PAD)
 
        # Table column header
        th = tk.Frame(nalazi_card, bg=THEAD_BG, height=26)
        th.pack(fill="x", padx=12, pady=(0, 1))
        th.pack_propagate(False)
        tk.Label(th, text="Mišljenje / Objašnjenje", font=FH,
                 bg=THEAD_BG, fg=SUBTLE, anchor="w", padx=6).place(
            relx=0.0, rely=0, relwidth=0.595, relheight=1.0)
        tk.Label(th, text="Parametar i vrednost", font=FH,
                 bg=THEAD_BG, fg=SUBTLE, anchor="w", padx=6).place(
            relx=0.61, rely=0, relwidth=0.37, relheight=1.0)
 
        self.nalazi_container = tk.Frame(nalazi_card, bg=BG)
        self.nalazi_container.pack(fill="x", padx=12)
 
        self.btn_dodaj_nalaz = tk.Button(
            nalazi_card, text="＋   Dodaj novi nalaz",
            font=FB, bg=ACCENT, fg=WHITE,
            activebackground=ACCENT_DK, activeforeground=WHITE,
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=lambda: self.add_finding_row()
        )
        self.btn_dodaj_nalaz.pack(fill="x", padx=12, pady=(4, 12))
        self.btn_dodaj_nalaz.bind("<Enter>", lambda _: self.btn_dodaj_nalaz.config(bg=ACCENT_DK))
        self.btn_dodaj_nalaz.bind("<Leave>", lambda _: self.btn_dodaj_nalaz.config(bg=ACCENT))
 
        # Bottom breathing room
        tk.Frame(sf, bg=BG, height=24).pack()
 
    # ─────────────────────────────────────────────────────────────────────────
    # Widget factories
    # ─────────────────────────────────────────────────────────────────────────
 
    def _card(self, parent, title: str) -> tk.Frame:
        """White card panel with an accent title strip."""
        outer = tk.Frame(parent, bg=PANEL,
                         highlightthickness=1, highlightbackground=BORDER)
        strip = tk.Frame(outer, bg=ACCENT, height=30)
        strip.pack(fill="x")
        strip.pack_propagate(False)
        tk.Label(strip, text=title.upper(), font=FL,
                 bg=ACCENT, fg=WHITE, anchor="w", padx=12).pack(
            fill="both", expand=True)
        return outer
 
    def _entry(self, parent, width=32) -> tk.Entry:
        e = tk.Entry(parent, font=FI, bg=PANEL, fg=TEXT, width=width,
                     relief="flat", bd=0,
                     highlightthickness=1, highlightbackground=BORDER,
                     highlightcolor=ACCENT, insertbackground=ACCENT)
        e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=ACCENT))
        e.bind("<FocusOut>", lambda _: e.config(highlightbackground=BORDER))
        return e
 
    def _scrolled_text(self, parent, height=5) -> scrolledtext.ScrolledText:
        t = scrolledtext.ScrolledText(
            parent, font=FI, bg=PANEL, fg=TEXT,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT,
            wrap="word", undo=True, height=height,
            insertbackground=ACCENT, padx=6, pady=4
        )
        t.bind("<FocusIn>",  lambda _: t.config(highlightbackground=ACCENT))
        t.bind("<FocusOut>", lambda _: t.config(highlightbackground=BORDER))
        return t
 
    # ─────────────────────────────────────────────────────────────────────────
    # Nalazi rows
    # ─────────────────────────────────────────────────────────────────────────
 
    def add_finding_row(self, misljenje: str = "", parametar: str = ""):
        self._row_parity += 1
        row_bg = ROW_A if self._row_parity % 2 == 1 else ROW_B
 
        row_frame = tk.Frame(self.nalazi_container, bg=row_bg, height=72)
        row_frame.pack(fill="x", pady=(0, 1))
        row_frame.pack_propagate(False)
 
        def st(master, value=""):
            widget = scrolledtext.ScrolledText(
                master, font=FI, bg=row_bg, fg=TEXT,
                relief="flat", bd=0,
                highlightthickness=1, highlightbackground=BORDER,
                highlightcolor=ACCENT,
                wrap="word", undo=True,
                insertbackground=ACCENT, padx=4, pady=2
            )
            widget.insert("1.0", value)
            widget.bind("<FocusIn>",  lambda _: widget.config(highlightbackground=ACCENT))
            widget.bind("<FocusOut>", lambda _: widget.config(highlightbackground=BORDER))
            return widget
 
        ent_m = st(row_frame, misljenje)
        ent_m.place(relx=0.0, rely=0.06, relwidth=0.595, relheight=0.88)
 
        ent_p = st(row_frame, parametar)
        ent_p.place(relx=0.610, rely=0.06, relwidth=0.295, relheight=0.88)
 
        btn_ukloni = tk.Button(
            row_frame, text="✕",
            font=("Segoe UI", 10, "bold"),
            bg="#FDECEA", fg=DANGER,
            activebackground=DANGER, activeforeground=WHITE,
            relief="flat", bd=0, cursor="hand2"
        )
        btn_ukloni.config(command=lambda rf=row_frame: self.remove_finding_row(rf))
        btn_ukloni.place(relx=0.918, rely=0.15, relwidth=0.074, relheight=0.70)
        btn_ukloni.bind("<Enter>", lambda _: btn_ukloni.config(bg=DANGER, fg=WHITE))
        btn_ukloni.bind("<Leave>", lambda _: btn_ukloni.config(bg="#FDECEA", fg=DANGER))
 
        self.nalazi_rows.append({
            "frame":    row_frame,
            "parametar": ent_p,
            "misljenje": ent_m,
            "btn_ukloni": btn_ukloni,
        })
 
    def remove_finding_row(self, frame: tk.Frame):
        for i, row in enumerate(self.nalazi_rows):
            if row["frame"] == frame:
                row["frame"].destroy()
                self.nalazi_rows.pop(i)
                break
 
    # ─────────────────────────────────────────────────────────────────────────
    # MVC public interface  (controller talks through these)
    # ─────────────────────────────────────────────────────────────────────────
 
    def get_user_input(self) -> MedicalReportModel:
        result = MedicalReportModel(
            patient_name=self.ent_ime.get(),
            report_date=self.ent_datum.get(),
            preporucena_terapija_i_savet=self.txt_terapija.get(
                "1.0", tk.END).strip(),
            nalazi=[]
        )
        for row in self.nalazi_rows:
            p = row["parametar"].get("1.0", tk.END).strip()
            m = row["misljenje"].get("1.0", tk.END).strip()
            if p or m:
                result.nalazi.append(MedicalCriticalFindingModel(
                    expertsko_misljenje=m,
                    parametar_i_vrednost=p
                ))
        return result
 
    def set_display_data(self, data: MedicalReportModel):
        self.ent_ime.delete(0, tk.END)
        self.ent_ime.insert(0, data.patient_name)
        self.ent_datum.delete(0, tk.END)
        self.ent_datum.insert(0, data.report_date)
        self.txt_terapija.delete("1.0", tk.END)
        self.txt_terapija.insert("1.0", data.preporucena_terapija_i_savet)
        for n in data.nalazi:
            self.add_finding_row(
                misljenje=n.expertsko_misljenje,
                parametar=n.parametar_i_vrednost
            )
 
    def update_status(self, header_text: str = "UNKNOWN", details_text: str = "/"):
        self.var_status.set(f"{header_text} | {details_text}")
 