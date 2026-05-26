@echo off
echo Установка зависимостей для MINIR Термокамера - Контроллер...
pip install -r requirements.txt

if errorlevel 1 (
  echo Произошла ошибка при установке зависимостей
  echo Убедитесь, что Python и pip установлены в системе
  pause
  exit /b 1
)

echo.
echo Установка завершена успешно!
echo.
echo Для запуска приложения используйте:
echo   python main_pyqt_claude.py
echo.
echo Также доступны кроссплатформенные скрипты:
echo   python launch_crossplatform.py - универсальный запуск
echo   python install_crossplatform.py - универсальная установка
echo.
pause