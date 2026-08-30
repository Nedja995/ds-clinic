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
* **Mitigation Strategy:** Emphasize 4-bit/8-bit quantization via Ollama and utilize third-party high-speed, GDPR-compliant APIs for open-weights models (Groq, Together AI, HuggingFace) as hybrid failovers.

## 4. Key Portfolio Target
* **Project Focus:** Transforming `ds-clinic` into an enterprise-ready, multi-brand B2B medical platform.
* **Key Showcase Features:**
  - Pluggable `LLMProvider` interface (Gemini, Claude, Groq, Together, HuggingFace, Ollama).
  - Split-Horizon Hybrid Inference Architecture (local/remote open models for extraction/PII scrubbing; heavy cloud LLMs for anonymized reasoning).
  - Custom local medical preprocessors (MONAI for 3D DICOM MRI slice selection; trained YOLOv8 or Vision Transformers on open datasets like DeepLesion or microscopy blood smears for hallucination-free metrics).
  - Full automated `pytest` coverage to prove senior production rigor.
