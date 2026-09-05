"""
src/dsclinic_gui/chat_session_view.py — Chat panel View.

Owns: ChatSessionView (the right-hand chat pane), MarkdownLabel (inline
      markdown renderer built on tk.Text).

Streaming architecture (v2.12.1):
  - var_chunk trace: updates the in-progress bot bubble in-place on every
    CHUNK event. Creates the bubble on the first chunk of each turn.
  - var_response trace: fires once at FINISHED to call append_chat_response()
    for persistence sync. Does NOT spawn a new bubble.
  - var_is_analyzing trace: clears _current_bot_bubble reference when the
    ViewModel transitions to idle so the next turn gets a fresh bubble.

Provider selector (v2.12.2):
  - ttk.Combobox in the header strip bound to view_model.var_active_provider.
  - postcommand refreshes values on every open; <<ComboboxSelected>> calls
    view_model.set_provider_by_name(); disabled while analyzing.

Reanalyze (v2.12.3):
  - Additional prompt ttk.Entry bound to var_additional_prompt, above the send row.
  - "↺ Reanalyze" button calls view_model.reanalyze(); disabled while analyzing.
  - var_reanalysis_summary trace adds a [Reanalysis] labeled bot bubble on completion.

Report inclusion checkboxes (v2.12.4):
  - Each bot bubble has a ttk.Checkbutton below the MarkdownLabel.
  - Checkbutton BooleanVar defaults True (include in PDF export).
  - On toggle: view_model.set_message_inclusion(bot_index, value) updates the
    ChatMessage.include_in_report flag and rebuilds _model.chat_responses.
  - _bot_bubble_count tracks the 0-based bot-turn index for each bubble created
    in this session; incremented in _add_bot_bubble() after the bubble is finalized.

Does NOT own: business logic, AI calls, session persistence.
"""
from __future__ import annotations

import re
from typing import Any, Literal, Optional

import tkinter as tk
import tkinter.ttk as ttk

from dsclinic_gui.styles import BG, ACCENT, WHITE, FOOTER_BG
from dsclinic_gui.report_view_models import DSClinicViewModel
from npy.core.logger import setup_logger

logger = setup_logger()


# ── Markdown bubble widget ────────────────────────────────────────────────────

class MarkdownLabel(tk.Text):
    """
    Read-only tk.Text widget that renders a limited markdown subset inline.

    Supports: ## headers, **bold**, plain text, and newlines.
    update_text() is the only public mutation point.
    """

    def __init__(
        self,
        container: tk.Misc,
        text: str,
        style_name: str,
        wraplength: int = 300,
        **kwargs: Any,
    ) -> None:
        bg_color = "#f0f0f0" if "Bot" in style_name else "#d1e7ff"

        super().__init__(
            container,
            width=1,
            highlightthickness=0,
            borderwidth=0,
            wrap="word",
            bg=bg_color,
            fg="black",
            font=("Segoe UI", 10),
            cursor="arrow",
            **kwargs,
        )

        self.tag_configure("bold",   font=("Segoe UI", 10, "bold"))
        self.tag_configure("header", font=("Segoe UI", 12, "bold"))
        self.tag_configure("bullet", lmargin1=10, lmargin2=20)

        self._insert_markdown(text)
        self.configure(state="disabled")
        self._recalculate_height()

    def _insert_markdown(self, text: str) -> None:
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

    def _recalculate_height(self) -> None:
        self.update_idletasks()
        line_count = float(self.index("end-1c").split(".")[0])
        self.configure(height=int(line_count))
        self.configure(width=40)

    def update_text(self, new_text: str) -> None:
        """Replace widget content with new_text and resize to fit.

        Called on every CHUNK event for in-place streaming update.
        """
        self.configure(state="normal")
        self.delete("1.0", "end")
        self._insert_markdown(new_text)
        self.configure(state="disabled")
        self._recalculate_height()


# ── Main chat view ────────────────────────────────────────────────────────────

