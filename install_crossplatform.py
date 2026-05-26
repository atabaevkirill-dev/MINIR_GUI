#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Кроссплатформенный скрипт установки зависимостей для MINIR Термокамера - Контроллер
Поддерживает Windows, macOS и Linux
"""

import sys
import os
import platform
import subprocess
import argparse


def install_dependencies():
    """Установка зависимостей через pip"""
    print("Установка зависимостей для MINIR Термокамера - Контроллер...")
    
    try:
        # Проверяем наличие requirements.txt
        if not os.path.exists("requirements.txt"):
            print("Файл requirements.txt не найден! Создаем стандартный...")
            with open("requirements.txt", "w") as f:
                f.write("pyserial>=3.5\nPyQt6>=6.4.0\n")
        
        # Устанавливаем зависимости
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              check=True, capture_output=True, text=True)
        print("Зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e}")
        print("Попробуйте установить вручную: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False


def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 6):
        print(f"Ошибка: Требуется Python 3.6 или выше. У вас: {sys.version}")
        return False
    else:
        print(f"Python версия: {sys.version}")
        return True


def main():
    parser = argparse.ArgumentParser(description='Установка зависимостей для MINIR Термокамера - Контроллер')
    parser.add_argument('--skip-python-check', action='store_true', 
                       help='Пропустить проверку версии Python')
    
    args = parser.parse_args()
    
    print(f"Операционная система: {platform.system()} {platform.release()}")
    print(f"Архитектура: {platform.machine()}")
    
    if not args.skip_python_check:
        if not check_python_version():
            input("Нажмите Enter для выхода...")
            return
    
    if install_dependencies():
        print("\nУстановка завершена успешно!")
        print("Теперь вы можете запустить приложение:")
        print("  python main_pyqt_claude.py")
        print("или")
        print("  python launch_crossplatform.py")
    else:
        print("\nУстановка завершена с ошибками!")
    
    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()