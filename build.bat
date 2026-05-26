@echo off
echo Начинаю сборку исполняемого файла MINIR GUI...
echo.

REM Переходим в директорию скрипта
cd /d "%~dp0"

REM Запускаем скрипт сборки
python build_exe.py

echo.
echo Сборка завершена!
pause