class ChatSessionView(ttk.Frame):
    """
    Right-hand chat pane.

    Manages the scrollable bubble list, additional-prompt / reanalyze row,
    and message send row. Streaming updates are applied in-place via
    _current_bot_bubble. Each bot bubble carries a checkbutton that controls
    whether the response is included in the PDF export (v2.12.4).
    """

    def __init__(
        self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)
        self.view_model = view_model

        # Holds the bot bubble currently receiving stream chunks.
        self._current_bot_bubble: Optional[MarkdownLabel] = None

        # 0-based counter of bot bubbles created in this session view.
        # Each completed bot bubble increments this so the checkbutton closure
        # captures the correct bot_index for set_message_inclusion().
        self._bot_bubble_count: int = 0

        self._build_ui()
        self._bind_viewmodel()

    def _bind_viewmodel(self) -> None:
        self.view_model.var_chunk.trace_add("write", lambda *_: self._on_chunk())
        self.view_model.var_response.trace_add("write", lambda *_: self._on_response_finalised())
        self.view_model.var_is_analyzing.trace_add("write", lambda *_: self._on_analyzing_changed())
        self.view_model.var_reanalysis_summary.trace_add("write", lambda *_: self._on_reanalysis_complete())
        self._update_input_state()

    def _on_chunk(self) -> None:
        text = self.view_model.var_chunk.get()
        if not text:
            return
        if self._current_bot_bubble is None:
            # First chunk — create the bubble; checkbutton will be added at FINISHED.
            self._current_bot_bubble = self._add_bot_bubble_label(text)
        else:
            self._current_bot_bubble.update_text(text)
        self._scroll_to_bottom()

    def _on_response_finalised(self) -> None:
        """FINISHED signal: add checkbutton to the completed streaming bubble,
        rebuild chat responses via append_chat_response(), increment bot counter.
        """
        answer = self.view_model.var_response.get()
        if not answer:
            return

        # Attach the inclusion checkbutton to the bubble that just finished.
        if self._current_bot_bubble is not None:
            self._attach_inclusion_checkbutton(
                self._current_bot_bubble, self._bot_bubble_count
            )

        # Notify the ViewModel to rebuild _model.chat_responses from chat_history.
        self.view_model.append_chat_response(answer)
        self._bot_bubble_count += 1

    def _on_analyzing_changed(self) -> None:
        if not self.view_model.var_is_analyzing.get():
            self._current_bot_bubble = None
        self._update_input_state()

    def _on_reanalysis_complete(self) -> None:
        summary = self.view_model.var_reanalysis_summary.get()
        if not summary:
            return
        self._add_full_bot_bubble(f"[Reanalysis] {summary}")
        self._scroll_to_bottom()

    def _update_input_state(self) -> None:
        is_busy = self.view_model.var_is_analyzing.get()
        state = "disabled" if is_busy else "normal"
        self.btn_send.config(state=state)
        self.ent_message.config(state=state)
        self.btn_reanalyze.config(state=state)
        self.ent_additional_prompt.config(state=state)
        self.cmb_provider.config(state="disabled" if is_busy else "readonly")

    def _build_ui(self) -> None:
        self._build_header()
        self._build_reanalyze_row()
        self._build_send_row()
        self._build_history_canvas()

    def _build_header(self) -> None:
        header = ttk.Frame(self, style="Strip.TFrame", padding=(8, 4))
        header.pack(side="top", fill="x")

        ttk.Label(header, text="CHAT ASISTENT", style="CardTitle.TLabel").pack(side="left")

        provider_frame = ttk.Frame(header, style="Strip.TFrame")
        provider_frame.pack(side="right", padx=(0, 4))

        ttk.Label(
            provider_frame, text="Provider:",
            background=ACCENT, foreground=WHITE, font=("Segoe UI", 8),
        ).pack(side="left", padx=(0, 4))

        self.cmb_provider = ttk.Combobox(
            provider_frame,
            textvariable=self.view_model.var_active_provider,
            state="readonly", width=14, font=("Segoe UI", 8),
        )
        self.cmb_provider.pack(side="left")
        self.cmb_provider.configure(postcommand=self._refresh_provider_list)
        self.cmb_provider.bind("<<ComboboxSelected>>", self._on_provider_selected)
        self._refresh_provider_list()

    def _build_reanalyze_row(self) -> None:
        reanalyze_pane = ttk.Frame(self, style="Footer.TFrame", padding=(12, 4))
        reanalyze_pane.pack(side="bottom", fill="x")

        self.ent_additional_prompt = ttk.Entry(
            reanalyze_pane,
            textvariable=self.view_model.var_additional_prompt,
            font=("Segoe UI", 9),
        )
        self.ent_additional_prompt.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=2)

        self.btn_reanalyze = ttk.Button(
            reanalyze_pane, text="↺ Reanalyze",
            style="Accent.TButton", command=self._on_reanalyze,
        )
        self.btn_reanalyze.pack(side="right")

    def _build_send_row(self) -> None:
        input_pane = ttk.Frame(self, style="Footer.TFrame", padding=(12, 8))
        input_pane.pack(side="bottom", fill="x")

        self.ent_message = ttk.Entry(
            input_pane, textvariable=self.view_model.var_initial_question
        )
        self.ent_message.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=2)
        self.ent_message.bind("<Return>", lambda _e: self._on_send())

        self.btn_send = ttk.Button(
            input_pane, text="Pošalji",
            style="Accent.TButton", command=self._on_send,
        )
        self.btn_send.pack(side="right")

    def _refresh_provider_list(self) -> None:
        self.cmb_provider.configure(values=self.view_model.available_provider_names())

    def _on_provider_selected(self, _event: Any) -> None:
        self.view_model.set_provider_by_name(self.view_model.var_active_provider.get())

    def _on_send(self) -> None:
        question = self.view_model.var_initial_question.get().strip()
        if not question:
            return
        self.add_user_bubble(question)
        self.view_model.followup_question_submit()

    def _on_reanalyze(self) -> None:
        prompt = self.view_model.var_additional_prompt.get().strip()
        label = f"[Reanalyze] {prompt}" if prompt else "[Reanalyze]"
        self.add_user_bubble(label)
        self.view_model.reanalyze()

    def _build_history_canvas(self) -> None:
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
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win_id, width=e.width))

        def _wheel(ev: Any) -> None:
            delta = int(-1 * ev.delta / 120) if ev.delta else (-1 if ev.num == 4 else 1)
            self.canvas.yview_scroll(delta, "units")

        self.canvas.bind_all("<MouseWheel>", _wheel)
        self.canvas.bind_all("<Button-4>", _wheel)
        self.canvas.bind_all("<Button-5>", _wheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _scroll_to_bottom(self) -> None:
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def add_user_bubble(self, text: str) -> None:
        """Render a right-aligned user message bubble."""
        if not text:
            return
        bubble_wrap = ttk.Frame(self.history_frame, padding=(12, 6))
        bubble_wrap.pack(side="top", fill="x")
        bubble = ttk.Frame(bubble_wrap, style="ChatUser.TFrame", padding=8)
        bubble.pack(anchor="e")
        ttk.Label(bubble, text=text, style="ChatUser.TLabel", wraplength=300).pack()
        self._scroll_to_bottom()

    def _add_bot_bubble_label(self, text: str) -> MarkdownLabel:
        """Create the bot bubble MarkdownLabel only (no checkbutton yet).

        The checkbutton is attached in _on_response_finalised() once the full
        response has arrived, because we need the final bot_index to be stable
        before creating the closure. Returns the MarkdownLabel for in-place
        streaming updates.
        """
        bubble_wrap = ttk.Frame(self.history_frame, padding=(12, 6))
        bubble_wrap.pack(side="top", fill="x")

        bubble = ttk.Frame(bubble_wrap, style="ChatBot.TFrame", padding=8)
        bubble.pack(anchor="w")

        label = MarkdownLabel(bubble, text=text, style_name="ChatBot")
        label.pack()

        # Store bubble frame reference on the label so _attach_inclusion_checkbutton
        # can add the checkbutton to the same parent frame.
        label._bubble_frame = bubble  # type: ignore[attr-defined]

        self._scroll_to_bottom()
        return label

    def _attach_inclusion_checkbutton(
        self, label: MarkdownLabel, bot_index: int
    ) -> None:
        """Add a 'Include in report' checkbutton below a completed bot bubble.

        bot_index is the 0-based index of this bubble in the bot-turn sequence.
        The BooleanVar starts True (matching ChatMessage.include_in_report default).
        The closure captures bot_index by value so toggling always targets the
        correct message even after further bubbles are added.
        """
        var = tk.BooleanVar(value=True)
        bubble_frame: ttk.Frame = label._bubble_frame  # type: ignore[attr-defined]

        def _on_toggle() -> None:
            self.view_model.set_message_inclusion(bot_index, var.get())

        chk = ttk.Checkbutton(
            bubble_frame,
            text="Include in report",
            variable=var,
            command=_on_toggle,
            style="TCheckbutton",
        )
        chk.pack(anchor="w", pady=(4, 0))
        logger.debug("Checkbutton attached to bot bubble %d.", bot_index)

    def _add_full_bot_bubble(self, text: str) -> None:
        """Create a complete bot bubble with checkbutton in one call.

        Used for non-streaming bot messages (e.g. [Reanalysis] label bubbles)
        where there is no intermediate streaming phase.
        """
        label = self._add_bot_bubble_label(text)
        self._attach_inclusion_checkbutton(label, self._bot_bubble_count)
        self.view_model.append_chat_response(text)
        self._bot_bubble_count += 1

    # Legacy shim
    def add_message(self, text: str, is_user: bool = True) -> None:
        """Deprecated shim — prefer add_user_bubble() or _add_full_bot_bubble()."""
        if not text:
            return
        if is_user:
            self.add_user_bubble(text)
        else:
            self._add_full_bot_bubble(text)
