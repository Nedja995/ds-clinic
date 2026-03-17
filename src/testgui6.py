"""
Patient Data Input Form
=======================
Tkinter GUI za unos podataka pacijenta sa punom podrškom
za srpski jezik (unicode). Integriše se sa postojećom
funkcijom za generisanje PDF-a.

Pokretanje: python patient_input_form.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os


# ---------------------------------------------------------------------------
# Ovde ubaci svoju funkciju za generisanje PDF-a
# ---------------------------------------------------------------------------
def generate_pdf(patient_name: str, therapy_advice: str) -> str:
    """
    Placeholder – zameni ovom tvojom stvarnom funkcijom.

    Args:
        patient_name:    Ime pacijenta.
        therapy_advice:  Preporučena terapija i savet.

    Returns:
        Putanja do generisanog PDF fajla.
    """
    # --- PRIMER (ukloni kada povežeš svoju funkciju) ---
    output_path = f"{patient_name.replace(' ', '_')}_izvestaj.pdf"
    print(f"[PDF] Generisanje za: {patient_name}")
    print(f"[PDF] Terapija: {therapy_advice}")
    print(f"[PDF] Sačuvano: {output_path}")
    return output_path
    # ---------------------------------------------------


# ---------------------------------------------------------------------------
# Stilske konstante
# ---------------------------------------------------------------------------
FONT_LABEL  = ("Segoe UI", 10, "bold")
FONT_INPUT  = ("Segoe UI", 10)
FONT_TEXT   = ("Segoe UI", 10)
FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_BTN    = ("Segoe UI", 10, "bold")

COLOR_BG        = "#F5F7FA"
COLOR_PANEL     = "#FFFFFF"
COLOR_ACCENT    = "#1A6FA8"
COLOR_ACCENT2   = "#E8F1F8"
COLOR_BORDER    = "#C8D8E8"
COLOR_TEXT      = "#1C2B3A"
COLOR_SUBTLE    = "#6B7D8E"
COLOR_SUCCESS   = "#2E7D32"
COLOR_DANGER    = "#C62828"
COLOR_BTN_FG    = "#FFFFFF"


# ---------------------------------------------------------------------------
# Glavni prozor
# ---------------------------------------------------------------------------
class PatientInputForm(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Osnovno podešavanje prozora ---
        self.title("Unos podataka pacijenta")
        self.resizable(True, True)
        self.minsize(520, 480)
        self.configure(bg=COLOR_BG)

        # Unicode / srpski font na svim platformama
        self._configure_encoding()

        self._build_ui()
        self._center_window(560, 560)

    # ------------------------------------------------------------------
    # Enkoding / font
    # ------------------------------------------------------------------
    def _configure_encoding(self):
        """Osigurava UTF-8 output na Windowsu i postavljia defaultni font."""
        if sys.platform == "win32":
            # Python 3.7+ automatski koristi UTF-8 u Tk,
            # ali ovo osigurava konzolu
            import io
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        # Postavi defaultni font za sve Tk widgete
        self.option_add("*Font", FONT_INPUT)

    # ------------------------------------------------------------------
    # Izgradnja UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---- Naslov ----
        header = tk.Frame(self, bg=COLOR_ACCENT, pady=14)
        header.pack(fill="x")

        tk.Label(
            header,
            text="📋  Izveštaj pacijenta",
            font=FONT_TITLE,
            bg=COLOR_ACCENT,
            fg=COLOR_BTN_FG,
            anchor="w",
        ).pack(padx=20)

        tk.Label(
            header,
            text="Popunite polja i generišite PDF izveštaj",
            font=("Segoe UI", 9),
            bg=COLOR_ACCENT,
            fg="#B8D4EC",
            anchor="w",
        ).pack(padx=20)

        # ---- Glavni sadržaj ----
        content = tk.Frame(self, bg=COLOR_BG, padx=20, pady=16)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)

        # ---- Polje: Ime pacijenta ----
        self._section_label(content, "Ime i prezime pacijenta", row=0)

        self.entry_name = tk.Entry(
            content,
            font=FONT_INPUT,
            bg=COLOR_PANEL,
            fg=COLOR_TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            highlightcolor=COLOR_ACCENT,
        )
        self.entry_name.grid(row=1, column=0, sticky="ew", pady=(2, 14), ipady=7, padx=1)
        self._bind_focus_highlight(self.entry_name)

        # ---- Polje: Preporučena terapija i savet ----
        self._section_label(content, "Preporučena terapija i savet", row=2)

        # Omotač za border efekat
        text_frame = tk.Frame(
            content,
            bg=COLOR_BORDER,
            bd=0,
            padx=1,
            pady=1,
        )
        text_frame.grid(row=3, column=0, sticky="nsew", pady=(2, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        content.rowconfigure(3, weight=1)

        self.text_therapy = scrolledtext.ScrolledText(
            text_frame,
            font=FONT_TEXT,
            bg=COLOR_PANEL,
            fg=COLOR_TEXT,
            relief="flat",
            bd=0,
            wrap="word",
            undo=True,
            padx=8,
            pady=6,
            insertbackground=COLOR_ACCENT,
        )
        self.text_therapy.grid(row=0, column=0, sticky="nsew")
        self._bind_focus_highlight_text(self.text_therapy, text_frame)

        # Hint ispod text area
        tk.Label(
            content,
            text="Podržana su sva srpska slova: č, ć, š, ž, đ / Č, Ć, Š, Ž, Đ",
            font=("Segoe UI", 8),
            bg=COLOR_BG,
            fg=COLOR_SUBTLE,
        ).grid(row=4, column=0, sticky="w", pady=(0, 12))

        # ---- Status bar ----
        self.status_var = tk.StringVar(value="")
        self.status_label = tk.Label(
            content,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg=COLOR_BG,
            fg=COLOR_SUCCESS,
            anchor="w",
        )
        self.status_label.grid(row=5, column=0, sticky="ew")

        # ---- Dugmad ----
        btn_frame = tk.Frame(self, bg=COLOR_BG, padx=20, pady=12)
        btn_frame.pack(fill="x")

        self._make_button(
            btn_frame,
            "🗑  Obriši",
            self._clear_form,
            bg="#E0E0E0",
            fg=COLOR_TEXT,
            side="left",
        )

        self._make_button(
            btn_frame,
            "📄  Generiši PDF",
            self._on_generate,
            bg=COLOR_ACCENT,
            fg=COLOR_BTN_FG,
            side="right",
        )

    # ------------------------------------------------------------------
    # Pomoćne metode za UI
    # ------------------------------------------------------------------
    def _section_label(self, parent, text: str, row: int):
        tk.Label(
            parent,
            text=text,
            font=FONT_LABEL,
            bg=COLOR_BG,
            fg=COLOR_TEXT,
            anchor="w",
        ).grid(row=row, column=0, sticky="w", pady=(0, 2))

    def _make_button(self, parent, text, command, bg, fg, side="right"):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONT_BTN,
            bg=bg,
            fg=fg,
            activebackground=COLOR_ACCENT2,
            activeforeground=COLOR_ACCENT,
            relief="flat",
            bd=0,
            padx=18,
            pady=8,
            cursor="hand2",
        )
        btn.pack(side=side, padx=(0, 6) if side == "right" else (0, 6))

        # Hover efekat
        orig_bg = bg
        btn.bind("<Enter>", lambda e: btn.configure(bg=self._darken(orig_bg)))
        btn.bind("<Leave>", lambda e: btn.configure(bg=orig_bg))
        return btn

    @staticmethod
    def _darken(hex_color: str) -> str:
        """Malo zatamni boju za hover efekat."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r - 20), max(0, g - 20), max(0, b - 20)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _bind_focus_highlight(self, widget):
        widget.bind("<FocusIn>",  lambda e: widget.configure(highlightbackground=COLOR_ACCENT))
        widget.bind("<FocusOut>", lambda e: widget.configure(highlightbackground=COLOR_BORDER))

    def _bind_focus_highlight_text(self, widget, frame):
        widget.bind("<FocusIn>",  lambda e: frame.configure(bg=COLOR_ACCENT))
        widget.bind("<FocusOut>", lambda e: frame.configure(bg=COLOR_BORDER))

    def _center_window(self, w: int, h: int):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------------------------------------------------------
    # Akcije
    # ------------------------------------------------------------------
    def _get_values(self) -> tuple[str, str]:
        name    = self.entry_name.get().strip()
        therapy = self.text_therapy.get("1.0", "end").strip()
        return name, therapy

    def _clear_form(self):
        self.entry_name.delete(0, "end")
        self.text_therapy.delete("1.0", "end")
        self._set_status("")
        self.entry_name.focus_set()

    def _set_status(self, msg: str, error: bool = False):
        self.status_var.set(msg)
        self.status_label.configure(fg=COLOR_DANGER if error else COLOR_SUCCESS)

    def _on_generate(self):
        name, therapy = self._get_values()

        # Validacija
        if not name:
            self._set_status("⚠  Unesite ime pacijenta.", error=True)
            self.entry_name.focus_set()
            return
        if not therapy:
            self._set_status("⚠  Unesite preporučenu terapiju i savet.", error=True)
            self.text_therapy.focus_set()
            return

        self._set_status("⏳  Generisanje PDF-a...")
        self.update_idletasks()

        try:
            pdf_path = generate_pdf(
                patient_name=name,
                therapy_advice=therapy,
            )
            self._set_status(f"✅  PDF sačuvan: {pdf_path}")
            messagebox.showinfo(
                "Uspešno",
                f"PDF izveštaj je generisan:\n{pdf_path}",
            )
        except Exception as exc:
            self._set_status(f"❌  Greška: {exc}", error=True)
            messagebox.showerror("Greška", str(exc))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = PatientInputForm()
    app.mainloop()