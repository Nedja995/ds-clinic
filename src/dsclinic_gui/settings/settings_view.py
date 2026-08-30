"""
settings_view.py – Settings Window (View)
==========================================
Subclasses tk.Toplevel. Follows MVVM; binds to SettingsViewModel.
Intentional tk.* exceptions (documented):
  - tk.Canvas              – scrollable host, no ttk equivalent
  - tk.Frame               – _card/_nested_card border-color trick
  - scrolledtext.ScrolledText – multiline text; internal tk.Text
  - tk.StringVar / tk.DoubleVar / tk.BooleanVar – always tk
"""
import tkinter as tk
from tkinter import Frame, ttk, scrolledtext

from dsclinic_gui.styles import (
    BG, PANEL, TOOLBAR, WHITE, ACCENT, BORDER,
    TEXT, SUBTLE, DANGER, SHADOW,
    FL, FI, FSB, FS,
)
from dsclinic_gui.settings.settings_view_model import SettingsViewModel
from npy.core.localization import TranslationManager
from npy.core import utils


class SettingsWindow(tk.Toplevel):

    _WIDTH  = 640
    _HEIGHT = 860  # increased to accommodate three credential fields
    _MIN_WIDTH = 400
    _MIN_HEIGHT = 400


    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        self.resizable(True, True)
        self.minsize(self._MIN_WIDTH, self._MIN_HEIGHT)
        self.configure(bg=BG)
        self._center_window(self._WIDTH, self._HEIGHT)

        self.view_model = SettingsViewModel()
        self.languages = {"English": "en", "Srpski": "sr", "Español": "es"}

        initial_lang = self.view_model.var_app_language.get()
        locale_dir = utils.get_resource_dirpath('locale')
        self.translator = TranslationManager(
            locale_dir=locale_dir,
            default_lang=initial_lang,
            save_config_callback=self.save_config_language
        )

        self._setup_ui()
        self.view_model.update_from_config()
        self.translator.register_ui(self.refresh_text)
        self.refresh_text()
        self._bind_events()

        self.transient(master)
        self.grab_set()

    def destroy(self) -> None:
        self._unbind_all()
        super().destroy()

    def _center_window(self, w: int, h: int):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ─────────────────────────────────────────────────────────────────────────
    # Setup
    # ─────────────────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self._build_toolbar()
        self._build_scroll_area()
        self._build_patient_data_section()
        self._build_ai_section()
        self._build_general_section()
        self._build_support_section()
        self._finalize_scroll()

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, style="Toolbar.TFrame", padding=(8, 6))
        bar.pack(side="top", fill="x")
        ttk.Label(
            bar, text="Settings",
            background=TOOLBAR, foreground=WHITE, font=FL,
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            bar, text="Save",
            style="Toolbar.TButton",
            command=self._on_save,
        ).pack(side="right")
        ttk.Frame(self, style="Shadow.TFrame", height=2).pack(side="top", fill="x")

    def _build_scroll_area(self) -> None:
        host = ttk.Frame(self)
        host.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(host, bg=BG, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(host, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=sb.set)

        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = ttk.Frame(self._canvas, padding=(16, 12))
        self._canvas_win = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._inner.bind("<Configure>",
                         lambda _: self._canvas.configure(scrollregion=self._canvas.bbox("all")))

    def _finalize_scroll(self) -> None:
        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _build_row(self, parent) -> ttk.Frame:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 0))
        frame.pack(fill="x", pady=(0, 0))
        return frame

    # ─────────────────────────────────────────────────────────────────────────
    # Patient Data Section
    # ─────────────────────────────────────────────────────────────────────────

    def _build_patient_data_section(self) -> None:
        gen = self._card("Patient Data")
        row = self._build_row(gen)
        ttk.Checkbutton(row, text="Auto Anonymization", variable=self.view_model.var_anonymization_on).pack(side="left", padx=(4, 0))
        if not self.view_model.var_anonymization_on.get():
            ttk.Checkbutton(row, text="Anonymize Custom Texts", variable=self.view_model.var_anonymization_custom_texts_on).pack(side="left", padx=(4, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # AI Section
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ai_section(self) -> None:
        ai = self._card("AI")
        self._build_model_panel(ai)
        self._build_analyze_instructions_panel(ai)

    def _build_model_panel(self, parent: ttk.Frame) -> None:
        panel = self._sub_panel(parent, "Model")
        row = ttk.Frame(panel, style="Panel.TFrame")
        row.pack(fill="x")
        row.columnconfigure((0, 1, 2), weight=1, uniform="col")

        c0 = ttk.Frame(row, style="Panel.TFrame")
        c0.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ttk.Label(c0, text="Model Name", style="FormLabel.TLabel").pack(anchor="w")
        ttk.Combobox(
            c0, textvariable=self.view_model.var_model_name,
            values=self.view_model.available_models,
            state="readonly", font=FI,
        ).pack(fill="x", pady=(2, 0))

        c1 = ttk.Frame(row, style="Panel.TFrame")
        c1.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self._slider_field(c1, "Temperature", self.view_model.var_temperature, 0.0, 2.0)

        c2 = ttk.Frame(row, style="Panel.TFrame")
        c2.grid(row=0, column=2, sticky="ew")
        self._slider_field(c2, "Top P", self.view_model.var_top_p, 0.0, 1.0)

    def _build_analyze_instructions_panel(self, parent: ttk.Frame) -> None:
        panel = self._sub_panel(parent, "Analyze Instructions")

        self._entry_field(panel, "Recommended Therapy and Advice",
                          self.view_model.var_recommended_therapy_prompt)
        self._entry_field(panel, "Critical Findings",
                          self.view_model.var_critical_findings_prompt)

        nested = self._nested_card(panel, "Critical Findings")
        self._entry_field(nested, "Expertsko Mišljenje", self.view_model.var_expert_opinion_label)
        self._entry_field(nested, "Parameter and Value", self.view_model.var_parameter_value_label)

        self._text_field(panel, "Initial Task Description",
                         self.view_model.var_initial_task_text, height=4)

        self.system_instructions_frame = ttk.Frame(panel, style="Panel.TFrame", padding=(0, 0, 0, 6))
        self.system_instructions_frame.pack(fill="x")
        ttk.Label(self.system_instructions_frame,
                  text="System Instructions", style="FormLabel.TLabel").pack(anchor="w")
        self._sys_instr_text = self._make_text_widget(self.system_instructions_frame, height=5)
        self._sync_text_widget(self._sys_instr_text, self.view_model.var_system_instructions_text)

        # ── API Credentials (OS keyring — never written to disk) ──────────────
        self._credential_field(panel, "Google API Key",    self.view_model.var_google_api_key)
        self._credential_field(panel, "Anthropic API Key", self.view_model.var_anthropic_api_key)
        self._credential_field(panel, "Google Project ID", self.view_model.var_google_project_id)

    # ─────────────────────────────────────────────────────────────────────────
    # General Section
    # ─────────────────────────────────────────────────────────────────────────

    def save_config_language(self, lang_code):
        self.view_model.var_app_language.set(lang_code)
        self.view_model.save_to_config()

    def refresh_text(self):
        current_code = self.translator.current_lang
        for display_name, code in self.languages.items():
            if code == current_code:
                self.view_model.var_app_language.set(display_name)
                break

    def load_config_language(self):
        return self.view_model.var_app_language.get()

    def on_language_change(self, event):
        selected_display = self.view_model.var_app_language.get()
        target_lang_code = self.languages[selected_display]
        self.translator.apply_language(target_lang_code)

    def _build_general_section(self) -> None:
        gen = self._card("General")

        self.view_model.var_app_language = tk.StringVar()
        lang_row = ttk.Frame(gen, style="Panel.TFrame", padding=(0, 4, 0, 10))
        lang_row.pack(fill="x")
        ttk.Label(lang_row, text="Languages:", style="FormLabel.TLabel").pack(side="left")
        self.dropdown = ttk.Combobox(
            lang_row, textvariable=self.view_model.var_app_language,
            values=list(self.languages.keys()), state="readonly", width=15,
        )
        self.dropdown.pack(side="left", padx=(10, 0))
        self.dropdown.bind("<<ComboboxSelected>>", self.on_language_change)

        ver_row = ttk.Frame(gen, style="Panel.TFrame", padding=(0, 4, 0, 2))
        ver_row.pack(fill="x")
        ttk.Label(ver_row, text="App Version", style="FormLabel.TLabel").pack(side="left")
        ttk.Label(ver_row, textvariable=self.view_model.var_app_version,
                  background=PANEL, foreground=SUBTLE, font=FI).pack(side="left", padx=(8, 0))

    # ─────────────────────────────────────────────────────────────────────────
    # Support Section
    # ─────────────────────────────────────────────────────────────────────────

    def _build_support_section(self) -> None:
        sup = self._card("Support")

        email_frame = ttk.Frame(sup, style="Panel.TFrame", padding=(0, 0, 0, 10))
        email_frame.pack(fill="x")
        email_row = ttk.Frame(email_frame, style="Panel.TFrame")
        email_row.pack(fill="x")
        ttk.Label(email_row, text="Support Email", style="FormLabel.TLabel").pack(side="left")
        self._email_entry = ttk.Entry(email_row, textvariable=self.view_model.var_support_email)
        self._email_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self._email_error_lbl = ttk.Label(
            email_frame, text="✕  Invalid email format",
            background=PANEL, foreground=DANGER, font=FS,
        )

        btn_row = ttk.Frame(sup, style="Panel.TFrame", padding=(0, 4, 0, 0))
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Send Logs", style="Accent.TButton",
                   command=self.view_model.on_send_logs).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Show Logs Folder", style="Accent.TButton",
                   command=self.view_model.on_show_logs_folder).pack(side="left")

    # ─────────────────────────────────────────────────────────────────────────
    # Widget / Layout helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _card(self, title: str) -> ttk.Frame:
        outer = ttk.Frame(self._inner, padding=(0, 0, 0, 14))
        outer.pack(fill="x")
        border = tk.Frame(outer, bg=SHADOW, padx=1, pady=1)
        border.pack(fill="x")
        card = ttk.Frame(border, style="Panel.TFrame")
        card.pack(fill="both", expand=True)
        ttk.Label(card, text=title.upper(),
                  style="CardTitle.TLabel", anchor="w").pack(fill="x", ipady=6)
        content = ttk.Frame(card, style="Panel.TFrame", padding=(14, 10, 14, 10))
        content.pack(fill="x")
        return content

    def _sub_panel(self, parent: ttk.Frame, title: str) -> ttk.Frame:
        wrapper = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 10))
        wrapper.pack(fill="x")
        ttk.Label(wrapper, text=title,
                  background=PANEL, foreground=ACCENT, font=FL).pack(anchor="w", pady=(0, 6))
        content = ttk.Frame(wrapper, style="Panel.TFrame")
        content.pack(fill="x")
        return content

    def _nested_card(self, parent: ttk.Frame, title: str) -> ttk.Frame:
        wrapper = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 2, 0, 8))
        wrapper.pack(fill="x")
        ttk.Label(wrapper, text=title,
                  background=PANEL, foreground=SUBTLE, font=FSB).pack(anchor="w", pady=(0, 4))
        border = tk.Frame(wrapper, bg=BORDER, padx=1, pady=1)
        border.pack(fill="x")
        content = ttk.Frame(border, style="Panel.TFrame", padding=(10, 6))
        content.pack(fill="x")
        return content

    def _entry_field(self, parent: ttk.Frame, label: str,
                     var: tk.StringVar, show: str = "") -> ttk.Entry:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 6))
        frame.pack(fill="x")
        ttk.Label(frame, text=label, style="FormLabel.TLabel").pack(anchor="w")
        entry = ttk.Entry(frame, textvariable=var, show=show)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _credential_field(self, parent: ttk.Frame, label: str,
                          var: tk.StringVar) -> ttk.Entry:
        """Masked entry for OS keyring credentials with a security hint label."""
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 6))
        frame.pack(fill="x")
        ttk.Label(frame, text=label, style="FormLabel.TLabel").pack(anchor="w")
        entry = ttk.Entry(frame, textvariable=var, show="*")
        entry.pack(fill="x", pady=(2, 0))
        ttk.Label(
            frame,
            text="Stored securely in OS keyring — never written to disk.",
            background=PANEL, foreground=SUBTLE, font=FS,
        ).pack(anchor="w", pady=(2, 0))
        return entry

    def _slider_field(self, parent: ttk.Frame, label: str,
                      var: tk.DoubleVar, from_: float, to: float) -> ttk.Scale:
        ttk.Label(parent, text=label, style="FormLabel.TLabel",
                  background=PANEL).pack(anchor="w")
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(2, 0))
        val_lbl = ttk.Label(row, text=f"{var.get():.2f}",
                            background=PANEL, foreground=ACCENT, font=FSB, width=5)
        val_lbl.pack(side="right")
        sc = ttk.Scale(row, from_=from_, to=to, variable=var, orient="horizontal")
        sc.pack(side="left", fill="x", expand=True, padx=(0, 4))
        var.trace_add("write", lambda *_: val_lbl.config(text=f"{var.get():.2f}"))
        return sc

    def _make_text_widget(self, parent: ttk.Frame,
                          height: int = 4) -> scrolledtext.ScrolledText:
        w = scrolledtext.ScrolledText(
            parent, height=height, wrap="word",
            font=FI, bg=PANEL, fg=TEXT,
            relief="flat", bd=0,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            highlightthickness=1,
        )
        w.pack(fill="x", pady=(2, 0))
        return w

    def _text_field(self, parent: ttk.Frame,
                    label: str,
                    var: tk.StringVar,
                    height: int = 4) -> scrolledtext.ScrolledText:
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(0, 0, 0, 6))
        frame.pack(fill="x")
        ttk.Label(frame, text=label, style="FormLabel.TLabel").pack(anchor="w")
        w = self._make_text_widget(frame, height)
        self._sync_text_widget(w, var)
        return w

    def _sync_text_widget(self, widget: scrolledtext.ScrolledText,
                          var: tk.StringVar) -> None:
        def _var_to_widget(*_: object) -> None:
            new_val = var.get()
            if widget.get("1.0", "end-1c") != new_val:
                widget.delete("1.0", "end")
                widget.insert("1.0", new_val)

        def _widget_to_var(_event: tk.Event) -> None:
            var.set(widget.get("1.0", "end-1c"))

        var.trace_add("write", _var_to_widget)
        widget.bind("<FocusOut>", _widget_to_var)
        widget.bind("<KeyRelease>", _widget_to_var)

    # ─────────────────────────────────────────────────────────────────────────
    # Events
    # ─────────────────────────────────────────────────────────────────────────

    def _bind_events(self) -> None:
        self.view_model.var_support_email.trace_add("write", lambda *_: self.view_model.validate_email())
        self.view_model.var_email_valid.trace_add("write", self._on_email_validity_changed)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel)

    def _unbind_all(self) -> None:
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_canvas_resize(self, event: tk.Event) -> None:
        self._canvas.itemconfigure(self._canvas_win, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:
        if event.delta:
            delta = int(-1 * event.delta / 120)
        else:
            delta = -1 if event.num == 4 else 1
        self._canvas.yview_scroll(delta, "units")

    def _on_email_validity_changed(self, *_: object) -> None:
        if self.view_model.var_email_valid.get():
            self._email_error_lbl.pack_forget()
        else:
            self._email_error_lbl.pack(anchor="w", pady=(2, 0))

    def _on_save(self) -> None:
        if not self.view_model.validate_email():
            return
        self.view_model.save_to_config()
        self._unbind_all()
        self.destroy()
