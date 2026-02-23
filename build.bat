@echo off
chcp 65001
echo Установка зависимостей...
pip install -r requirements.txt

echo Очистка предыдущих сборок...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q __pycache__ 2>nul

echo Сборка голосового помощника Кеша...
pyinstaller --onefile --windowed --icon=Kesha_icoc.jpeg --name "KeshaAssistant" --add-data "Kesha.py;." --add-data "gig.py;." --add-data "games/*.py;games/" --add-data "Media/*;Media/" --add-data "Kesha_icoc.jpeg;." --clean main.py

echo.
echo ====================================
echo ГОТОВО! Ваше приложение: dist\KeshaAssistant.exe
echo ====================================
echo.
pause