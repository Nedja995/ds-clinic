# App data drafts

```text
app_data/
├── sessions/
│   ├── _index.json          ← lightweight metadata for listing
│   └── .json    ← full ChatSessionModel
│   └── {session_id}.json    ← full AppSessionModel
├── reports/
│   ├── _index.json
│   └── {report_id}.json     ← full MedicalReport
└── ai_settings/
    ├── ai_settings.json
    ├── models_db.json
    ├── initial_task_descriptions_db.json
    ├── response_recommended_therapy_db.json
    ├── response_critical_findings_db.json
    ├── response_critical_finding_expert_opinion_db.json
    ├── response_critical_finding_param_and_value_db.json   
    ├── gemini/
    │   ├── _index.json
    │   └── {name}.json      ← GeminiModelConfig
    └── claude/
        ├── _index.json
        └── {name}.json      ← ClaudeModelConfig
```
