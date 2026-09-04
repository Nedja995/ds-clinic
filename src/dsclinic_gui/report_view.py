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
from tkinter import ttk, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk

from models import app_settings, MedicalReport, MedicalReportModel, MedicalCriticalFindingModel, MedicalTherapyModel
from models.brand import brand_config
from npy.core.logger import setup_logger

from dsclinic_gui.styles import *
from dsclinic_gui.report_view_models import DSClinicViewModel
from dsclinic_gui.chat_session_view import ChatSessionView
from dsclinic_gui.settings.window import open_settings
from npy.core.event_emitter import ErrorMessageEvent
from dsclinic_gui.report_view_models import ExportRequest


## App Logger
logger = setup_logger()


##### ---------------------------------------------------------------- #####
class ReportWindow(tk.Toplevel):
    """Top-level window for displaying a medical report. Hosts the MedicalReportView and related dialogs."""
    _WIDTH      = 700
    _HEIGHT     = 750
    _MIN_WIDTH  = 400
    _MIN_HEIGHT = 400


##### ----------------------------------------------------------------- #####
class MedicalReportView(ttk.Frame):
    """View for displaying and editing medical reports."""
    
    def __init__(self, parent: ttk.Misc, view_model: DSClinicViewModel, **kwargs: any) -> None:
        super().__init__(parent, **kwargs)
        self.view_model = view_model

         # Tracks widgets for rows in the "Nalazi" section, so we can update/destroy them as needed.
        self.critical_finding_widgets:  list[dict]  = []
        self._row_parity_findings:      int         = 0
        
        # Track widget for rows in the "Terapija" section, if we later want to support multiple therapies with add/remove functionality.
        self.therapy_widgets:           list[dict] = []
        self._row_parity_therapy:       int        = 0

        # Layout and widgets
        self._setup_ui()
        
        # Event Binding (MVVM)
        #self.master.bind("<<VM_DataChanged>>", lambda e: self.update_view_from_viewmodel())
        self.view_model.on_vm_data_changed.subscribe(self.update_view_from_viewmodel)
        
        self.view_model.var_status_title.trace_add("write", lambda *args: self.update_view_from_viewmodel())
        self.view_model.var_is_analyzing.trace_add("write", lambda *args: self.update_view_from_viewmodel())

        # Subscribe to ViewModel export events
        self.view_model.on_show_error_message.subscribe(self._on_show_error_message)
        self.view_model.on_export_requested.subscribe(self._on_export_requested)
        self.view_model.on_export_succeeded.subscribe(self._on_export_succeeded)

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
        # # 
        # self.geometry(f"{self._WIDTH}x{self._HEIGHT}")
        # self.resizable(True, True)
        # self.minsize(self._MIN_WIDTH, self._MIN_HEIGHT)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self, parent: tk.Widget):
        self.top_frame = ttk.Frame(parent, style="Toolbar.TFrame", padding=(0, 6))
        self.top_frame.pack(side="top", fill="x")

        # Action buttons — left side
        self.btn_analyze = self._tooolbar_button(self.top_frame, textvariable=self.view_model.var_btn_analyze_text)
        self.btn_analyze.config(command=self.view_model.toggle_analysis)

        self.btn_export = self._tooolbar_button(self.top_frame, text=_("Export Report"))
        self.btn_export.config(command=self._handle_export_click)

        self.btn_full_report = self._tooolbar_button(self.top_frame, text=_("Details"), state="disabled")
        self.btn_settings    = self._tooolbar_button(self.top_frame, text=_("Settings"), side="right", command=lambda: open_settings(self.master))

        # Branded clinic identity — right side, left of Settings button (AD-20).
        # Logo image reference must be stored on self to prevent GC from
        # destroying the PhotoImage while the widget is still displayed.
        self._toolbar_logo_image = None
        logo_path = brand_config.resolved_logo_path()
        if logo_path:
            try:
                pil_img = Image.open(logo_path).resize((22, 22), Image.LANCZOS)
                self._toolbar_logo_image = ImageTk.PhotoImage(pil_img)
                ttk.Label(
                    self.top_frame,
                    image=self._toolbar_logo_image,
                    background=TOOLBAR,
                ).pack(side="right", padx=(0, 4))
            except Exception as exc:
                logger.debug(f"Toolbar logo load skipped: {exc}")

        # Clinic name + subtitle — condensed single-line label in the toolbar
        _subtitle = brand_config.clinic_subtitle
        _header_text = (
            f"{brand_config.clinic_name}  ·  {_subtitle}"
            if _subtitle else brand_config.clinic_name
        )
        ttk.Label(
            self.top_frame,
            text=_header_text,
            background=TOOLBAR,
            foreground=WHITE,
            font=FL,
        ).pack(side="right", padx=(0, 12))

        ttk.Frame(parent, style="Shadow.TFrame", height=2).pack(side="top", fill="x")

    def _tooolbar_button(self, parent, text="", textvariable=None, state="normal", command=None, side="left") -> ttk.Button:
        kw: dict = dict(style="Toolbar.TButton", state=state, command=command)
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
        patient_card = self._card(sf, _("PATIENT DATA"))
        patient_card.pack(fill="x", **PAD)

        pr = ttk.Frame(patient_card, style="Panel.TFrame", padding=(12, 0, 12, 2))
        pr.pack(fill="x")

        ttk.Label(pr, text=_("Name:"), style="FormLabel.TLabel").pack(side="left")
        self.ent_ime = ttk.Entry(pr, width=24, font=FI, textvariable=self.view_model.var_patient_name)
        self.ent_ime.pack(side="left", padx=(2, 2), ipady=2, pady=4)

        ttk.Label(pr, text=_("Date:"), style="FormLabel.TLabel").pack(side="left")
        self.ent_datum = ttk.Entry(pr, width=10, font=FI, textvariable=self.view_model.var_report_date)
        self.ent_datum.pack(side="left", padx=(2, 0), ipady=2, pady=4)
        
        # Card: Folder Inputs
        folder_card = self._card(sf, _("INPUT FINDINGS"))
        folder_card.pack(fill="x", **PAD)
        self._build_folder_input_row(folder_card, 
                                     _("Folder:"), 
                                     _("Browse"), 
                                     command=lambda: [self.update_viewmodel_from_view(), self._browse_folder(self.entry_folder), self.update_view_from_viewmodel()], 
                                     default_folder=self.view_model.var_input_dir.get())


        # Card: Terapija
        therapy_card = self._card(sf, _("RECOMMENDED THERAPY AND ADVICES"))
        therapy_card.pack(fill="x", **PAD)

        self.txt_terapija = self._scrolled_text(therapy_card, height=9)
        self.txt_terapija.pack(fill="x", padx=0, pady=(0, 0))

        # Card: Nalazi
        nalazi_card = self._card(sf, _("CRITICAL FINDINGS"))
        nalazi_card.pack(fill="x", **PAD)

        self.th = ttk.Frame(nalazi_card, style="THead.TFrame", height=26)
        self.th.pack(fill="x", padx=0, pady=(0, 2))
        self.th.pack_propagate(False)
        ttk.Label(self.th, text=_("Opinion / Explanation"), style="THeadLabel.TLabel").place(relx=0.0, rely=0, relwidth=0.595, relheight=1.0)
        ttk.Label(self.th, text=_("Parameter and Value"), style="THeadLabel.TLabel").place(relx=0.61, rely=0, relwidth=0.37, relheight=1.0)
        #self.th.grid_remove()  # Hide initially; only show if there are findings
        #self.th.pack_forget()  # Hide initially; only show if there are findings

        self.nalazi_container = ttk.Frame(nalazi_card, style="Rows.TFrame")
        self.nalazi_container.pack(fill="x", padx=0)

        self.btn_dodaj_nalaz = ttk.Button(
            nalazi_card, text=_("+ Add new Finding"),
            style="Accent.TButton",
            command=lambda: [self.update_viewmodel_from_view(), self.view_model.add_finding(), self.update_view_from_viewmodel()]
        )
        self.btn_dodaj_nalaz.pack(fill="x", padx=2, pady=(4, 4))

        # Card: Terapija
        terapija_card = self._card(sf, _("THERAPY"))
        terapija_card.pack(fill="x", **PAD)

        th2 = ttk.Frame(terapija_card, style="THead.TFrame", height=26)
        th2.pack(fill="x", padx=0, pady=(0, 2))
        th2.pack_propagate(False)
        ttk.Label(th2, text=_("Article / Product"), style="THeadLabel.TLabel").place(relx=0.0, rely=0, relwidth=0.595, relheight=1.0)
        ttk.Label(th2, text=_("Usage Instructions"), style="THeadLabel.TLabel").place(relx=0.61, rely=0, relwidth=0.37, relheight=1.0)

        self.terapija_container = ttk.Frame(terapija_card, style="Rows.TFrame")
        self.terapija_container.pack(fill="x", padx=0)

        self.btn_dodaj_terapiju = ttk.Button(
            terapija_card, text=_("+ Add new Therapy"),
            style="Accent.TButton",
            command=lambda: [self.update_viewmodel_from_view(), self.view_model.add_therapy(), self.update_view_from_viewmodel()]
        )
        self.btn_dodaj_terapiju.pack(fill="x", padx=2, pady=(4, 4))

        ttk.Frame(sf, height=24).pack()

    # ─────────────────────────────────────────────────────────────────────────
    # Widget factories
    # ─────────────────────────────────────────────────────────────────────────

    def _card(self, parent, title: str) -> ttk.Frame:
        outer = ttk.Frame(parent, style="Card.TFrame")
        strip = ttk.Frame(outer, style="Strip.TFrame", height=30)
        strip.pack(fill="x")
        strip.pack_propagate(False)
        ttk.Label(strip, text=title, style="CardTitle.TLabel", anchor="center").pack(fill="both", expand=True)
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
    
    # -- Folder Input Row ─────────────────────────────────────────────────────

    def _browse_folder(self, entry_folder: ttk.Entry):
        # Open the native system directory chooser
        self.selected_directory = filedialog.askdirectory()
        
        if self.selected_directory:
            # Clear any existing text inside the entry box
            entry_folder.delete(0, tk.END)
            # Insert the newly selected directory path
            entry_folder.insert(0, self.selected_directory)
            
            self.entry_folder = entry_folder
            app_settings.input_dir = self.selected_directory
            app_settings.save_unified()
            self.view_model.var_input_dir.set(self.selected_directory)
            self.view_model._update_model_from_viewmodel()

    # --- Folder Input Row ─────────────────────────────────────────────────────

    def _build_folder_input_row(self, parent, label_text: str, button_text: str, command, default_folder: str = None):
        # Create a frame to hold the label, entry, and button
        frame = ttk.Frame(parent, style="Panel.TFrame", padding=(12, 0, 12, 2))
        frame.pack(fill="x", pady=(4, 4))
        # Add the label, entry, and button to the frame
        ttk.Label(frame, text=label_text, style="FormLabel.TLabel").pack(side="left")
        self.entry_folder = ttk.Entry(frame, width=40, font=FI)
        if default_folder:
            self.entry_folder.insert(0, default_folder)
        self.entry_folder.pack(side="left", padx=(6, 6), ipady=2)
        # Add the button to the frame
        browse_button = ttk.Button(frame, text=button_text, command=command)
        browse_button.pack(side="left", padx=(6, 0), ipady=2)


    # ─────────────────────────────────────────────────────────────────────────
    # Nalazi rows
    # ─────────────────────────────────────────────────────────────────────────

    def _render_finding_row(self, index: int, finding: MedicalCriticalFindingModel, is_enabled=True):
        """Renders a single row based on VM data."""
        logger.debug(f"Rendering finding row {index}: {finding.parametar_and_value}")
        self._row_parity_findings += 1
        
        row_style = "RowA.TFrame" if self._row_parity_findings % 2 else "RowB.TFrame"
        row_bg    = ROW_A         if self._row_parity_findings % 2 else ROW_B

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
            state="normal" if is_enabled else "disabled",
            command=lambda i=index: [self.update_viewmodel_from_view(), self.view_model.remove_finding(i), self.update_view_from_viewmodel()]
        )
        btn_ukloni.place(relx=0.918, rely=0.15, relwidth=0.074, relheight=0.70)

        self.critical_finding_widgets.append({
            "frame":      row_frame,
            "parametar":  ent_p,
            "misljenje":  ent_m,
        })

    def _render_therapy_row(self, index: int, therapy: MedicalTherapyModel, is_enabled=True):
        """Renders a single therapy row based on VM data."""
        logger.debug(f"Rendering therapy row {index}: {therapy.article}")
        self._row_parity_therapy += 1

        row_style = "RowA.TFrame" if self._row_parity_therapy % 2 else "RowB.TFrame"
        row_bg    = ROW_A         if self._row_parity_therapy % 2 else ROW_B

        row_frame = ttk.Frame(self.terapija_container, style=row_style, height=72)
        row_frame.pack(fill="x", pady=(0, 0))
        row_frame.pack_propagate(False)

        ent_article = self._scrolled_text(row_frame, height=1, bg=row_bg)
        ent_article.insert("1.0", therapy.article)
        ent_article.place(relx=0.0, rely=0.06, relwidth=0.595, relheight=0.88)

        ent_instructions = self._scrolled_text(row_frame, height=1, bg=row_bg)
        ent_instructions.insert("1.0", therapy.using_instructions)
        ent_instructions.place(relx=0.610, rely=0.06, relwidth=0.295, relheight=0.88)

        btn_ukloni = ttk.Button(
            row_frame, text="✕", style="Danger.TButton",
            state="normal" if is_enabled else "disabled",
            command=lambda i=index: [self.update_viewmodel_from_view(), self.view_model.remove_therapy(i), self.update_view_from_viewmodel()]
        )
        btn_ukloni.place(relx=0.918, rely=0.15, relwidth=0.074, relheight=0.70)

        self.therapy_widgets.append({
            "frame":        row_frame,
            "article":      ent_article,
            "instructions": ent_instructions,
        })

    def set_all_entries_state(self, state: str):
        self.ent_ime.config(state=state)
        self.ent_datum.config(state=state)
        self.txt_terapija.config(state=state)
        self.btn_dodaj_nalaz.config(state=state)
        self.btn_dodaj_terapiju.config(state=state)
        self.btn_analyze.config(state=state)
        self.btn_export.config(state=state)

        for widgets in self.critical_finding_widgets:
            widgets["parametar"].config(state=state)
            widgets["misljenje"].config(state=state)
            widgets["frame"].children.get("!button", tk.Button()).config(state=state)

        for widgets in self.therapy_widgets:
            widgets["article"].config(state=state)
            widgets["instructions"].config(state=state)
            widgets["frame"].children.get("!button", tk.Button()).config(state=state)
            
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

        # Therapy List
        for i, widgets in enumerate(self.therapy_widgets):
            if i < len(self.view_model.therapy_data):
                self.view_model.therapy_data[i].article            = widgets["article"].get("1.0", tk.END).strip()
                self.view_model.therapy_data[i].using_instructions = widgets["instructions"].get("1.0", tk.END).strip()


    def update_view_from_viewmodel(self):
        """Updates complex widgets based on current VM state."""
        
        logger.debug(f"Updating View from ViewModel={self.view_model}...")
        
        # if self.view_model.findings and len(self.view_model.findings) > 0:
        #     self.th.grid()  # Show header if there are findings
        #     # self.th.pack(fill="x", padx=0, pady=(0, 2))
        #     self.th.pack(fill="x", padx=0, pady=(0, 2), before=self.th_or_first_element)
        # else:
        #     #self.th.grid_remove()  # Hide header if no findings
        #     self.th.pack_forget()  # Hide header if no findings
        
        # Reset parity for row colors
        self._row_parity_findings = 0
        self._row_parity_therapy  = 0

        is_analyzing = self.view_model.var_is_analyzing.get()
        
        # ScrolledText (tk.Text) ignores delete/insert if state is 'disabled'.
        # We must temporarily enable it to update content.
        self.txt_terapija.config(state="normal")

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
            self._render_finding_row(i, finding, not is_analyzing)

        # Therapy Rows (Rebuild completely)
        for w in self.therapy_widgets:
            w["frame"].destroy()
        self.therapy_widgets.clear()

        for i, therapy in enumerate(self.view_model.therapy_data):
            self._render_therapy_row(i, therapy, not is_analyzing)
            
        self.set_all_entries_state("disabled" if is_analyzing else "normal")

    # ─────────────────────────────────────────────────────────────────────────
    # MVVM Bindings
    # ─────────────────────────────────────────────────────────────────────────

    def _handle_export_click(self):
        """Export button handler. Syncs Text widgets → VM, then asks the VM to prepare."""
        self.update_viewmodel_from_view()
        self.view_model.prepare_export()   # VM will emit on_export_requested

    def _on_export_requested(self, request: ExportRequest) -> None:
        """
        View-owned dialog logic. Receives an ExportRequest from the ViewModel,
        shows the file dialog, then calls VM.execute_export() with the chosen path.
        """
        output_filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialdir=request.default_dir,
            initialfile=request.default_filename,
        )
        if not output_filepath:
            return  # user cancelled — nothing to do

        try:
            self.view_model.execute_export(output_filepath)
        except Exception as e:
            logger.error(e)
            self.view_model.var_status_title.set("Error")
            self.view_model.var_status_detail.set("Failed to generate PDF: ")
            messagebox.showerror("Error", str(e))

    def _on_export_succeeded(self, output_filepath: str) -> None:
        """Called by the ViewModel after a successful export. Shows the open-file prompt."""
        from npy.core import fileutils
        if messagebox.askyesno("Success", "Report generated. Open file?"):
            fileutils.open_file_from_filepath(output_filepath)

    def _on_show_error_message(self, error_event: ErrorMessageEvent) -> None:
        """Called by the ViewModel when an error message needs to be displayed."""
        messagebox.showerror(error_event.title, error_event.message)