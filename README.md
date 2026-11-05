# Agent skills for Power BI: demo project

The demo for the session "Advanced Agent Skills for Power BI". A small, messy Sales model in
PBIP format, and the skill setup from the field guide, added one piece per git tag.

| Tag | What it adds |
|---|---|
| `stage-0` | The messy model, no skills |
| `stage-1` | model-standards with a vague description |
| `stage-2` | A sharp description, the rules, and reference files |
| `stage-3` | The check script, and "Before you finish" |
| `stage-4` | Hooks: no production, and a name check after every edit |
| `stage-5` | The table-documenter sub-agent |
| `stage-6` | The learning section, "After each task" |
| `fallback-clean` | stage-6 with the model already cleaned up |

Jump to a stage, throwing away any changes: `powershell -File demo/reset.ps1 stage-3`

The model's data is inline, so it refreshes without a data source. `tools/build_model.py`
regenerates the messy or clean model from one definition.

The run sheet with prompts and timings is in the MVP repo:
`speaking/advanced-agent-skills/demo-script.md`.
