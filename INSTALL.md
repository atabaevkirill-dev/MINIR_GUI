# Установка MINIR Термокамера - Контроллер

## Windows

### Установка Python
1. Скачайте Python с [официального сайта](https://www.python.org/downloads/)
2. Убедитесь, что при установке отмечена опция "Add Python to PATH"
3. Перезапустите командную строку после установки

### Установка приложения
1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   python main_pyqt_claude.py
   ```
   или используйте скрипт запуска:
   ```
   launch.bat
   ```

## macOS

### Установка Python
1. Установите Python через Homebrew:
   ```
   brew install python3
   ```
2. Или скачайте с [официального сайта](https://www.python.org/downloads/)

### Установка приложения
1. Установите зависимости:
   ```
   pip3 install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   python3 main_pyqt_claude.py
   ```

## Linux (Ubuntu/Debian)

### Установка Python и зависимостей
1. Установите Python и pip:
   ```
   sudo apt update
   sudo apt install python3 python3-pip python3-dev
   ```
2. Установите системные зависимости для PyQt6:
   ```
   sudo apt install python3-pyqt6
   ```

### Установка приложения
1. Установите зависимости:
   ```
   pip3 install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   python3 main_pyqt_claude.py
   ```

## Linux (CentOS/RHEL/Fedora)

### Установка Python и зависимостей
1. Установите Python и pip:
   ```
   # CentOS/RHEL:
   sudo yum install python3 python3-pip python3-devel
   
   # Fedora:
   sudo dnf install python3 python3-pip python3-devel
   ```
2. Установите системные зависимости для PyQt6:
   ```
   # CentOS/RHEL:
   sudo yum install qt6-qtbase-devel
   
   # Fedora:
   sudo dnf install qt6-qtbase-devel
   ```

### Установка приложения
1. Установите зависимости:
   ```
   pip3 install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   python3 main_pyqt_claude.py
   ```

## Установка через pip (для всех платформ)

Если проект подготовлен для установки как пакет:

1. Установите приложение:
   ```
   pip install .
   ```
   или в режиме разработки:
   ```
   pip install -e .
   ```

2. Запустите приложение:
   ```
   minir-gui
   ```

## Решение проблем

### macOS/Linux: Ошибка доступа к последовательному порту
Добавьте своего пользователя в группу dialout (Linux) или проверьте права доступа к порту:
```
# Linux:
sudo usermod -a -G dialout $USER
# затем перезайдите в систему

# Проверка доступа к порту:
ls -la /dev/tty*
```

### Windows: Ошибка с COM-портом
Убедитесь, что драйверы для вашего RS-232 адаптера установлены правильно.

### Общие проблемы с PyQt6
Если возникают проблемы с отображением интерфейса, попробуйте установить конкретную версию:
```
pip install PyQt6==6.4.0
```