@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo [1/3] Обновление данных панели мониторинга...
python generate_panel.py

echo [2/3] Запуск локальной панели управления...
start "" "%~dp0Панель.html"

echo [3/3] Открытие главного производственного руководства...
start "" "%~dp0GEMINI_SEO_MACHINE_PRO.md"

exit
