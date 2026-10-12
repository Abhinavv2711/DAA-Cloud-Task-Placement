@echo off
title Cloud Task Placement Dashboard
echo ========================================================
echo  Launching Cloud Task Placement Optimization Dashboard
echo ========================================================
cd /d "%~dp0"
start "" "http://localhost:8000"
python -m uvicorn api:app --host 0.0.0.0 --port 8000
pause
