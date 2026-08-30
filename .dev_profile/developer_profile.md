# Developer Profile & Strategy Notes (In-Repo)

## 1. Professional Background
* **Seniority:** Senior Full-Stack Software Engineer with 12 years of professional experience.
* **Track Record:** Developed/published 50+ conventional/commercial projects. Low turnover (minimum 3+ years per company) with strong LinkedIn recommendations.
* **Core Goal:** Transitioning to a stable, high-value, remote EU Software Engineer, AI Engineer, or Solutions Architect role.

## 2. Developer AI Assistant Stack
* **Workflows:** Active subscriptions to both **Claude AI** and **Google Gemini** (AI Studio/Vertex).
* **Usage:** Both assistants are utilized in parallel during coding sessions. Workflows must be structured to support clean code handoffs and dual-prompt compatibility so that either model can pick up and contribute effectively.

## 3. Hardware Constraints
* **GPU Setup:** 1x 16GB VRAM GPU passed through to a Proxmox/LXC Linux container.
* **Limitations:** Experiences bottlenecks/crashes when running multiple or heavy vision models locally.
* **Mitigation Strategy:** Emphasize 4-bit/8-bit quantization via Ollama and utilize third-party high-speed, GDPR-compliant APIs for open-weights models (Groq, Together AI, HuggingFace) as hybrid fallbacks.

## 4. Key Portfolio Target
* **Project Focus:** Transforming `ds-clinic` into an enterprise-ready, multi-brand B2B medical platform.
* **Key Showcase Features:**
  - Pluggable `LLMProvider` interface (Gemini, Claude, Groq, Together, HuggingFace, Ollama).
  - Split-Horizon Hybrid Inference Architecture (local/remote open models for extraction/PII scrubbing; heavy cloud LLMs for anonymized reasoning).
  - Custom local medical preprocessors (MONAI for 3D DICOM MRI slice selection; trained YOLOv8 or Vision Transformers on open datasets like DeepLesion or microscopy blood smears for hallucination-free metrics).
  - Full automated `pytest` coverage to prove senior production rigor.

---

## 5. Version & Commit Discipline (GASSI Standard)

This is a project-wide rule that applies to **every sub-version, every session, every AI assistant**.

### Sub-version Rule
Every parent milestone (e.g. `v2.6.0`) is broken into discrete numbered sub-tasks (`v2.6.1`, `v2.6.2`, ...). Each sub-version is a **self-contained, committable unit of work**. Sub-versions are completed in order. The parent version is marked done only when all sub-versions are complete.

### One Commit Per Sub-version
Each sub-version gets exactly **one git commit**. Code changes and all doc updates are staged and committed together in that single commit. Never split a sub-version across multiple commits; never bundle two sub-versions into one commit.

### Commit Command — Generated After Each Completed Task
The AI assistant provides the exact `git add` + `git commit` + `git push` command **at the end of every completed task**, listing only the files actually changed in that task. Commands are never pre-written in advance for future sub-versions.

**Format:**
```bash
git add <exact files changed in this task>
git commit -m "vX.Y.Z: <imperative short description of what changed>"
git push
```

**Commit message format:** `v{MAJOR}.{MINOR}.{PATCH}: <what changed>`

Examples:
- `v2.6.1: read app_name/version from pyproject.toml via importlib.metadata`
- `v2.6.3: purge secret fields from AppSettings and load_unified()`
- `v2.6.7: delete settings.ini, rotate keys, final security audit`

### Mandatory Doc Updates Per Sub-version
The AI assistant must check and update **every applicable file** from this list without being reminded. Skipping any applicable file is an error.

| File | Update | When |
|---|---|---|
| `CHANGELOG.md` | New `## [X.Y.Z]` entry (Added / Fixed / Changed) | Every sub-version |
| `TODO.md` | Mark completed tasks `[x]` | Every sub-version |
| `pyproject.toml` | Bump `version = "X.Y.Z"` | Every sub-version |
| `docs/session_handoff.md` | Update current status to next sub-version | Every sub-version |
| `docs/architecture.md` | Add `AD-XX` for any non-obvious design or structural decision | Any time a design choice is made |
| `GEMINI.md` | Update architectural guidelines or project-wide workflow rules | Any time project-wide rules change |
| `.dev_profile/developer_profile.md` | Update workflow rules, constraints, or standing conventions | Any time a standing rule is added or changed |

### TODO Archiving Rule
**Completed versions are never collapsed or summarised.** Every completed sub-version and its full task list remains fully expanded with `[x]` checkboxes in `TODO.md` indefinitely. The only change on completion is marking tasks `[x]` and adding a ✅ to the section heading. Never remove task detail, never replace a completed section with a one-liner stub.

### What NOT to Do
- Never use `git add .` — always stage specific files only.
- Never commit without updating `CHANGELOG.md` and `TODO.md`.
- Never bump `pyproject.toml` version without a matching `CHANGELOG.md` entry.
- Never leave `docs/session_handoff.md` pointing at a completed sub-version.
- Never pre-write commit commands for future sub-versions — generate them at task completion only.
- Never skip `docs/architecture.md` when a design decision was made — add an AD entry.
- Never skip `.dev_profile/developer_profile.md` when a standing workflow rule changes.
- Never collapse or stub out completed TODO sections — keep all task detail fully visible.
