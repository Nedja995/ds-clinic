from __future__ import annotations

import re
from typing import Any, Literal

import tkinter as tk
import tkinter.ttk as ttk

from dsclinic_gui.styles import BG
from dsclinic_gui.report_view_models import DSClinicViewModel
from npy.core.logger import setup_logger

logger = setup_logger()


# ── Markdown bubble widget ────────────────────────────────────────────────────

class MarkdownLabel(tk.Text):
    def __init__(
        self,
        container: tk.Misc,
        text: str,
        style_name: str,
        wraplength: int = 300,
        **kwargs: Any,
    ) -> None:
        bg_color = "#f0f0f0" if "Bot" in style_name else "#d1e7ff"
        fg_color = "black"

        super().__init__(
            container,
            width=1,
            highlightthickness=0,
            borderwidth=0,
            wrap="word",
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 10),
            cursor="arrow",
            **kwargs,
        )

        self.wraplength_px = wraplength

        self.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.tag_configure("header", font=("Segoe UI", 12, "bold"))
        self.tag_configure("bullet", lmargin1=10, lmargin2=20)

        self.insert_markdown(text)
        self.configure(state="disabled")
        self.update_height()

    def insert_markdown(self, text: str) -> None:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            header_match = re.match(r"^(#{1,6})\s*(.*)", line)
            if header_match:
                self.insert("end", header_match.group(2), "header")
            else:
                parts = re.split(r"(\*\*.*?\*\*)", line)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        self.insert("end", part[2:-2], "bold")
                    else:
                        self.insert("end", part)
            if i < len(lines) - 1:
                self.insert("end", "\n")

    def update_height(self) -> None:
        self.update_idletasks()
        line_count = float(self.index("end-1c").split(".")[0])
        self.configure(height=int(line_count))
        self.configure(width=40)


# ── Main chat view ────────────────────────────────────────────────────────────

class ChatSessionView(ttk.Frame):
    def __init__(
        self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)
        logger.debug("Building ChatSessionView...")
        self.view_model = view_model
        self._build_ui()

        self.view_model.var_response.trace_add(
            "write",
            lambda *args: self.add_message(self.view_model.var_response.get(), is_user=False),
        )
        self.view_model.var_is_analyzing.trace_add(
            "write", lambda *args: self._update_ui_state()
        )
        self._update_ui_state()

    def _update_ui_state(self) -> None:
        state = "disabled" if self.view_model.var_is_analyzing.get() else "normal"
        self.btn_send.config(state=state)
        self.ent_message.config(state=state)

    def _build_ui(self) -> None:
        header = ttk.Frame(self, style="Strip.TFrame", height=30)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        ttk.Label(header, text="CHAT ASISTENT", style="CardTitle.TLabel").pack(
            fill="both", expand=True
        )

        input_pane = ttk.Frame(self, style="Footer.TFrame", padding=(12, 8))
        input_pane.pack(side="bottom", fill="x")

        self.ent_message = ttk.Entry(
            input_pane, textvariable=self.view_model.var_initial_question
        )
        self.ent_message.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=2)

        self.btn_send = ttk.Button(
            input_pane,
            text="Pošalji",
            style="Accent.TButton",
            command=self._on_send,
        )
        self.btn_send.pack(side="right")

        self._build_history_canvas()

    def _on_send(self) -> None:
        """Send button handler — adds the user bubble then submits to ViewModel."""
        self.add_message(self.view_model.var_initial_question.get())
        self.view_model.followup_question_submit()

    def _build_history_canvas(self) -> None:
        logger.debug("Building history canvas...")
        wrap = ttk.Frame(self)
        wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(wrap, bg=BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.history_frame = ttk.Frame(self.canvas)

        self.history_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self._win_id = self.canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self._win_id, width=e.width),
        )

        def _wheel(ev: Any) -> None:
            delta = int(-1 * ev.delta / 120) if ev.delta else (-1 if ev.num == 4 else 1)
            self.canvas.yview_scroll(delta, "units")

        self.canvas.bind_all("<MouseWheel>", _wheel)
        self.canvas.bind_all("<Button-4>", _wheel)
        self.canvas.bind_all("<Button-5>", _wheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def add_message(self, text: str, is_user: bool = True) -> None:
        """Renders a chat bubble aligned to the correct side."""
        logger.debug(f"Adding message: {text}")
        if not text:
            return

        if not is_user:
            self.view_model.append_chat_response(text)

        anchor: Literal["e", "w"] = "e" if is_user else "w"
        style_frame = "ChatUser.TFrame" if is_user else "ChatBot.TFrame"
        style_label = "ChatUser.TLabel" if is_user else "ChatBot.TLabel"

        bubble_wrap = ttk.Frame(self.history_frame, padding=(12, 6))
        bubble_wrap.pack(side="top", fill="x")

        bubble = ttk.Frame(bubble_wrap, style=style_frame, padding=8)
        bubble.pack(anchor=anchor)

        lbl = ttk.Label(bubble, text=text, style=style_label, wraplength=300)
        lbl.pack()

        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
