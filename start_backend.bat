@echo off
title Support Ticket Backend (FastAPI)
echo ========================================================
echo  Starting Backend API Server...
echo ========================================================
cd /d "%~dp0backend"
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found at backend\venv!
)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
