# Support Ticket Automation System - PowerShell Launcher
$rootDir = $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Launching Support Ticket Automation System" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# Start Backend
Write-Host "`n[1/2] Starting Backend API Server (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\backend'; .\venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend Vite Server (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\frontend'; npm run dev"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host " Both servers launched successfully!" -ForegroundColor Green
Write-Host " - Frontend UI:   http://localhost:5173" -ForegroundColor White
Write-Host " - Backend API:   http://127.0.0.1:8000" -ForegroundColor White
Write-Host " - Swagger Docs:  http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " - Health Check:  http://127.0.0.1:8000/health" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
