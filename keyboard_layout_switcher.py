from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key
from pynput.mouse import Listener as MouseListener
from evdev import InputDevice, list_devices, ecodes
import signal
import sys
import subprocess
import os
import threading
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(message)s',  # Формат логов
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "app.log")),  # Логирование в файл
        logging.StreamHandler()  # Логирование в консоль
    ]
)

def parse_input_devices(file_path="/proc/bus/input/devices"):
    devices = []
    current_device = {}

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith("N: Name="):  # Capture the name of the device
                if current_device:
                    devices.append(current_device)  # Add the previous device to the list
                    current_device = {}  # Reset for the new device
                current_device['name'] = line.split('=')[1].strip('"')
            
            elif line.startswith("H: Handlers="):  # Capture the handlers (eventX)
                handlers = line.split('=')[1].strip()
                # We're interested in eventX for the device path
                for handler in handlers.split():
                    if handler.startswith("event"):
                        current_device['path'] = f"/dev/input/{handler}"
        
        # Add the last device to the list if it exists
        if current_device:
            devices.append(current_device)

    return devices

# Создаем объект контроллера для управления клавишами
keyboard_controller = KeyboardController()

key_mapping = {
    'й': 'q',
    'ц': 'w',
    'у': 'e',
    'к': 'r',
    'е': 't',
    'н': 'y',
    'г': 'u',
    'ш': 'i',
    'щ': 'o',
    'з': 'p',
    'х': '[',
    'ъ': ']',
    'ф': 'a',
    'ы': 's',
    'в': 'd',
    'а': 'f',
    'п': 'g',
    'р': 'h',
    'о': 'j',
    'л': 'k',
    'д': 'l',
    'ж': ';',
    'э': '\'',
    'я': 'z',
    'ч': 'x',
    'с': 'c',
    'м': 'v',
    'и': 'b',
    'т': 'n',
    'ь': 'm',
    'б': ',',
    'ю': '.',
    
    'Й': 'Q',
    'Ц': 'W',
    'У': 'E',
    'К': 'R',
    'Е': 'T',
    'Н': 'Y',
    'Г': 'U',
    'Ш': 'I',
    'Щ': 'O',
    'З': 'P',
    'Х': '{',
    'Ъ': '}',
    'Ф': 'A',
    'Ы': 'S',
    'В': 'D',
    'А': 'F',
    'П': 'G',
    'Р': 'H',
    'О': 'J',
    'Л': 'K',
    'Д': 'L',
    'Ж': ':',
    'Э': '"',
    'Я': 'Z',
    'Ч': 'X',
    'С': 'C',
    'М': 'V',
    'И': 'B',
    'Т': 'N',
    'Ь': 'M',
    'Б': '<',
    'Ю': '>',
}

# Функция для получения текущей раскладки
def get_current_layout():
    command = "sudo -E -u user gdbus introspect --session --dest org.gnome.Shell --object-path /me/madhead/Shyriiwook --only-properties | grep 'currentLayout' | awk -F\"'\" '{print $2}'"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    layout = result.stdout.strip()
    return layout

# Переменные для отслеживания состояния клавиш
ctrl_pressed = False
c_pressed = False
shift_pressed = False
alt_pressed = False
programmatic_press = False
last_word = ""
clear_the_word_at_next_symbol = False
backspace_lenght = 0

