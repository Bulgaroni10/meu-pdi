param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile
)

$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"
$resolvedBackup = (Resolve-Path -LiteralPath $BackupFile).Path

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Ambiente virtual não encontrado. Execute .\scripts\init.ps1."
}

Set-Location -LiteralPath $projectRoot
& $pythonPath manage.py migrate

$userCount = & $pythonPath manage.py shell -c "from usuarios.models import Usuario; print(Usuario.objects.count())"
if ([int]$userCount -gt 0) {
    throw "Restauração recusada: o banco já contém usuários. Use um banco vazio."
}

& $pythonPath manage.py loaddata $resolvedBackup
if ($LASTEXITCODE -ne 0) {
    throw "A restauração não foi concluída."
}

Write-Host "Backup restaurado com sucesso."
