import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
from typing import List, Tuple

class ThermalCameraController:
    """
    Класс для управления тепловизионной камерой MINIR по протоколу RS-232
    """
    
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
            'agc_on': [0xF0, 0x03, 0x26, 0x13, 0x03, 0x3C, 0xFF],
            'agc_off': [0xF0, 0x03, 0x26, 0x13, 0x01, 0x3A, 0xFF],
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
    
    def connect(self, port: str, baudrate: int = 9600) -> bool:  # Changed to 9600
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
            # Преобразуем команду в байты
            command_bytes = bytearray(command)
            
            # Логируем команду перед отправкой
            if log_callback:
                cmd_hex = ' '.join([f'{byte:02X}' for byte in command])
                log_callback(f"Отправка команды: {cmd_hex}")
            
            self.serial_port.write(command_bytes)
            
            # Даем время на выполнение команды
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            if log_callback:
                log_callback(f"Ошибка отправки команды: {e}")
            return False
    
    def calculate_checksum(self, data: List[int]) -> int:
        """Вычисление контрольной суммы"""
        checksum = sum(data) & 0xFF
        return checksum
    
    def create_brightness_command(self, value: int) -> List[int]:
        """Создание команды для установки яркости (0-255)"""
        if value < 0 or value > 255:
            raise ValueError("Яркость должна быть в диапазоне 0-255")
        
        # Формат команды: F0 03 26 0A [значение] [контрольная_сумма] FF
        data = [0x26, 0x0A, value]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x03] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def create_gain_command(self, value: int) -> List[int]:
        """Создание команды для установки усиления (0-255)"""
        if value < 0 or value > 255:
            raise ValueError("Усиление должно быть в диапазоне 0-255")
        
        # Формат команды: F0 03 26 09 [значение] [контрольная_сумма] FF
        data = [0x26, 0x09, value]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x03] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def create_dde_command(self, value: int) -> List[int]:
        """Создание команды для установки DDE (0-255)"""
        if value < 0 or value > 255:
            raise ValueError("DDE должно быть в диапазоне 0-255")
        
        # Формат команды: F0 03 26 77 [значение] [контрольная_сумма] FF
        data = [0x26, 0x77, value]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x03] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def create_filter_command(self, value: int) -> List[int]:
        """Создание команды для установки Spatial Filter (0-255)"""
        if value < 0 or value > 255:
            raise ValueError("Фильтр должен быть в диапазоне 0-255")
        
        # Формат команды: F0 03 26 78 [значение] [контрольная_сумма] FF
        data = [0x26, 0x78, value]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x03] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def create_cross_x_command(self, value: int) -> List[int]:
        """Создание команды для установки координаты X перекрестия (0-701)"""
        if value < 0 or value > 701:
            raise ValueError("Координата X должна быть в диапазоне 0-701")
        
        # Разделяем значение на старший и младший байты
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        
        # Формат команды: F0 04 26 0B [младший_байт] [старший_байт] [контрольная_сумма] FF
        data = [0x26, 0x0B, low_byte, high_byte]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x04] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def create_cross_y_command(self, value: int) -> List[int]:
        """Создание команды для установки координаты Y перекрестия (0-575)"""
        if value < 0 or value > 575:
            raise ValueError("Координата Y должна быть в диапазоне 0-575")
        
        # Разделяем значение на старший и младший байты
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        
        # Формат команды: F0 04 26 0C [младший_байт] [старший_байт] [контрольная_сумма] FF
        data = [0x26, 0x0C, low_byte, high_byte]
        checksum = self.calculate_checksum(data)
        command = [0xF0, 0x04] + data + [checksum, 0xFF]
        
        # Применяем экранирование если необходимо
        return self.escape_command(command)
    
    def escape_command(self, command: List[int]) -> List[int]:
        """Применение экранирования к команде согласно протоколу"""
        # Убираем стартовый и конечный байты для обработки данных
        start_byte = command[0]
        end_byte = command[-1]
        data_part = command[1:-1]  # Все байты между стартом и концом
        
        escaped_data = []
        for byte in data_part:
            if byte == 0xF0:
                escaped_data.extend([0xF5, 0x00])
            elif byte == 0xFF:
                escaped_data.extend([0xF5, 0x0F])
            elif byte == 0xF5:
                escaped_data.extend([0xF5, 0x05])
            else:
                escaped_data.append(byte)
        
        # Пересчитываем контрольную сумму для экранированных данных
        new_checksum = self.calculate_checksum([start_byte, len(escaped_data)] + escaped_data)
        
        # Собираем команду обратно
        result = [start_byte, len(escaped_data)] + escaped_data + [new_checksum, end_byte]
        return result


