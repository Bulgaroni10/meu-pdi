$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$venvPath = Join-Path $projectRoot ".venv"
$envExample = Join-Path $projectRoot ".env.example"
$envFile = Join-Path $projectRoot ".env"

Set-Location -LiteralPath $projectRoot

if (-not (Test-Path -LiteralPath $venvPath)) {
    python -m venv $venvPath
}

$pythonPath = Join-Path $venvPath "Scripts\python.exe"
& $pythonPath -m pip install --upgrade pip
& $pythonPath -m pip install -r (Join-Path $projectRoot "requirements.txt")

if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath $envExample -Destination $envFile
    Write-Host "Arquivo .env criado a partir de .env.example."
}

& $pythonPath manage.py migrate
& $pythonPath manage.py check

Write-Host "Fundação pronta. Inicie com dois cliques em iniciar.cmd."
