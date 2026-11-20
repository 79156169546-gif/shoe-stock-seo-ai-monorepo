@echo off
chcp 65001 >nul
cd /d "%~dp0gemini_seo_machine"

echo [1/3] Обновление данных панели мониторинга...
python generate_panel.py

echo [2/3] Запуск локальной панели управления...
start "" "%~dp0gemini_seo_machine\Панель.html"

echo [3/3] Открытие главного руководства...
start "" "%~dp0gemini_seo_machine\GEMINI_SEO_MACHINE_PRO.md"

exit