class ThermalCameraGUI:
    """Графический интерфейс для управления тепловизионной камерой"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MINIR Термокамера - Контроллер")
        self.root.geometry("800x900")
        
        # Настройка весов для изменения размера окон
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.controller = ThermalCameraController()
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Создаем основные фреймы
        connection_frame = ttk.LabelFrame(self.root, text="Подключение", padding=(10, 5))
        connection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        connection_frame.grid_columnconfigure(0, weight=1)
        
        # Панель подключения
        ttk.Label(connection_frame, text="Порт:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar(value="COM1")
        self.port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var, width=15)
        self.port_combo.grid(row=0, column=1, padx=(0, 10))
        
        refresh_btn = ttk.Button(connection_frame, text="Обновить порты", command=self.refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Добавляем выбор скорости передачи
        ttk.Label(connection_frame, text="Скорость:").grid(row=0, column=3, padx=(10, 5))
        self.baudrate_var = tk.StringVar(value="9600")
        self.baudrate_combo = ttk.Combobox(connection_frame, textvariable=self.baudrate_var, width=10, values=["9600", "19200"])
        self.baudrate_combo.grid(row=0, column=4, padx=(0, 10))
        
        self.connect_btn = ttk.Button(connection_frame, text="Подключить", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=5)
        
        # Обновляем список доступных портов
        self.refresh_ports()
        
        # Основная область с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Вкладки
        self.create_basic_controls_tab()
        self.create_image_controls_tab()
        self.create_advanced_controls_tab()
        self.create_manual_controls_tab()
        
        # Логи
        log_frame = ttk.LabelFrame(self.root, text="Лог", padding=(10, 5))
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.root.grid_rowconfigure(2, weight=2)  # Увеличиваем вес для увеличения области логов
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def create_basic_controls_tab(self):
        """Создание вкладки базовых элементов управления"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Базовое управление")
        
        # Шторка
        shutter_frame = ttk.LabelFrame(frame, text="Шторка", padding=(10, 5))
        shutter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(shutter_frame, text="Открыть шторку", command=self.open_shutter).pack(side=tk.LEFT, padx=5)
        ttk.Button(shutter_frame, text="Закрыть шторку", command=self.close_shutter).pack(side=tk.LEFT, padx=5)
        
        # Калибровка
        calib_frame = ttk.LabelFrame(frame, text="Калибровка", padding=(10, 5))
        calib_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(calib_frame, text="Ручная калибровка", command=self.manual_calibration).pack(side=tk.LEFT, padx=5)
        ttk.Button(calib_frame, text="Фоновая калибровка", command=self.background_calibration).pack(side=tk.LEFT, padx=5)
        ttk.Button(calib_frame, text="Авто калибровка ON", command=self.auto_calibration_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(calib_frame, text="Авто калибровка OFF", command=self.auto_calibration_off).pack(side=tk.LEFT, padx=5)
        
        # Сброс и сохранение
        reset_save_frame = ttk.LabelFrame(frame, text="Сброс и сохранение", padding=(10, 5))
        reset_save_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(reset_save_frame, text="Сброс", command=self.reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(reset_save_frame, text="Сохранить параметры", command=self.save_parameters).pack(side=tk.LEFT, padx=5)
        ttk.Button(reset_save_frame, text="Сохранить Calib.data", command=self.save_calib_data).pack(side=tk.LEFT, padx=5)
        
    def create_image_controls_tab(self):
        """Создание вкладки управления изображением"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Управление изображением")
        
        # Яркость
        brightness_frame = ttk.LabelFrame(frame, text="Яркость", padding=(10, 5))
        brightness_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.brightness_var = tk.IntVar(value=128)
        brightness_scale = ttk.Scale(brightness_frame, from_=0, to=255, variable=self.brightness_var, orient=tk.HORIZONTAL)
        brightness_scale.pack(fill=tk.X, padx=5, pady=5)
        
        brightness_label = ttk.Label(brightness_frame, text="128")
        brightness_label.pack()
        
        def update_brightness_label(val):
            brightness_label.config(text=str(int(float(val))))
            self.set_brightness(int(float(val)))
        
        brightness_scale.config(command=update_brightness_label)
        
        # Усиление
        gain_frame = ttk.LabelFrame(frame, text="Усиление", padding=(10, 5))
        gain_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.gain_var = tk.IntVar(value=128)
        gain_scale = ttk.Scale(gain_frame, from_=0, to=255, variable=self.gain_var, orient=tk.HORIZONTAL)
        gain_scale.pack(fill=tk.X, padx=5, pady=5)
        
        gain_label = ttk.Label(gain_frame, text="128")
        gain_label.pack()
        
        def update_gain_label(val):
            gain_label.config(text=str(int(float(val))))
            self.set_gain(int(float(val)))
        
        gain_scale.config(command=update_gain_label)
        
        # DDE
        dde_frame = ttk.LabelFrame(frame, text="DDE (Dynamic Differential Enhancement)", padding=(10, 5))
        dde_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dde_var = tk.IntVar(value=128)
        dde_scale = ttk.Scale(dde_frame, from_=0, to=255, variable=self.dde_var, orient=tk.HORIZONTAL)
        dde_scale.pack(fill=tk.X, padx=5, pady=5)
        
        dde_label = ttk.Label(dde_frame, text="128")
        dde_label.pack()
        
        def update_dde_label(val):
            dde_label.config(text=str(int(float(val))))
            self.set_dde(int(float(val)))
        
        dde_scale.config(command=update_dde_label)
        
        # Spatial Filter
        filter_frame = ttk.LabelFrame(frame, text="Пространственный фильтр", padding=(10, 5))
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.filter_var = tk.IntVar(value=128)
        filter_scale = ttk.Scale(filter_frame, from_=0, to=255, variable=self.filter_var, orient=tk.HORIZONTAL)
        filter_scale.pack(fill=tk.X, padx=5, pady=5)
        
        filter_label = ttk.Label(filter_frame, text="128")
        filter_label.pack()
        
        def update_filter_label(val):
            filter_label.config(text=str(int(float(val))))
            self.set_filter(int(float(val)))
        
        filter_scale.config(command=update_filter_label)
        
        # Перекрестие
        cross_frame = ttk.LabelFrame(frame, text="Перекрестие", padding=(10, 5))
        cross_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Координата X
        x_frame = ttk.Frame(cross_frame)
        x_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(x_frame, text="X:").pack(side=tk.LEFT)
        self.cross_x_var = tk.IntVar(value=320)
        cross_x_scale = ttk.Scale(x_frame, from_=0, to=701, variable=self.cross_x_var, orient=tk.HORIZONTAL)
        cross_x_scale.pack(fill=tk.X, expand=True, padx=5)
        
        cross_x_label = ttk.Label(x_frame, text="320")
        cross_x_label.pack(side=tk.RIGHT)
        
        def update_cross_x_label(val):
            cross_x_label.config(text=str(int(float(val))))
            self.set_cross_x(int(float(val)))
        
        cross_x_scale.config(command=update_cross_x_label)
        
        # Координата Y
        y_frame = ttk.Frame(cross_frame)
        y_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(y_frame, text="Y:").pack(side=tk.LEFT)
        self.cross_y_var = tk.IntVar(value=240)
        cross_y_scale = ttk.Scale(y_frame, from_=0, to=575, variable=self.cross_y_var, orient=tk.HORIZONTAL)
        cross_y_scale.pack(fill=tk.X, expand=True, padx=5)
        
        cross_y_label = ttk.Label(y_frame, text="240")
        cross_y_label.pack(side=tk.RIGHT)
        
        def update_cross_y_label(val):
            cross_y_label.config(text=str(int(float(val))))
            self.set_cross_y(int(float(val)))
        
        cross_y_scale.config(command=update_cross_y_label)
        
    def create_advanced_controls_tab(self):
        """Создание вкладки расширенного управления"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Расширенное управление")
        
        # Цветовые палитры
        palette_frame = ttk.LabelFrame(frame, text="Цветовые палитры", padding=(10, 5))
        palette_frame.pack(fill=tk.X, padx=10, pady=5)
        
        palettes = [
            ("Color 0", "color0"), ("Color 1", "color1"), ("Color 2", "color2"),
            ("Color 3", "color3"), ("Color 4", "color4"), ("Color 5", "color5"),
            ("Color 6", "color6"), ("Color 7", "color7"), ("Color 8", "color8"),
            ("Color 9", "color9"), ("Color 10", "color10"), ("Color 11", "color11")
        ]
        
        for i, (label, cmd_key) in enumerate(palettes):
            if i % 4 == 0:  # Начинаем новую строку каждые 4 кнопки
                row_frame = ttk.Frame(palette_frame)
                row_frame.pack(fill=tk.X, pady=2)
            
            btn = ttk.Button(row_frame, text=label, command=lambda k=cmd_key: self.send_command_by_key(k))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Зум
        zoom_frame = ttk.LabelFrame(frame, text="Электронный зум", padding=(10, 5))
        zoom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(zoom_frame, text="1x", command=self.zoom_1x).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="2x", command=self.zoom_2x).pack(side=tk.LEFT, padx=5)
        ttk.Button(zoom_frame, text="4x", command=self.zoom_4x).pack(side=tk.LEFT, padx=5)
        
        # Режимы изображения
        mode_frame = ttk.LabelFrame(frame, text="Режимы изображения", padding=(10, 5))
        mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(mode_frame, text="L", command=self.mode_L).pack(side=tk.LEFT, padx=5)
        ttk.Button(mode_frame, text="M", command=self.mode_M).pack(side=tk.LEFT, padx=5)
        ttk.Button(mode_frame, text="H", command=self.mode_H).pack(side=tk.LEFT, padx=5)
        
        # Инверсия
        flip_frame = ttk.LabelFrame(frame, text="Инверсия изображения", padding=(10, 5))
        flip_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(flip_frame, text="Нет", command=self.flip_none).pack(side=tk.LEFT, padx=5)
        ttk.Button(flip_frame, text="Горизонтально", command=self.flip_h).pack(side=tk.LEFT, padx=5)
        ttk.Button(flip_frame, text="Вертикально", command=self.flip_v).pack(side=tk.LEFT, padx=5)
        ttk.Button(flip_frame, text="Оба", command=self.flip_hv).pack(side=tk.LEFT, padx=5)
        
        # Гамма-коррекция
        gamma_frame = ttk.LabelFrame(frame, text="Гамма-коррекция", padding=(10, 5))
        gamma_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.gamma_var = tk.IntVar(value=12)
        gamma_scale = ttk.Scale(gamma_frame, from_=0, to=23, variable=self.gamma_var, orient=tk.HORIZONTAL)
        gamma_scale.pack(fill=tk.X, padx=5, pady=5)
        
        gamma_label = ttk.Label(gamma_frame, text="12")
        gamma_label.pack()
        
        def update_gamma_label(val):
            gamma_label.config(text=str(int(float(val))))
            self.set_gamma(int(float(val)))
        
        gamma_scale.config(command=update_gamma_label)
        
        # NUC таблицы
        nuc_frame = ttk.LabelFrame(frame, text="NUC Таблицы", padding=(10, 5))
        nuc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(nuc_frame, text="Таблица 0", command=self.nuc_table_0).pack(side=tk.LEFT, padx=5)
        ttk.Button(nuc_frame, text="Таблица 1", command=self.nuc_table_1).pack(side=tk.LEFT, padx=5)
        ttk.Button(nuc_frame, text="Таблица 2", command=self.nuc_table_2).pack(side=tk.LEFT, padx=5)
        
    def create_manual_controls_tab(self):
        """Создание вкладки ручного управления"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Ручное управление")
        
        # Переключатели
        switches_frame = ttk.LabelFrame(frame, text="Переключатели", padding=(10, 5))
        switches_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(switches_frame, text="Открыть перекрестие ON", command=self.open_cross_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(switches_frame, text="Открыть перекрестие OFF", command=self.open_cross_off).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(switches_frame, text="Time Domain Filter ON", command=self.time_domain_filter_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(switches_frame, text="Time Domain Filter OFF", command=self.time_domain_filter_off).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(switches_frame, text="Image Enhance ON", command=self.image_enhance_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(switches_frame, text="Image Enhance OFF", command=self.image_enhance_off).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(switches_frame, text="White Hot ON", command=self.white_hot_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(switches_frame, text="White Hot OFF", command=self.white_hot_off).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(switches_frame, text="AGC ON", command=self.agc_on).pack(side=tk.LEFT, padx=5)
        ttk.Button(switches_frame, text="AGC OFF", command=self.agc_off).pack(side=tk.LEFT, padx=5)
        
        # Дополнительные функции
        extra_frame = ttk.LabelFrame(frame, text="Дополнительные функции", padding=(10, 5))
        extra_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(extra_frame, text="Автофокус", command=self.auto_focus).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Запрос статуса", command=self.status_inquiry).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Two Point Calc", command=self.two_point_calc).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Two Point & Auto BPR Save", command=self.two_point_auto_bpr_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Manual BPR Save", command=self.manual_bpr_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Auto BPR", command=self.auto_bpr).pack(side=tk.LEFT, padx=5)
        
        # Поле для отправки произвольных команд
        custom_frame = ttk.LabelFrame(frame, text="Произвольная команда", padding=(10, 5))
        custom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(custom_frame, text="Введите команду в формате hex (через пробел):").pack(anchor=tk.W)
        
        self.custom_cmd_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_cmd_var)
        custom_entry.pack(fill=tk.X, pady=5)
        
        ttk.Button(custom_frame, text="Отправить команду", command=self.send_custom_command).pack()
        
    def refresh_ports(self):
        """Обновление списка доступных COM-портов"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        
        if not ports:
            ports = ["COM1", "COM2", "COM3", "COM4"]
        
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
    
    def toggle_connection(self):
        """Переключение состояния подключения"""
        if self.controller.is_connected:
            self.controller.disconnect()
            self.connect_btn.config(text="Подключить")
            self.log_message("Отключено от порта")
        else:
            port = self.port_var.get()
            baudrate = int(self.baudrate_var.get())  # Получаем выбранную скорость
            if self.controller.connect(port, baudrate):
                self.connect_btn.config(text="Отключить")
                self.log_message(f"Подключено к {port} на скорости {baudrate} бод")
            else:
                messagebox.showerror("Ошибка", f"Не удалось подключиться к {port}")
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
    
    def send_command_by_key(self, key):
        """Отправка команды по ключу"""
        if not self.controller.is_connected:
            messagebox.showwarning("Предупреждение", "Не подключено к камере")
            return
        
        # Проверяем наличие команды в разных словарях
        command = None
        if key in self.controller.commands:
            command = self.controller.commands[key]
        elif key in self.controller.color_palettes:
            command = self.controller.color_palettes[key]
        elif key in self.controller.zoom_levels:
            command = self.controller.zoom_levels[key]
        elif key in self.controller.image_modes:
            command = self.controller.image_modes[key]
        elif key in self.controller.flip_modes:
            command = self.controller.flip_modes[key]
        elif key in self.controller.nuc_tables:
            command = self.controller.nuc_tables[key]
        elif key in self.controller.gamma_values:
            command = self.controller.gamma_values[key]
        
        if command:
            # Добавляем callback для логирования команды
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Отправлена команда: {key}")
            else:
                self.log_message(f"Ошибка отправки команды: {key}")
        else:
            messagebox.showerror("Ошибка", f"Команда не найдена: {key}")
    
    # Базовые команды
    def open_shutter(self):
        self.send_command_by_key('shutter_open')
    
    def close_shutter(self):
        self.send_command_by_key('shutter_close')
    
    def manual_calibration(self):
        self.send_command_by_key('manual_calibration')
    
    def background_calibration(self):
        self.send_command_by_key('background_calibration')
    
    def auto_calibration_on(self):
        self.send_command_by_key('auto_calibration_on')
    
    def auto_calibration_off(self):
        self.send_command_by_key('auto_calibration_off')
    
    def reset(self):
        self.send_command_by_key('reset')
    
    def save_parameters(self):
        self.send_command_by_key('save_parameter')
    
    def save_calib_data(self):
        self.send_command_by_key('save_calib_data')
    
    # Команды управления изображением
    def set_brightness(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_brightness_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлена яркость: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def set_gain(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_gain_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлено усиление: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def set_dde(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_dde_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлено DDE: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def set_filter(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_filter_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлен фильтр: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def set_cross_x(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_cross_x_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлена координата X перекрестия: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def set_cross_y(self, value):
        if not self.controller.is_connected:
            return
        
        try:
            command = self.controller.create_cross_y_command(value)
            success = self.controller.send_command(command, log_callback=self.log_message)
            if success:
                self.log_message(f"Установлена координата Y перекрестия: {value}")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    # Расширенные команды
    def zoom_1x(self):
        self.send_command_by_key('zoom_1x')
    
    def zoom_2x(self):
        self.send_command_by_key('zoom_2x')
    
    def zoom_4x(self):
        self.send_command_by_key('zoom_4x')
    
    def mode_L(self):
        self.send_command_by_key('mode_L')
    
    def mode_M(self):
        self.send_command_by_key('mode_M')
    
    def mode_H(self):
        self.send_command_by_key('mode_H')
    
    def flip_none(self):
        self.send_command_by_key('flip_none')
    
    def flip_h(self):
        self.send_command_by_key('flip_h')
    
    def flip_v(self):
        self.send_command_by_key('flip_v')
    
    def flip_hv(self):
        self.send_command_by_key('flip_hv')
    
    def set_gamma(self, value):
        key = f'gamma_{value}'
        self.send_command_by_key(key)
    
    def nuc_table_0(self):
        self.send_command_by_key('nuc_table_0')
    
    def nuc_table_1(self):
        self.send_command_by_key('nuc_table_1')
    
    def nuc_table_2(self):
        self.send_command_by_key('nuc_table_2')
    
    # Ручные команды
    def open_cross_on(self):
        self.send_command_by_key('open_cross_on')
    
    def open_cross_off(self):
        self.send_command_by_key('open_cross_off')
    
    def time_domain_filter_on(self):
        self.send_command_by_key('time_domain_filter_on')
    
    def time_domain_filter_off(self):
        self.send_command_by_key('time_domain_filter_off')
    
    def image_enhance_on(self):
        self.send_command_by_key('image_enhance_on')
    
    def image_enhance_off(self):
        self.send_command_by_key('image_enhance_off')
    
    def white_hot_on(self):
        self.send_command_by_key('white_hot_on')
    
    def white_hot_off(self):
        self.send_command_by_key('white_hot_off')
    
    def agc_on(self):
        self.send_command_by_key('agc_on')
    
    def agc_off(self):
        self.send_command_by_key('agc_off')
    
    def auto_focus(self):
        self.send_command_by_key('auto_focus')
    
    def status_inquiry(self):
        self.send_command_by_key('status_inquiry')
    
    def two_point_calc(self):
        self.send_command_by_key('two_point_calc')
    
    def two_point_auto_bpr_save(self):
        self.send_command_by_key('two_point_auto_bpr_save')
    
    def manual_bpr_save(self):
        self.send_command_by_key('manual_bpr_save')
    
    def auto_bpr(self):
        self.send_command_by_key('auto_bpr')
    
    def send_custom_command(self):
        if not self.controller.is_connected:
            messagebox.showwarning("Предупреждение", "Не подключено к камере")
            return
        
        try:
            cmd_str = self.custom_cmd_var.get().strip()
            if not cmd_str:
                messagebox.showwarning("Предупреждение", "Введите команду")
                return
            
            # Преобразуем строку в hex значения
            hex_values = [int(x, 16) for x in cmd_str.split()]
            
            # Логируем команду перед отправкой
            self.log_message(f"Отправка пользовательской команды: {cmd_str}")
            
            success = self.controller.send_command(hex_values, log_callback=self.log_message)
            if success:
                self.log_message(f"Отправлена произвольная команда: {cmd_str}")
            else:
                self.log_message(f"Ошибка отправки команды: {cmd_str}")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат команды. Используйте шестнадцатеричные значения через пробел (например: F0 02 26 41 67 FF)")


def main():
    root = tk.Tk()
    app = ThermalCameraGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()