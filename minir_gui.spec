# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Получаем путь к текущему каталогу проекта
PROJECT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=[
        # Если есть какие-то данные или ресурсы, которые нужно включить
        # ('path/to/resource', 'resource'),
    ],
    hiddenimports=[
        # Список модулей, которые могут быть импортированы динамически
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MINIR_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Установите в True, если хотите видеть консоль при запуске
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Укажите путь к иконке, если есть
)