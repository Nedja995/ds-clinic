# Session Handoff — DSClinic Chat Session View Integration

This handoff is prepared to allow any incoming development AI assistant (including Gemini CLI and Claude) to immediately continue development, specifically focusing on the next immediate milestone: **Completing the Chat Session View and styling it dynamically.**

> [!IMPORTANT]
> **Handoff & TODO Update Rule (GASSI Standard):** On *every single code modification or task completion*, the active AI assistant MUST immediately update both `TODO.md` (maintaining descending version order) and `docs/session_handoff.md`. This maintains perfect workspace continuity across different development platforms and resets, avoiding duplicate work and context waste.

---

## 1. What to Build: Chat Session View & Streaming
You are implementing/rewriting `src/dsclinic_gui/chat_session_view.py`. 

### The Core Challenge & Streaming Bug:
Currently, the `ChatSessionView.add_message` method is designed to spawn a new chat bubble (`ttk.Frame` + `ttk.Label` or `MarkdownLabel`) every time a new text string is written. However, during AI inference, the view model's reactive state `var_response` is written to **in real-time increments (word-by-word streaming)**.
* **The Bug:** If we simply trace `var_response` and call `add_message()` on every write, the app will spawn a *new* chat bubble for every word/chunk of the incoming stream, cluttering the UI with hundreds of micro-bubbles!
* **The Solution (Active Stream Tracking):**
  - We must track whether a bot stream is currently active (e.g., using `self._current_bot_bubble` or `self._is_streaming` state inside the View).
  - When the first chunk of a bot response arrives, spawn a **single** bot message bubble, and keep a reference to its text-rendering widget (e.g., a mutable text widget or custom label).
  - On subsequent chunk arrivals, append or update the text inside that **same** bubble in-place, instead of spawning a new one.
  - When the stream completes (or `var_is_analyzing` transitions back to `False`), clear the stream bubble reference.

### Formatting & Rendering:
* Use the existing custom `MarkdownLabel` (which wraps `tk.Text`) to support headers (`###`), bullet points (`-`), and bold text (`**`).
* Ensure `MarkdownLabel` can be updated dynamically during streaming (e.g., support clear-and-reinsert or append-and-format logic).

### Styling:
* Chat bubbles must be beautifully styled using definitions from `src/dsclinic_gui/styles.py`.
* User messages must align to the right (`anchor="e"`, blue bubble, white text).
* Bot messages must align to the left (`anchor="w"`, grey/white bubble, black text).
* Ensure proper auto-scrolling to the bottom of the scrollable canvas as new chunks stream in.

---

## 2. File Context for This Task

Before writing code, please read and analyze these files in the repository:
1. `src/dsclinic_gui/chat_session_view.py` — The primary file you will modify.
2. `src/dsclinic_gui/styles.py` — Holds the colors, fonts, and widget styling rules.
3. `src/dsclinic_gui/main_container.py` — Main UI container that hosts `ChatSessionView`.
4. `src/dsclinic_gui/report_view_models.py` — Holds the `DSClinicViewModel` which owns `var_response`, `var_is_analyzing`, and `var_initial_question`.
5. `GEMINI.md` — Holds the strict MVVM architecture rules and template reference.

---

## 3. Step-by-Step Implementation Strategy

1. **Review and Update `styles.py`:** Check if specific chat styles (`ChatUser.TFrame`, `ChatBot.TFrame`, etc.) are fully defined, and if not, add them following the existing app color palette.
2. **Refactor `MarkdownLabel`:**
   - Enhance the `MarkdownLabel(tk.Text)` class. Since it wraps a standard `tk.Text` widget (one of the three exceptions in our strict MVVM guidelines), ensure it handles word-wrapping beautifully and is configured to be non-editable by the user.
   - Implement a method `update_text(text: str)` or `append_text(chunk: str)` that updates/re-parses the markdown rendering in-place.
3. **Refactor `ChatSessionView` Trace Listeners:**
   - Instead of immediately appending a new bubble on every trace of `var_response`, check if `self._current_bot_bubble` is set.
   - If `self._current_bot_bubble` exists, update its text.
   - If not (this is the start of a new stream), call `add_message(is_user=False)` to spawn a new bubble, store its reference in `self._current_bot_bubble`, and populate the first chunk.
4. **Wire input validation and loading state:**
   - Trace `var_is_analyzing` to disable the entry field and "Send" button while the AI is thinking/streaming, showing a loading indicator or clearing the input field once sent.
5. **Auto-Scroll Management:**
   - Ensure the scrollable canvas updates its scroll region dynamically and scrolls to `1.0` (the bottom) on every chunk write.
