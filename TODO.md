### v2.6.6 — Runtime Key Consumption: `dsclinic.py` & API Clients ✅ Completed

- [x] `ClaudeAnalyzerClient` instantiated in `DSClinic.__init__` using `get_credential("anthropic")` — was previously missing entirely.
- [x] Claude client wrapped in startup guard: `self.claude_client = None` if key absent — app starts without crashing.
- [x] `ClaudeModelConfig` and `ClaudeAIServiceConfig` imported and wired in `dsclinic.py`.
- [x] `api_gemini/client.py` — replaced `raise ValueError` on missing key with `logger.warning` + early `return`. `RuntimeError` raised at call time with Settings navigation hint.
- [x] `api_claude/client.py` — same startup guard pattern applied.
- [x] Both clients guard `self.client`/`self.chat_session` before use — `RuntimeError` with clear message if called without a key.
- [x] `src/api_gemini/client.py`: zero `app_settings.*` references — key via `config.api_key` only.
- [x] `src/api_claude/client.py`: zero `app_settings.*` references — key via `config.api_key` only.