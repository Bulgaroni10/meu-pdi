$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$backupDir = Join-Path $projectRoot "backups"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Ambiente virtual não encontrado. Execute .\scripts\init.ps1."
}

if (-not (Test-Path -LiteralPath $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$backupFile = Join-Path $backupDir "meu-pdi-$timestamp.json"

Set-Location -LiteralPath $projectRoot
& $pythonPath manage.py dumpdata `
    --natural-foreign `
    --natural-primary `
    --exclude auth.permission `
    --exclude contenttypes `
    --exclude admin.logentry `
    --exclude sessions.session `
    --indent 2 `
    --output $backupFile

if ($LASTEXITCODE -ne 0) {
    throw "O backup não foi concluído."
}

Write-Host "Backup criado em $backupFile"
Write-Host "Copie media/ separadamente quando houver uploads."
