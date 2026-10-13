@echo off
title Launch Support Ticket Automation
echo ========================================================
echo  Launching Support Ticket Automation System
echo ========================================================
echo.
echo Starting Backend API Server (Port 8000)...
start "Backend (FastAPI)" cmd /k "%~dp0start_backend.bat"

timeout /t 3 /nobreak > nul

echo Starting Frontend Dev Server (Port 5173)...
start "Frontend (React Vite)" cmd /k "%~dp0start_frontend.bat"

echo.
echo ========================================================
echo  Both services have been started!
echo.
echo  - Frontend Dashboard: http://localhost:5173
echo  - Backend API:        http://127.0.0.1:8000
echo  - Swagger Docs:       http://127.0.0.1:8000/docs
echo  - Health Check:       http://127.0.0.1:8000/health
echo ========================================================
echo.
pause
