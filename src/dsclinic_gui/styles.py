from tkinter import ttk

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

# ─────────────────────────────────────────────────────────────────────────
# ttk.Style  (single source of truth for all colors / fonts)
# ─────────────────────────────────────────────────────────────────────────

def build_styles():
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
    
    # Chat message styles
    s.configure("ChatUser.TFrame", background=ACCENT_LT)
    s.configure("ChatBot.TFrame",  background=WHITE)
    s.configure("ChatUser.TLabel", background=ACCENT_LT, foreground=TEXT, font=FI)
    s.configure("ChatBot.TLabel",  background=WHITE,     foreground=TEXT, font=FI)

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