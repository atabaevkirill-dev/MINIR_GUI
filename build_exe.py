import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Устанавливает PyInstaller, если он еще не установлен"""
    try:
        import PyInstaller
        print("PyInstaller уже установлен")
    except ImportError:
        print("Устанавливаю PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller успешно установлен")

def build_executable():
    """Собирает исполняемый файл с помощью PyInstaller"""
    print("Начинаю сборку исполняемого файла...")
    
    # Команда для сборки исполняемого файла
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Создать один исполняемый файл
        "--windowed",          # Не показывать консольное окно
        "--name=MINIR_GUI",    # Имя исполняемого файла
        "--add-data=README.md;.",  # Добавляем файлы документации
        "--hidden-import=serial",
        "--hidden-import=serial.tools",
        "--hidden-import=serial.tools.list_ports",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--collect-submodules=serial",
        "--collect-submodules=PyQt6",
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("Исполняемый файл успешно создан!")
        print("Вы можете найти его в папке dist/")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке исполняемого файла: {e}")
        sys.exit(1)

def main():
    """Основная функция для выполнения сборки"""
    print("Установка и сборка исполняемого файла MINIR GUI...")
    
    # Убедиться, что мы в правильной директории
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    install_pyinstaller()
    build_executable()

if __name__ == "__main__":
    main()