@echo off
chcp 65001 >nul
cd /d "%~dp0shoe_stock_avito_ai"

echo [1/2] Открытие браузера http://127.0.0.1:8765...
start "" "http://127.0.0.1:8765"

echo [2/2] Запуск сервера Shoe Stock & Avito AI Machine...
python app.py
pause
