"""
src/dsclinic_gui/chat_session_view.py — Chat panel View.

Owns: ChatSessionView (the right-hand chat pane), MarkdownLabel (inline
      markdown renderer built on tk.Text).

Streaming architecture (v2.12.1):
  - var_chunk trace: updates the in-progress bot bubble in-place on every
    CHUNK event. Creates the bubble on the first chunk of each turn.
  - var_response trace: fires once at FINISHED to call append_chat_response()
    for model persistence. Does NOT spawn a new bubble.
  - var_is_analyzing trace: clears _current_bot_bubble reference when the
    ViewModel transitions to idle so the next turn gets a fresh bubble.

Provider selector (v2.12.2):
  - ttk.Combobox in the header strip bound to view_model.var_active_provider.
  - postcommand refreshes values from view_model.available_provider_names()
    on every open so runtime changes (e.g. Ollama daemon start) are reflected.
  - <<ComboboxSelected>> calls view_model.set_provider_by_name(); disabled
    while var_is_analyzing is True alongside the send button and entry.

Does NOT own: business logic, AI calls, session persistence.
"""
from __future__ import annotations

import re
from typing import Any, Literal, Optional

import tkinter as tk
import tkinter.ttk as ttk

from dsclinic_gui.styles import BG, ACCENT, WHITE, SUBTLE
from dsclinic_gui.report_view_models import DSClinicViewModel
from npy.core.logger import setup_logger

logger = setup_logger()


# ── Markdown bubble widget ────────────────────────────────────────────────────

