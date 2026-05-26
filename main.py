import sys
import os
import platform
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QGroupBox, QPushButton, QSlider, QLabel, QComboBox, 
                             QTextEdit, QTabWidget, QFrame, QSplitter, QStatusBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import List


def get_serial_ports():
    """Получение списка доступных COM-портов"""
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append(port.device)
    return ports


class VSCodeDarkTheme:
    """Тема в стиле Visual Studio Code Dark"""
    BACKGROUND = "#1e1e1e"
    PANEL_BACKGROUND = "#252526"
    ACCENT = "#007acc"
    TEXT = "#d4d4d4"
    TEXT_SECONDARY = "#9e9e9e"
    BORDER = "#3c3c3c"
    HIGHLIGHT = "#2a2d2e"
    WARNING = "#ffcc00"
    ERROR = "#f48771"


class ThermalCameraController:
    """Класс для управления тепловизионной камерой MINIR по протоколу RS-232"""
    
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        
        # Определение команд по протоколу
        self.commands = {
            'shutter_close': [0xF0, 0x02, 0x26, 0x40, 0x66, 0xFF],
            'shutter_open': [0xF0, 0x02, 0x26, 0x41, 0x67, 0xFF],
            'reset': [0xF0, 0x02, 0x26, 0x80, 0xA6, 0xFF],
            'save_parameter': [0xF0, 0x02, 0x26, 0x81, 0xA7, 0xFF],
            'manual_calibration': [0xF0, 0x02, 0x26, 0x03, 0x29, 0xFF],
            'background_calibration': [0xF0, 0x02, 0x26, 0x02, 0x28, 0xFF],
            'auto_calibration_on': [0xF0, 0x03, 0x26, 0x07, 0x0F, 0x3C, 0xFF],
            'auto_calibration_off': [0xF0, 0x03, 0x26, 0x07, 0x00, 0x2D, 0xFF],
            'open_cross_on': [0xF0, 0x03, 0x26, 0x04, 0x0F, 0x39, 0xFF],
            'open_cross_off': [0xF0, 0x03, 0x26, 0x04, 0x00, 0x2A, 0xFF],
            'time_domain_filter_on': [0xF0, 0x03, 0x26, 0x0D, 0x00, 0x33, 0xFF],
            'time_domain_filter_off': [0xF0, 0x03, 0x26, 0x0D, 0x0F, 0x42, 0xFF],
            'image_enhance_on': [0xF0, 0x03, 0x26, 0x0E, 0x0F, 0x43, 0xFF],
            'image_enhance_off': [0xF0, 0x03, 0x26, 0x0E, 0x00, 0x34, 0xFF],
            'white_hot_on': [0xF0, 0x03, 0x26, 0x05, 0x00, 0x2B, 0xFF],
            'white_hot_off': [0xF0, 0x03, 0x26, 0x05, 0x0F, 0x3A, 0xFF],
            'agc_on': [0xF0, 0x03, 0x26, 0x13, 0x03, 0x3C, 0xFF],   # agc on(√)
            'agc_off': [0xF0, 0x03, 0x26, 0x13, 0x01, 0x3A, 0xFF],  # agc on()
            'two_point_calc': [0xF0, 0x02, 0x26, 0x93, 0xB9, 0xFF],
            'two_point_auto_bpr_save': [0xF0, 0x02, 0x26, 0x94, 0xBA, 0xFF],
            'auto_focus': [0xF0, 0x02, 0x26, 0x34, 0x5A, 0xFF],
            'status_inquiry': [0xF0, 0x02, 0x26, 0x00, 0x26, 0xFF],
            'save_calib_data': [0xF0, 0x02, 0x26, 0x3F, 0x5D, 0xFF],
            'manual_bpr_save': [0xF0, 0x04, 0x26, 0x94, 0x37, 0x9D, 0x8E, 0xFF],
            'auto_bpr': [0xF0, 0x05, 0x26, 0x57, 0x64, 0x51, 0x62, 0x94, 0xFF]
        }
        
        # Цветовые палитры
        self.color_palettes = {
            'color0': [0xF0, 0x03, 0x26, 0x32, 0x00, 0x58, 0xFF],
            'color1': [0xF0, 0x03, 0x26, 0x32, 0x01, 0x59, 0xFF],
            'color2': [0xF0, 0x03, 0x26, 0x32, 0x02, 0x5A, 0xFF],
            'color3': [0xF0, 0x03, 0x26, 0x32, 0x03, 0x5B, 0xFF],
            'color4': [0xF0, 0x03, 0x26, 0x32, 0x04, 0x5C, 0xFF],
            'color5': [0xF0, 0x03, 0x26, 0x32, 0x05, 0x5D, 0xFF],
            'color6': [0xF0, 0x03, 0x26, 0x32, 0x06, 0x5E, 0xFF],
            'color7': [0xF0, 0x03, 0x26, 0x32, 0x07, 0x5F, 0xFF],
            'color8': [0xF0, 0x03, 0x26, 0x32, 0x08, 0x60, 0xFF],
            'color9': [0xF0, 0x03, 0x26, 0x32, 0x09, 0x61, 0xFF],
            'color10': [0xF0, 0x03, 0x26, 0x32, 0x0A, 0x62, 0xFF],
            'color11': [0xF0, 0x03, 0x26, 0x32, 0x0B, 0x63, 0xFF]
        }
        
        # Электронный зум
        self.zoom_levels = {
            'zoom_1x': [0xF0, 0x03, 0x26, 0x08, 0x00, 0x2E, 0xFF],
            'zoom_2x': [0xF0, 0x03, 0x26, 0x08, 0x0F, 0x3D, 0xFF],
            'zoom_4x': [0xF0, 0x03, 0x26, 0x08, 0x03, 0x31, 0xFF]
        }
        
        # Режимы изображения
        self.image_modes = {
            'mode_L': [0xF0, 0x03, 0x26, 0x74, 0x00, 0x9A, 0xFF],
            'mode_M': [0xF0, 0x03, 0x26, 0x74, 0x01, 0x9B, 0xFF],
            'mode_H': [0xF0, 0x03, 0x26, 0x74, 0x02, 0x9C, 0xFF]
        }
        
        # Инверсия изображения
        self.flip_modes = {
            'flip_none': [0xF0, 0x03, 0x26, 0x16, 0x00, 0x3C, 0xFF],
            'flip_h': [0xF0, 0x03, 0x26, 0x16, 0x02, 0x3E, 0xFF],
            'flip_v': [0xF0, 0x03, 0x26, 0x16, 0x01, 0x3D, 0xFF],
            'flip_hv': [0xF0, 0x03, 0x26, 0x16, 0x03, 0x3F, 0xFF]
        }
        
        # NUC таблицы
        self.nuc_tables = {
            'nuc_table_0': [0xF0, 0x06, 0x26, 0x57, 0x64, 0x51, 0x61, 0x00, 0x93, 0xFF],
            'nuc_table_1': [0xF0, 0x06, 0x26, 0x57, 0x64, 0x51, 0x61, 0x01, 0x94, 0xFF],
            'nuc_table_2': [0xF0, 0x06, 0x26, 0x57, 0x64, 0x51, 0x61, 0x02, 0x95, 0xFF]
        }
        
        # Гамма-коррекция (0-23)
        self.gamma_values = {}
        for i in range(24):
            cmd = [0xF0, 0x03, 0x26, 0x06, i, 0x2C + i, 0xFF]
            if cmd[5] > 0xFF:
                cmd[5] -= 0x100
            self.gamma_values[f'gamma_{i}'] = cmd
    
    def connect(self, port: str, baudrate: int = 9600) -> bool:
        """Подключение к порту"""
        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключение от порта"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
    
    def send_command(self, command: List[int], log_callback=None) -> bool:
        """Отправка команды в порт"""
        if not self.is_connected or not self.serial_port:
            return False

        try:
            command_bytes = bytearray(command)
            cmd_hex = ' '.join([f'{byte:02X}' for byte in command])
            if log_callback:
                log_callback(f"TX: {cmd_hex}")
            self.serial_port.write(command_bytes)
            return True
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            return False
    
    def calculate_checksum(self, data: List[int]) -> int:
        """Вычисление контрольной суммы от оригинальных (не экранированных) данных"""
        return sum(data) & 0xFF

    @staticmethod
    def escape_byte(byte: int) -> List[int]:
        """Экранирование одного байта согласно протоколу MINIR.

        Специальные байты 0xF0, 0xFF, 0xF5 заменяются двухбайтовой
        последовательностью. Заголовок пакета (F0, len, 26, cmd) и
        конечный байт (FF) экранированию НЕ подлежат — они фиксированы
        и никогда не принимают значения F0/FF/F5.
        """
        if byte == 0xF0:
            return [0xF5, 0x00]
        elif byte == 0xFF:
            return [0xF5, 0x0F]
        elif byte == 0xF5:
            return [0xF5, 0x05]
        return [byte]

    def build_command(self, cmd_byte: int, value_bytes: List[int]) -> List[int]:
        """Сборка команды с правильным экранированием согласно протоколу.

        Алгоритм (подтверждён таблицами протокола):
          1. Данные для контрольной суммы: [0x26, cmd_byte] + value_bytes (оригинальные).
          2. Контрольная сумма считается от этих оригинальных данных.
          3. value_bytes и checksum независимо экранируются при необходимости.
          4. len-байт = len(value_bytes) + 1 (за 0x26) — всегда оригинальная длина,
             не меняется при экранировании.

        Формат пакета: F0 [len] 26 [cmd] [value_escaped...] [checksum_escaped...] FF
        """
        # Шаг 1: оригинальные данные для контрольной суммы
        checksum_data = [0x26, cmd_byte] + value_bytes
        checksum = self.calculate_checksum(checksum_data)

        # Шаг 2: len = количество байт после len-поля до checksum (0x26 + cmd + values)
        pkt_len = 1 + 1 + len(value_bytes)  # 0x26, cmd_byte, value_bytes

        # Шаг 3: экранируем только value_bytes и checksum
        escaped_values: List[int] = []
        for b in value_bytes:
            escaped_values.extend(self.escape_byte(b))
        escaped_checksum = self.escape_byte(checksum)

        return [0xF0, pkt_len, 0x26, cmd_byte] + escaped_values + escaped_checksum + [0xFF]

    def create_brightness_command(self, value: int) -> List[int]:
        """Создание команды для установки яркости (0-255).
        Формат: F0 03 26 0A [value_esc] [checksum_esc] FF
        """
        if value < 0 or value > 255:
            raise ValueError("Яркость должна быть в диапазоне 0-255")
        return self.build_command(0x0A, [value])

    def create_gain_command(self, value: int) -> List[int]:
        """Создание команды для установки усиления (0-255).
        Формат: F0 03 26 09 [value_esc] [checksum_esc] FF
        """
        if value < 0 or value > 255:
            raise ValueError("Усиление должно быть в диапазоне 0-255")
        return self.build_command(0x09, [value])

    def create_dde_command(self, value: int) -> List[int]:
        """Создание команды для установки DDE (0-255).
        Формат: F0 03 26 77 [value_esc] [checksum_esc] FF
        """
        if value < 0 or value > 255:
            raise ValueError("DDE должно быть в диапазоне 0-255")
        return self.build_command(0x77, [value])

    def create_filter_command(self, value: int) -> List[int]:
        """Создание команды для установки Spatial Filter (0-255).
        Формат: F0 03 26 78 [value_esc] [checksum_esc] FF
        """
        if value < 0 or value > 255:
            raise ValueError("Фильтр должен быть в диапазоне 0-255")
        return self.build_command(0x78, [value])

    def create_cross_x_command(self, value: int) -> List[int]:
        """Создание команды для установки координаты X перекрестия (0-701).
        Формат: F0 04 26 0B [low_esc] [high_esc] [checksum_esc] FF
        low_byte = value & 0xFF, high_byte = value >> 8
        """
        if value < 0 or value > 701:
            raise ValueError("Координата X должна быть в диапазоне 0-701")
        low_byte = value & 0xFF
        high_byte = (value >> 8) & 0xFF
        return self.build_command(0x0B, [low_byte, high_byte])

    def create_cross_y_command(self, value: int) -> List[int]:
        """Создание команды для установки координаты Y перекрестия (0-575).
        Формат: F0 04 26 0C [low_esc] [high_esc] [checksum_esc] FF
        low_byte = value & 0xFF, high_byte = value >> 8
        """
        if value < 0 or value > 575:
            raise ValueError("Координата Y должна быть в диапазоне 0-575")
        low_byte = value & 0xFF
        high_byte = (value >> 8) & 0xFF
        return self.build_command(0x0C, [low_byte, high_byte])


