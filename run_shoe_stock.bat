@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Starting Shoe Stock App...
start "" "http://127.0.0.1:8765"
python "shoe_stock_app\app.py"

pause