class MarkdownLabel(tk.Text):
    """
    Read-only tk.Text widget that renders a limited markdown subset inline.

    Supports: ## headers, **bold**, plain text, and newlines.
    The widget is kept in DISABLED state between mutations to prevent
    accidental user edits. update_text() is the only public mutation point.
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

        self.tag_configure("bold",   font=("Segoe UI", 10, "bold"))
        self.tag_configure("header", font=("Segoe UI", 12, "bold"))
        self.tag_configure("bullet", lmargin1=10, lmargin2=20)

        self._insert_markdown(text)
        self.configure(state="disabled")
        self._recalculate_height()

    def _insert_markdown(self, text: str) -> None:
        """Insert markdown-annotated text into the widget (widget must be NORMAL)."""
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
        """Replace the widget content with new_text and resize to fit.

        Called on every CHUNK event to update the in-progress streaming
        bubble in place without spawning a new widget.
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

    Manages the scrollable bubble list and the message input row. Streaming
    updates are applied in-place via _current_bot_bubble — only one bubble
    object is created per bot turn regardless of how many CHUNK events arrive.
    """

    def __init__(
        self, parent: tk.Misc, view_model: DSClinicViewModel, **kwargs: Any
    ) -> None:
        super().__init__(parent, **kwargs)
        logger.debug("Building ChatSessionView...")
        self.view_model = view_model

        # Holds a reference to the bot bubble currently receiving stream chunks.
        # Reset to None when var_is_analyzing transitions True → False so the
        # next turn gets a fresh bubble on its first chunk.
        self._current_bot_bubble: Optional[MarkdownLabel] = None

        self._build_ui()
        self._bind_viewmodel()

    def _bind_viewmodel(self) -> None:
        """Wire all ViewModel observable vars to View handlers."""
        # var_chunk: fires on every streaming fragment — update bubble in place.
        self.view_model.var_chunk.trace_add(
            "write",
            lambda *_: self._on_chunk(),
        )
        # var_response: fires once at FINISHED — persist response, no new bubble.
        self.view_model.var_response.trace_add(
            "write",
            lambda *_: self._on_response_finalised(),
        )
        # var_is_analyzing: clear the in-progress bubble reference when idle
        # and sync input widget states.
        self.view_model.var_is_analyzing.trace_add(
            "write",
            lambda *_: self._on_analyzing_changed(),
        )
        self._update_input_state()

    def _on_chunk(self) -> None:
        """Handle a streaming CHUNK event from the ViewModel.

        Creates the bot bubble on the first chunk of a turn; calls update_text()
        on subsequent chunks so the text grows in-place without layout thrash.
        """
        text = self.view_model.var_chunk.get()
        if not text:
            return

        if self._current_bot_bubble is None:
            self._current_bot_bubble = self._add_bot_bubble(text)
        else:
            self._current_bot_bubble.update_text(text)

        self._scroll_to_bottom()

    def _on_response_finalised(self) -> None:
        """Handle the FINISHED signal — persist the completed response.

        Does NOT create a new bubble: the streaming bubble already contains
        the full text by the time FINISHED arrives.
        """
        answer = self.view_model.var_response.get()
        if answer:
            self.view_model.append_chat_response(answer)

    def _on_analyzing_changed(self) -> None:
        """Clear the in-progress bubble reference and sync widget states."""
        if not self.view_model.var_is_analyzing.get():
            # Turn is over — next send creates a new bubble from scratch.
            self._current_bot_bubble = None
        self._update_input_state()

    def _update_input_state(self) -> None:
        """Enable or disable all interactive widgets based on analyzing state.

        The provider Combobox and the send controls are all disabled together
        while a task is running so the user cannot change the provider mid-stream
        or submit a second question before the first completes.
        """
        state = "disabled" if self.view_model.var_is_analyzing.get() else "normal"
        self.btn_send.config(state=state)
        self.ent_message.config(state=state)
        self.cmb_provider.config(state="disabled" if self.view_model.var_is_analyzing.get() else "readonly")

    def _build_ui(self) -> None:
        self._build_header()

        input_pane = ttk.Frame(self, style="Footer.TFrame", padding=(12, 8))
        input_pane.pack(side="bottom", fill="x")

        self.ent_message = ttk.Entry(
            input_pane, textvariable=self.view_model.var_initial_question
        )
        self.ent_message.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=2)
        self.ent_message.bind("<Return>", lambda _e: self._on_send())

        self.btn_send = ttk.Button(
            input_pane,
            text="Pošalji",
            style="Accent.TButton",
            command=self._on_send,
        )
        self.btn_send.pack(side="right")

        self._build_history_canvas()

    def _build_header(self) -> None:
        """Build the header strip containing the title and provider selector.

        The provider Combobox uses 'readonly' state so the user picks from the
        list rather than typing a raw provider name. postcommand refreshes the
        values list on every open so runtime availability changes are reflected
        without requiring an app restart.
        """
        header = ttk.Frame(self, style="Strip.TFrame", padding=(8, 4))
        header.pack(side="top", fill="x")

        ttk.Label(
            header,
            text="CHAT ASISTENT",
            style="CardTitle.TLabel",
        ).pack(side="left")

        # Provider selector — right-aligned in the header strip.
        provider_frame = ttk.Frame(header, style="Strip.TFrame")
        provider_frame.pack(side="right", padx=(0, 4))

        ttk.Label(
            provider_frame,
            text="Provider:",
            background=ACCENT,
            foreground=WHITE,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=(0, 4))

        self.cmb_provider = ttk.Combobox(
            provider_frame,
            textvariable=self.view_model.var_active_provider,
            state="readonly",
            width=14,
            font=("Segoe UI", 8),
        )
        self.cmb_provider.pack(side="left")

        # Refresh available providers on every dropdown open — catches Ollama
        # daemon start or new API key added after app launch.
        self.cmb_provider.configure(
            postcommand=self._refresh_provider_list,
        )
        self.cmb_provider.bind("<<ComboboxSelected>>", self._on_provider_selected)

        # Populate on build so the list is not empty before first open.
        self._refresh_provider_list()

    def _refresh_provider_list(self) -> None:
        """Reload the Combobox values from the ViewModel's live availability check."""
        names = self.view_model.available_provider_names()
        self.cmb_provider.configure(values=names)

    def _on_provider_selected(self, _event: Any) -> None:
        """Forward the selected provider name to the ViewModel."""
        selected = self.view_model.var_active_provider.get()
        self.view_model.set_provider_by_name(selected)

    def _on_send(self) -> None:
        """Send button handler — adds the user bubble then submits to ViewModel."""
        question = self.view_model.var_initial_question.get().strip()
        if not question:
            return
        self.add_user_bubble(question)
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

        self._win_id = self.canvas.create_window(
            (0, 0), window=self.history_frame, anchor="nw"
        )
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

    def _scroll_to_bottom(self) -> None:
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def add_user_bubble(self, text: str) -> None:
        """Render a right-aligned user message bubble."""
        if not text:
            return
        self._add_bubble(text, is_user=True)

    def _add_bot_bubble(self, text: str) -> MarkdownLabel:
        """Render a left-aligned bot bubble and return the MarkdownLabel widget.

        The caller stores the reference so subsequent chunks can call
        update_text() on the same widget.
        """
        bubble_wrap = ttk.Frame(self.history_frame, padding=(12, 6))
        bubble_wrap.pack(side="top", fill="x")

        bubble = ttk.Frame(bubble_wrap, style="ChatBot.TFrame", padding=8)
        bubble.pack(anchor="w")

        label = MarkdownLabel(bubble, text=text, style_name="ChatBot")
        label.pack()

        self._scroll_to_bottom()
        return label

    def _add_bubble(self, text: str, is_user: bool) -> None:
        """Render a plain ttk.Label bubble (used for user messages)."""
        anchor: Literal["e", "w"] = "e" if is_user else "w"
        style_frame = "ChatUser.TFrame" if is_user else "ChatBot.TFrame"
        style_label = "ChatUser.TLabel" if is_user else "ChatBot.TLabel"

        bubble_wrap = ttk.Frame(self.history_frame, padding=(12, 6))
        bubble_wrap.pack(side="top", fill="x")

        bubble = ttk.Frame(bubble_wrap, style=style_frame, padding=8)
        bubble.pack(anchor=anchor)

        lbl = ttk.Label(bubble, text=text, style=style_label, wraplength=300)
        lbl.pack()

        self._scroll_to_bottom()

    # Legacy public method preserved for any external callers from v2.12.0 and earlier.
    def add_message(self, text: str, is_user: bool = True) -> None:
        """Deprecated shim — prefer add_user_bubble() or _add_bot_bubble()."""
        if not text:
            return
        if is_user:
            self.add_user_bubble(text)
        else:
            self.view_model.append_chat_response(text)