class ConnectionPanel(QWidget):
    """Панель подключения к термокамере"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # Порт
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Порт:"))
        self.port_combo = QComboBox()
        self.update_ports()
        port_layout.addWidget(self.port_combo)
        
        # Кнопка обновления портов
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.update_ports)
        port_layout.addWidget(self.refresh_btn)
        
        # Скорость
        baudrate_layout = QHBoxLayout()
        baudrate_layout.addWidget(QLabel("Скорость:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200"])
        self.baudrate_combo.setCurrentText("9600")
        baudrate_layout.addWidget(self.baudrate_combo)
        
        # Кнопка подключения
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VSCodeDarkTheme.ACCENT};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #005a9e;
            }}
        """)
        baudrate_layout.addWidget(self.connect_btn)
        
        layout.addLayout(port_layout)
        layout.addStretch()
        layout.addLayout(baudrate_layout)
        
    def update_ports(self):
        """Обновление списка доступных портов"""
        self.port_combo.clear()
        ports = get_serial_ports()
        self.port_combo.addItems(ports)


class ControlTab(QWidget):
    """Базовый класс для вкладок управления"""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
    
    def create_button_with_style(self, text, handler):
        """Создание кнопки с темным стилем"""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {VSCodeDarkTheme.HIGHLIGHT};
                color: {VSCodeDarkTheme.TEXT};
                border: 1px solid {VSCodeDarkTheme.BORDER};
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #3a3d3f;
            }}
        """)
        btn.clicked.connect(handler)
        return btn

    def send_command_safe(self, command_key, display_name):
        """Безопасная отправка команды — ищет по всем словарям контроллера"""
        try:
            c = self.controller
            for table in (c.commands, c.color_palettes, c.zoom_levels,
                          c.image_modes, c.flip_modes, c.nuc_tables, c.gamma_values):
                if command_key in table:
                    c.send_command(table[command_key], lambda msg: print(msg))
                    return
            print(f"Команда '{command_key}' не найдена")
        except Exception as e:
            print(f"Ошибка при отправке команды '{display_name}': {e}")


class BasicControlsTab(ControlTab):
    """Вкладка базового управления"""
    
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        self.init_ui()
    
    def init_ui(self):
        # Шторка
        shutter_group = QGroupBox("Шторка")
        shutter_layout = QHBoxLayout()
        shutter_layout.addWidget(self.create_button_with_style("Открыть шторку", self.open_shutter))
        shutter_layout.addWidget(self.create_button_with_style("Закрыть шторку", self.close_shutter))
        shutter_group.setLayout(shutter_layout)
        self.layout.addWidget(shutter_group)
        
        # Калибровка
        calib_group = QGroupBox("Калибровка")
        calib_layout = QHBoxLayout()
        calib_layout.addWidget(self.create_button_with_style("Ручная калибровка", self.manual_calibration))
        calib_layout.addWidget(self.create_button_with_style("Фоновая калибровка", self.background_calibration))
        calib_layout.addWidget(self.create_button_with_style("Авто калибровка ON", self.auto_calibration_on))
        calib_layout.addWidget(self.create_button_with_style("Авто калибровка OFF", self.auto_calibration_off))
        calib_group.setLayout(calib_layout)
        self.layout.addWidget(calib_group)
        
        # Сброс и сохранение
        reset_group = QGroupBox("Сброс и сохранение")
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(self.create_button_with_style("Сброс", self.reset))
        reset_layout.addWidget(self.create_button_with_style("Сохранить параметры", self.save_parameters))
        reset_layout.addWidget(self.create_button_with_style("Сохранить Calib.data", self.save_calib_data))
        reset_group.setLayout(reset_layout)
        self.layout.addWidget(reset_group)
        
        self.layout.addStretch()
    
    def open_shutter(self):
        self.send_command_safe('shutter_open', 'shutter_open')
    
    def close_shutter(self):
        self.send_command_safe('shutter_close', 'shutter_close')
    
    def manual_calibration(self):
        self.send_command_safe('manual_calibration', 'manual_calibration')
    
    def background_calibration(self):
        self.send_command_safe('background_calibration', 'background_calibration')
    
    def auto_calibration_on(self):
        self.send_command_safe('auto_calibration_on', 'auto_calibration_on')
    
    def auto_calibration_off(self):
        self.send_command_safe('auto_calibration_off', 'auto_calibration_off')
    
    def reset(self):
        self.send_command_safe('reset', 'reset')
    
    def save_parameters(self):
        self.send_command_safe('save_parameter', 'save_parameter')
    
    def save_calib_data(self):
        self.send_command_safe('save_calib_data', 'save_calib_data')


class ImageControlsTab(ControlTab):
    """Вкладка управления изображением"""
    
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        self.init_ui()
    
    def init_ui(self):
        # Яркость
        brightness_group = QGroupBox("Яркость")
        brightness_layout = QVBoxLayout()
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 255)
        self.brightness_slider.setValue(128)
        self.brightness_label = QLabel("128")
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_label)
        brightness_group.setLayout(brightness_layout)
        self.layout.addWidget(brightness_group)
        
        # Усиление
        gain_group = QGroupBox("Усиление")
        gain_layout = QVBoxLayout()
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setRange(0, 255)
        self.gain_slider.setValue(128)
        self.gain_label = QLabel("128")
        self.gain_slider.valueChanged.connect(self.on_gain_changed)
        gain_layout.addWidget(self.gain_slider)
        gain_layout.addWidget(self.gain_label)
        gain_group.setLayout(gain_layout)
        self.layout.addWidget(gain_group)
        
        # DDE
        dde_group = QGroupBox("DDE (Dynamic Differential Enhancement)")
        dde_layout = QVBoxLayout()
        self.dde_slider = QSlider(Qt.Orientation.Horizontal)
        self.dde_slider.setRange(0, 255)
        self.dde_slider.setValue(128)
        self.dde_label = QLabel("128")
        self.dde_slider.valueChanged.connect(self.on_dde_changed)
        dde_layout.addWidget(self.dde_slider)
        dde_layout.addWidget(self.dde_label)
        dde_group.setLayout(dde_layout)
        self.layout.addWidget(dde_group)
        
        # Spatial Filter
        filter_group = QGroupBox("Пространственный фильтр")
        filter_layout = QVBoxLayout()
        self.filter_slider = QSlider(Qt.Orientation.Horizontal)
        self.filter_slider.setRange(0, 255)
        self.filter_slider.setValue(128)
        self.filter_label = QLabel("128")
        self.filter_slider.valueChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_slider)
        filter_layout.addWidget(self.filter_label)
        filter_group.setLayout(filter_layout)
        self.layout.addWidget(filter_group)
        
        # Перекрестие
        cross_group = QGroupBox("Перекрестие")
        cross_layout = QGridLayout()
        
        # X
        cross_layout.addWidget(QLabel("X:"), 0, 0)
        self.cross_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.cross_x_slider.setRange(0, 701)
        self.cross_x_slider.setValue(320)
        self.cross_x_label = QLabel("320")
        cross_layout.addWidget(self.cross_x_slider, 0, 1)
        cross_layout.addWidget(self.cross_x_label, 0, 2)
        self.cross_x_slider.valueChanged.connect(self.on_cross_x_changed)
        
        # Y
        cross_layout.addWidget(QLabel("Y:"), 1, 0)
        self.cross_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.cross_y_slider.setRange(0, 575)
        self.cross_y_slider.setValue(240)
        self.cross_y_label = QLabel("240")
        cross_layout.addWidget(self.cross_y_slider, 1, 1)
        cross_layout.addWidget(self.cross_y_label, 1, 2)
        self.cross_y_slider.valueChanged.connect(self.on_cross_y_changed)
        
        cross_group.setLayout(cross_layout)
        self.layout.addWidget(cross_group)
        
        self.layout.addStretch()
    
    def on_brightness_changed(self, value):
        self.brightness_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_brightness_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")
    
    def on_gain_changed(self, value):
        self.gain_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_gain_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")
    
    def on_dde_changed(self, value):
        self.dde_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_dde_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")
    
    def on_filter_changed(self, value):
        self.filter_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_filter_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")
    
    def on_cross_x_changed(self, value):
        self.cross_x_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_cross_x_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")
    
    def on_cross_y_changed(self, value):
        self.cross_y_label.setText(str(value))
        if self.controller.is_connected:
            try:
                command = self.controller.create_cross_y_command(value)
                self.controller.send_command(command, lambda msg: print(msg))
            except ValueError as e:
                print(f"Ошибка: {e}")


class AdvancedControlsTab(ControlTab):
    """Вкладка расширенного управления"""
    
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        self.init_ui()
    
    def init_ui(self):
        # Цветовые палитры
        palette_group = QGroupBox("Цветовые палитры")
        palette_layout = QGridLayout()
        
        palettes = [
            ("Color 0", "color0"), ("Color 1", "color1"), ("Color 2", "color2"),
            ("Color 3", "color3"), ("Color 4", "color4"), ("Color 5", "color5"),
            ("Color 6", "color6"), ("Color 7", "color7"), ("Color 8", "color8"),
            ("Color 9", "color9"), ("Color 10", "color10"), ("Color 11", "color11")
        ]
        
        for i, (label, cmd_key) in enumerate(palettes):
            row = i // 4
            col = i % 4
            btn = self.create_button_with_style(label, lambda checked, k=cmd_key: self.send_palette_command(k))
            palette_layout.addWidget(btn, row, col)
        
        palette_group.setLayout(palette_layout)
        self.layout.addWidget(palette_group)
        
        # Зум
        zoom_group = QGroupBox("Электронный зум")
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.create_button_with_style("1x", self.zoom_1x))
        zoom_layout.addWidget(self.create_button_with_style("2x", self.zoom_2x))
        zoom_layout.addWidget(self.create_button_with_style("4x", self.zoom_4x))
        zoom_group.setLayout(zoom_layout)
        self.layout.addWidget(zoom_group)
        
        # Режимы изображения
        mode_group = QGroupBox("Режимы изображения")
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.create_button_with_style("L", self.mode_L))
        mode_layout.addWidget(self.create_button_with_style("M", self.mode_M))
        mode_layout.addWidget(self.create_button_with_style("H", self.mode_H))
        mode_group.setLayout(mode_layout)
        self.layout.addWidget(mode_group)
        
        # Инверсия
        flip_group = QGroupBox("Инверсия изображения")
        flip_layout = QHBoxLayout()
        flip_layout.addWidget(self.create_button_with_style("Нет", self.flip_none))
        flip_layout.addWidget(self.create_button_with_style("Горизонтально", self.flip_h))
        flip_layout.addWidget(self.create_button_with_style("Вертикально", self.flip_v))
        flip_layout.addWidget(self.create_button_with_style("Оба", self.flip_hv))
        flip_group.setLayout(flip_layout)
        self.layout.addWidget(flip_group)
        
        # Гамма-коррекция
        gamma_group = QGroupBox("Гамма-коррекция")
        gamma_layout = QVBoxLayout()
        self.gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self.gamma_slider.setRange(0, 23)
        self.gamma_slider.setValue(12)
        self.gamma_label = QLabel("12")
        self.gamma_slider.valueChanged.connect(self.on_gamma_changed)
        gamma_layout.addWidget(self.gamma_slider)
        gamma_layout.addWidget(self.gamma_label)
        gamma_group.setLayout(gamma_layout)
        self.layout.addWidget(gamma_group)
        
        # NUC таблицы
        nuc_group = QGroupBox("NUC Таблицы")
        nuc_layout = QHBoxLayout()
        nuc_layout.addWidget(self.create_button_with_style("Таблица 0", self.nuc_table_0))
        nuc_layout.addWidget(self.create_button_with_style("Таблица 1", self.nuc_table_1))
        nuc_layout.addWidget(self.create_button_with_style("Таблица 2", self.nuc_table_2))
        nuc_group.setLayout(nuc_layout)
        self.layout.addWidget(nuc_group)
        
        self.layout.addStretch()
    
    def send_palette_command(self, palette_key):
        """Безопасная отправка команды цветовой палитры"""
        try:
            # Проверяем, что palette_key - строка и имеет правильный формат
            if not isinstance(palette_key, str):
                print(f"Недопустимый тип ключа палитры: {type(palette_key)}, значение: {palette_key}")
                return
            
            if palette_key in self.controller.color_palettes:
                command = self.controller.color_palettes[palette_key]
                self.controller.send_command(command, lambda msg: print(msg))
            else:
                print(f"Цветовая палитра '{palette_key}' не найдена")
        except Exception as e:
            print(f"Ошибка при отправке команды цветовой палитры '{palette_key}': {e}")
    
    def zoom_1x(self):
        self.send_command_safe('zoom_1x', 'zoom_1x')
    
    def zoom_2x(self):
        self.send_command_safe('zoom_2x', 'zoom_2x')
    
    def zoom_4x(self):
        self.send_command_safe('zoom_4x', 'zoom_4x')
    
    def mode_L(self):
        self.send_command_safe('mode_L', 'mode_L')
    
    def mode_M(self):
        self.send_command_safe('mode_M', 'mode_M')
    
    def mode_H(self):
        self.send_command_safe('mode_H', 'mode_H')
    
    def flip_none(self):
        self.send_command_safe('flip_none', 'flip_none')
    
    def flip_h(self):
        self.send_command_safe('flip_h', 'flip_h')
    
    def flip_v(self):
        self.send_command_safe('flip_v', 'flip_v')
    
    def flip_hv(self):
        self.send_command_safe('flip_hv', 'flip_hv')
    
    def on_gamma_changed(self, value):
        self.gamma_label.setText(str(value))
        key = f'gamma_{value}'
        if key in self.controller.gamma_values:
            try:
                self.controller.send_command(self.controller.gamma_values[key], lambda msg: print(msg))
            except Exception as e:
                print(f"Ошибка при отправке команды гаммы '{key}': {e}")
    
    def nuc_table_0(self):
        self.send_command_safe('nuc_table_0', 'nuc_table_0')
    
    def nuc_table_1(self):
        self.send_command_safe('nuc_table_1', 'nuc_table_1')
    
    def nuc_table_2(self):
        self.send_command_safe('nuc_table_2', 'nuc_table_2')


class ManualControlsTab(ControlTab):
    """Вкладка ручного управления"""
    
    def __init__(self, controller, parent=None):
        super().__init__(controller, parent)
        self.init_ui()
    
    def init_ui(self):
        # Переключатели
        switches_group = QGroupBox("Переключатели")
        switches_layout = QGridLayout()
        
        switches_layout.addWidget(self.create_button_with_style("Открыть перекрестие ON", self.open_cross_on), 0, 0)
        switches_layout.addWidget(self.create_button_with_style("Открыть перекрестие OFF", self.open_cross_off), 0, 1)
        switches_layout.addWidget(self.create_button_with_style("Time Domain Filter ON", self.time_domain_filter_on), 1, 0)
        switches_layout.addWidget(self.create_button_with_style("Time Domain Filter OFF", self.time_domain_filter_off), 1, 1)
        switches_layout.addWidget(self.create_button_with_style("Image Enhance ON", self.image_enhance_on), 2, 0)
        switches_layout.addWidget(self.create_button_with_style("Image Enhance OFF", self.image_enhance_off), 2, 1)
        switches_layout.addWidget(self.create_button_with_style("White Hot ON", self.white_hot_on), 3, 0)
        switches_layout.addWidget(self.create_button_with_style("White Hot OFF", self.white_hot_off), 3, 1)
        switches_layout.addWidget(self.create_button_with_style("AGC ON", self.agc_on), 4, 0)
        switches_layout.addWidget(self.create_button_with_style("AGC OFF", self.agc_off), 4, 1)
        
        switches_group.setLayout(switches_layout)
        self.layout.addWidget(switches_group)
        
        # Дополнительные функции
        extra_group = QGroupBox("Дополнительные функции")
        extra_layout = QGridLayout()
        
        extra_layout.addWidget(self.create_button_with_style("Автофокус", self.auto_focus), 0, 0)
        extra_layout.addWidget(self.create_button_with_style("Запрос статуса", self.status_inquiry), 0, 1)
        extra_layout.addWidget(self.create_button_with_style("Two Point Calc", self.two_point_calc), 1, 0)
        extra_layout.addWidget(self.create_button_with_style("Two Point & Auto BPR Save", self.two_point_auto_bpr_save), 1, 1)
        extra_layout.addWidget(self.create_button_with_style("Manual BPR Save", self.manual_bpr_save), 2, 0)
        extra_layout.addWidget(self.create_button_with_style("Auto BPR", self.auto_bpr), 2, 1)
        
        extra_group.setLayout(extra_layout)
        self.layout.addWidget(extra_group)
        
        # Поле для отправки произвольных команд
        custom_group = QGroupBox("Произвольная команда")
        custom_layout = QVBoxLayout()
        custom_layout.addWidget(QLabel("Введите команду в формате hex (через пробел):"))
        self.custom_cmd_input = QTextEdit()
        self.custom_cmd_input.setMaximumHeight(60)
        custom_layout.addWidget(self.custom_cmd_input)
        self.send_custom_btn = self.create_button_with_style("Отправить команду", self.send_custom_command)
        custom_layout.addWidget(self.send_custom_btn)
        custom_group.setLayout(custom_layout)
        self.layout.addWidget(custom_group)
        
        self.layout.addStretch()
    
    def open_cross_on(self):
        self.send_command_safe('open_cross_on', 'open_cross_on')
    
    def open_cross_off(self):
        self.send_command_safe('open_cross_off', 'open_cross_off')
    
    def time_domain_filter_on(self):
        self.send_command_safe('time_domain_filter_on', 'time_domain_filter_on')
    
    def time_domain_filter_off(self):
        self.send_command_safe('time_domain_filter_off', 'time_domain_filter_off')
    
    def image_enhance_on(self):
        self.send_command_safe('image_enhance_on', 'image_enhance_on')
    
    def image_enhance_off(self):
        self.send_command_safe('image_enhance_off', 'image_enhance_off')
    
    def white_hot_on(self):
        self.send_command_safe('white_hot_on', 'white_hot_on')
    
    def white_hot_off(self):
        self.send_command_safe('white_hot_off', 'white_hot_off')
    
    def agc_on(self):
        self.send_command_safe('agc_on', 'agc_on')
    
    def agc_off(self):
        self.send_command_safe('agc_off', 'agc_off')
    
    def auto_focus(self):
        self.send_command_safe('auto_focus', 'auto_focus')
    
    def status_inquiry(self):
        self.send_command_safe('status_inquiry', 'status_inquiry')
    
    def two_point_calc(self):
        self.send_command_safe('two_point_calc', 'two_point_calc')
    
    def two_point_auto_bpr_save(self):
        self.send_command_safe('two_point_auto_bpr_save', 'two_point_auto_bpr_save')
    
    def manual_bpr_save(self):
        self.send_command_safe('manual_bpr_save', 'manual_bpr_save')
    
    def auto_bpr(self):
        self.send_command_safe('auto_bpr', 'auto_bpr')
    
    def send_custom_command(self):
        cmd_text = self.custom_cmd_input.toPlainText().strip()
        if cmd_text:
            try:
                hex_values = [int(x, 16) for x in cmd_text.split()]
                self.controller.send_command(hex_values, lambda msg: print(msg))
            except ValueError:
                print("Неверный формат команды")


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.controller = ThermalCameraController()
        self.init_ui()
        self.apply_theme()
    
    def init_ui(self):
        self.setWindowTitle("MINIR Термокамера - Контроллер")
        self.setGeometry(200, 200, 500, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Панель подключения
        self.connection_panel = ConnectionPanel()
        main_layout.addWidget(self.connection_panel)
        
        # Установка соединений
        self.connection_panel.connect_btn.clicked.connect(self.toggle_connection)
        
        # Вкладки управления
        self.tabs = QTabWidget()
        self.tabs.addTab(BasicControlsTab(self.controller), "Базовое управление")
        self.tabs.addTab(ImageControlsTab(self.controller), "Управление изображением")
        self.tabs.addTab(AdvancedControlsTab(self.controller), "Расширенное управление")
        self.tabs.addTab(ManualControlsTab(self.controller), "Ручное управление")
        
        main_layout.addWidget(self.tabs)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов")
    
    def apply_theme(self):
        """Применение темной темы VS Code"""
        # Установка стилей для всего приложения
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {VSCodeDarkTheme.BACKGROUND};
            }}
            QTabWidget::pane {{
                border: 1px solid {VSCodeDarkTheme.BORDER};
                background-color: {VSCodeDarkTheme.PANEL_BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: {VSCodeDarkTheme.PANEL_BACKGROUND};
                color: {VSCodeDarkTheme.TEXT_SECONDARY};
                padding: 8px;
                border: 1px solid {VSCodeDarkTheme.BORDER};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {VSCodeDarkTheme.BACKGROUND};
                color: {VSCodeDarkTheme.TEXT};
                border-bottom: 2px solid {VSCodeDarkTheme.ACCENT};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {VSCodeDarkTheme.BORDER};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                color: {VSCodeDarkTheme.TEXT};
                background-color: {VSCodeDarkTheme.PANEL_BACKGROUND};
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QLabel {{
                color: {VSCodeDarkTheme.TEXT};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {VSCodeDarkTheme.BORDER};
                height: 6px;
                background: {VSCodeDarkTheme.HIGHLIGHT};
                margin: 2px 0;
            }}
            QSlider::handle:horizontal {{
                background: {VSCodeDarkTheme.ACCENT};
                border: 1px solid {VSCodeDarkTheme.BORDER};
                width: 18px;
                margin: -8px 0;
                border-radius: 3px;
            }}
            QComboBox {{
                background-color: {VSCodeDarkTheme.HIGHLIGHT};
                color: {VSCodeDarkTheme.TEXT};
                border: 1px solid {VSCodeDarkTheme.BORDER};
                padding: 3px 5px;
                border-radius: 3px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {VSCodeDarkTheme.HIGHLIGHT};
                color: {VSCodeDarkTheme.TEXT};
                selection-background-color: {VSCodeDarkTheme.ACCENT};
            }}
            QTextEdit {{
                background-color: {VSCodeDarkTheme.HIGHLIGHT};
                color: {VSCodeDarkTheme.TEXT};
                border: 1px solid {VSCodeDarkTheme.BORDER};
                border-radius: 3px;
            }}
            QStatusBar {{
                background-color: {VSCodeDarkTheme.PANEL_BACKGROUND};
                color: {VSCodeDarkTheme.TEXT};
            }}
        """)
        
        # Установка шрифта
        font = QFont("Consolas", 9)
        self.setFont(font)
    
    def toggle_connection(self):
        """Переключение состояния подключения"""
        if self.controller.is_connected:
            self.controller.disconnect()
            self.connection_panel.connect_btn.setText("Подключить")
            self.status_bar.showMessage("Отключено")
        else:
            port = self.connection_panel.port_combo.currentText()
            baudrate = int(self.connection_panel.baudrate_combo.currentText())
            if self.controller.connect(port, baudrate):
                self.connection_panel.connect_btn.setText("Отключить")
                self.status_bar.showMessage(f"Подключено к {port} на скорости {baudrate} бод")
            else:
                self.status_bar.showMessage(f"Ошибка подключения к {port}")
    


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()