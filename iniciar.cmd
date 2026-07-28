@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente virtual nao encontrado.
    echo Execute primeiro: powershell -ExecutionPolicy Bypass -File scripts\init.ps1
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Meu PDI - servidor local pessoal
echo ==========================================
echo.

".venv\Scripts\python.exe" manage.py migrate --noinput
if errorlevel 1 (
    echo.
    echo Nao foi possivel preparar o banco de dados.
    pause
    exit /b 1
)

echo.
echo Abra no navegador: http://127.0.0.1:8000
echo Para encerrar, pressione Ctrl+C.
echo.
".venv\Scripts\python.exe" manage.py runserver

endlocal
