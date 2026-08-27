@echo off
title Apex College AI - RAG Assistant
echo =========================================================
echo    Apex College AI - RAG Knowledge Assistant
echo =========================================================
echo.

IF NOT EXIST "venv" (
    echo [INFO] Virtual environment not found. Creating venv...
    python -m venv venv
    echo [INFO] Installing required dependencies...
    call venv\Scripts\python -m pip install --upgrade pip
    call venv\Scripts\pip install -r backend\requirements.txt
)

echo [INFO] Starting Application...
call venv\Scripts\python run.py
pause
