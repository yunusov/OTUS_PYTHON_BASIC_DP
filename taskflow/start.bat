@echo off
@chcp 65001 > nul
echo Проверка Python...

python --version > nul 2>&1
if errorlevel 1 (
    echo Ошибка: Python не установлен или не добавлен в PATH
    echo Скачайте с https://python.org
    pause
    exit /b 1
)

echo Проверка UV...
uv --version > nul 2>&1
if errorlevel 1 (
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
)

@rem Используем локальную .venv
set UV_PROJECT_ENVIRONMENT=.venv
uv run main.py
