@echo off
cd /d %~dp0
start "NEEMUS Detector" cmd /k python src\inference\run_inference.py
start "NEEMUS Dashboard" cmd /k python -m src.dashboard.app --config config/default.yaml
timeout /t 4 /nobreak >nul
start http://localhost:5000