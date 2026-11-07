# Agent skills for Power BI: demo project

The demo project for the session **Advanced Agent Skills for Power BI**. A small, messy Sales
model in PBIP format, and a skill that cleans it up, built one piece per git tag.

- **Slides:** https://mathiashalkjaer.github.io/Presentations/advanced-agent-skills-for-power-bi/
- **Field guide:** https://mathiashalkjaer.github.io/Presentations/advanced-agent-skills-for-power-bi/guide/

Every demo slide has the full steps and prompts for that demo: press **D** to show them.

## Get started

```
git clone https://github.com/MathiasHalkjaer/agent-skills-pbi-demo
cd agent-skills-pbi-demo
powershell -File demo\reset.ps1 stage-0
```

Then open `Sales.pbip` in Power BI Desktop and the folder in VS Code with Claude Code.
The model's data is inline, so it refreshes without a data source.

## The stages

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

Jump to a stage, throwing away any changes: `powershell -File demo\reset.ps1 stage-3`.
It works from any folder.

`tools/build_model.py` regenerates the messy or clean model from one definition.

## Good to know

- The production hook in demo 4 needs the Power BI modelling MCP server added to Claude
  Code under the name `powerbi-modeling`. Every other demo works on the files alone.
- The hook and sub-agent setup (`.claude/settings.json`, `.claude/agents/`) is Claude Code's.
  The skill folder itself follows the open Agent Skills standard.
