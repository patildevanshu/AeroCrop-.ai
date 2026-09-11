@echo off
title AeroCrop.ai Platform Launcher
cd /d "%~dp0"

echo ========================================================
echo          AeroCrop.ai - Agricultural Intelligence
echo ========================================================
echo.
echo 1. Starting Email Microservice (:5000)...
start "AeroCrop Email (:5000)" cmd /k "cd backend\email_service && node server.js"

echo 2. Starting Validator Microservice (:5005)...
start "AeroCrop Validator (:5005)" cmd /k "python validator_service\server.py"

echo 3. Starting Backend API (:8000)...
start "AeroCrop Backend (:8000)" cmd /k "python main.py"

echo 4. Starting Frontend UI (:3000)...
start "AeroCrop Frontend (:3000)" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo All 4 services have been launched in dedicated windows:
echo.
echo - Web Dashboard : http://localhost:3000
echo - Backend API   : http://localhost:8000
echo - Email Service : http://localhost:5000
echo - Validator     : http://localhost:5005
echo ========================================================
echo.
ping 127.0.0.1 -n 3 >nul
