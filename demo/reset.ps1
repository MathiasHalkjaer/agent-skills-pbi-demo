# Jump to a demo stage, discarding any changes made during the demo.
# Usage, from any folder: powershell -File <demo project>\demo\reset.ps1 stage-3
param([Parameter(Mandatory = $true)][string]$Stage)
Set-Location (Split-Path $PSScriptRoot -Parent)
git rev-parse -q --verify "refs/tags/$Stage" | Out-Null
if ($LASTEXITCODE -ne 0) { Write-Host "No such stage: $Stage" -ForegroundColor Red; exit 1 }
git checkout -q -f $Stage
git clean -fdq -e .claude/settings.local.json
Write-Host "At $Stage. Close and reopen Sales.pbip in Power BI Desktop to see the model as it is now." -ForegroundColor Green
