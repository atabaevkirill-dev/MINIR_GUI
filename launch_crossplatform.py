#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кроссплатформенный скрипт запуска MINIR Термокамера - Контроллер
Поддерживает Windows, macOS и Linux
"""

import sys
import os
import platform
import subprocess


def main():
    print(f"Запуск MINIR Термокамера - Контроллер")
    print(f"Операционная система: {platform.system()} {platform.release()}")
    
    # Определяем имя файла основного приложения
    main_app_file = "main.py"
    
    # Проверяем существование файла
    if not os.path.exists(main_app_file):
        print(f"Ошибка: файл {main_app_file} не найден!")
        input("Нажмите Enter для выхода...")
        return
    
    try:
        # Запускаем основное приложение
        result = subprocess.run([sys.executable, main_app_file], check=True)
        print("Приложение завершено")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при запуске приложения: {e}")
    except FileNotFoundError:
        print("Ошибка: Python не найден в системе")
        print("Убедитесь, что Python установлен и добавлен в PATH")
    except KeyboardInterrupt:
        print("\nЗапуск прерван пользователем")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
    
    input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()