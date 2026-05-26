#!/bin/bash
# -*- coding: utf-8 -*-
#
# Скрипт запуска MINIR Термокамера - Контроллер для Linux/macOS
#

echo "Запуск MINIR Термокамера - Контроллер"
echo "Операционная система: $(uname -s) $(uname -r)"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "Ошибка: python3 не найден в системе"
    echo "Установите Python 3.6 или выше"
    exit 1
fi

# Проверяем наличие основного файла приложения
if [ ! -f "main.py" ]; then
    echo "Ошибка: файл main_pyqt_claude.py не найден!"
    exit 1
fi

# Запускаем приложение
echo "Запуск приложения..."
python3 main.py

# Проверяем результат
if [ $? -eq 0 ]; then
    echo "Приложение завершено успешно"
else
    echo "Приложение завершено с ошибкой"
fi