def on_press(key):
    global current_dir, ctrl_pressed, c_pressed, shift_pressed, alt_pressed, last_word, programmatic_press, clear_the_word_at_next_symbol, backspace_lenght
    try:
        logging.info(f"Нажата клавиша: {key}")
        if key.char.isalnum() and programmatic_press == False and ctrl_pressed == False and alt_pressed == False:
            if clear_the_word_at_next_symbol == True or (last_word and (last_word[-1] == " " or last_word[-1] == "\n")):
                last_word = ""
            last_word += key.char
            clear_the_word_at_next_symbol = False
        if key.char.isalnum() and programmatic_press == False and ctrl_pressed == True and alt_pressed == False and key.char == "ф":
            last_word = ""
            
    except AttributeError:
        logging.info(f"Нажата клавиша (специальная): {key}")
        if programmatic_press == False:
            if key == Key.space:
                clear_the_word_at_next_symbol = True
                last_word += " "
            if key == Key.enter:
                clear_the_word_at_next_symbol = True
                last_word += "\n"
            if key == Key.backspace:
                prev_backspace_lenght = backspace_lenght
                if backspace_lenght > 0:
                    backspace_lenght -= 1
                else:
                    backspace_lenght = 0
                print(f"backspace_lenght: {backspace_lenght}")
                if backspace_lenght == 0:
                    clear_the_word_at_next_symbol = True
                    if prev_backspace_lenght == 0:
                        last_word = last_word[:-1] if last_word else last_word
                        clear_the_word_at_next_symbol = False
                    last_word = last_word.rstrip('\n')
            
    logging.info(f"last_word: |{last_word}|")
    logging.info(f"programmatic_press: {programmatic_press}")
    logging.info(f"clear_the_word_at_next_symbol: {clear_the_word_at_next_symbol}")
        
    # Отслеживаем нажатие Ctrl
    if key == Key.ctrl_l or key == Key.ctrl_r:
        ctrl_pressed = True

    # Отслеживаем нажатие C
    if hasattr(key, 'char') and key.char == 'c':
        c_pressed = True

    # Отслеживаем нажатие Shift
    if key == Key.shift_l:
        shift_pressed = True
    
    # Отслеживаем нажатие Alt
    if key == Key.alt:
        alt_pressed = True
        
    # Отслеживаем нажатие Shift и Alt по коду
    if hasattr(key, 'vk'):  # Проверяем, что у клавиши есть код
        if key.vk == 65511:  # Это код для Alt
            alt_pressed = True
        if key.vk == 65505:  # Это код для Shift (левая)
            shift_pressed = True

    logging.info(f"shift_alt_ctrl_pressed: {shift_pressed} {alt_pressed} {ctrl_pressed}")

    
    if ctrl_pressed and alt_pressed and last_word:
        print(f"Стираем и снова вводим слово: {key} {last_word}")
        keyboard_controller.release(Key.ctrl_l)
        keyboard_controller.release(Key.ctrl_r)
        keyboard_controller.release(Key.alt)
        # Стираем последнее слово
        programmatic_press = True
        
        for _ in range(len(last_word)):
            keyboard_controller.press(Key.backspace)
            keyboard_controller.release(Key.backspace)
        
        script_path = os.path.join(current_dir, "switch_layout.sh")
        
        # Запуск скрипта для переключения раскладки
        try:
            subprocess.run(['sudo', '-E', script_path], check=True)
        except subprocess.CalledProcessError as e:
            logging.info(f"Ошибка при выполнении скрипта: {e}")
        except FileNotFoundError:
            logging.info(f"Скрипт {script_path} не найден.")
        
        temp_word = last_word
        clear_the_word_at_next_symbol = True
        
        # Получаем текущую раскладку
        current_layout = get_current_layout()
        logging.info(f"Текущая раскладка: {current_layout}")
            
        keyboard_controller.release(Key.ctrl_l)
        keyboard_controller.release(Key.ctrl_r)
        keyboard_controller.release(Key.alt)
        
        # Повторный ввод последнего слова
        for char in temp_word:
            symbol = key_mapping.get(char) if current_layout == 'us' and char in key_mapping else char
            keyboard_controller.press(symbol)
            keyboard_controller.release(symbol)
        
        programmatic_press = False
        backspace_lenght = len(temp_word)
    
    # Если нажаты Shift и Alt одновременно, запускаем скрипт switch_layout.sh
    if shift_pressed and alt_pressed:
        last_word = ""
        logging.info("Нажаты Shift и Alt, запускаем скрипт switch_layout.sh...")
        # Путь к скрипту
        script_path = os.path.join(current_dir, "switch_layout.sh")
        
        try:
            # Запускаем скрипт
            subprocess.run(['sudo', '-E', script_path], check=True)
        except subprocess.CalledProcessError as e:
            logging.info(f"Ошибка при выполнении скрипта: {e}")
        except FileNotFoundError:
            logging.info(f"Скрипт {script_path} не найден.")

def on_release(key):
    global ctrl_pressed, c_pressed, shift_pressed, alt_pressed
    if key == Key.ctrl_l or key == Key.ctrl_r:
        ctrl_pressed = False
    if hasattr(key, 'char') and key.char == 'c':
        c_pressed = False

    # Отслеживаем отпускание клавиш Shift и Alt
    if key == Key.shift_l:
        shift_pressed = False
    if key == Key.alt_l or hasattr(key, 'vk') and key.vk == 65511:
        alt_pressed = False

    # Завершаем программу, если нажаты Ctrl+C
    if ctrl_pressed and c_pressed:
        logging.info("Программа завершена через Ctrl+C.")
        return False
    if key == Key.esc:
        return False
    
def on_click():
    global last_word, clear_the_word_at_next_symbol
    #if pressed:  # если нажата кнопка мыши
    last_word = ""
    clear_the_word_at_next_symbol = False
    logging.info(f"Mouse clicked")

# Обработка сигнала Ctrl+C
def signal_handler(sig, frame):
    logging.info("\nПрограмма завершена.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Функция для поиска устройства по имени
def find_device_by_name(device_name):
    # Получаем список всех устройств
    devices = parse_input_devices()
    logging.info(f"devices: {devices}")
    
    try:
        user = subprocess.check_output(['whoami'], text=True).strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting user: {e}")
        return None
    
    for device in devices:
        if device['name'].strip() == device_name:
            device_path = device['path']
            try:
                # Set ACL permissions for the device if necessary
                subprocess.run(['sudo', 'setfacl', '-m', f'u:{user}:rwx', device_path], check=True)
                
                # Now attempt to access the device
                return InputDevice(device_path)
            except subprocess.CalledProcessError as e:
                logging.error(f"Error accessing {device_path}: {e}")
                return None
    return None

device_name = "INSTANT USB GAMING MOUSE"
device = find_device_by_name(device_name)

# Чтение событий от мыши через evdev
def start_listening_mouse():
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:  # Нажатие кнопки
                on_click()  # Обработка события клика
    except Exception as e:
        logging.info(f"Error: {e}")

# Запуск прослушивания событий мыши в отдельном потоке
mouse_thread = threading.Thread(target=start_listening_mouse)
mouse_thread.daemon = True  # Даем разрешение на завершение потока при завершении программы
mouse_thread.start()

# Запуск слушателя для клавиатуры в отдельном потоке
keyboard_listener = KeyboardListener(on_press=on_press, on_release=on_release)
keyboard_listener.start()
keyboard_listener.join()

