from evdev import InputDevice, list_devices, ecodes

# Функция для поиска устройства по имени
def find_device_by_name(device_name):
    # Получаем список всех устройств
    devices = [InputDevice(path) for path in list_devices()]
    for device in devices:
        print(f"device: {device.name}")
    
    for device in devices:
        if device.name.strip() == device_name:
            return device
    return None

# Название устройства мыши
device_mouse_name = "INSTANT USB GAMING MOUSE"

# Поиск устройства мыши
device_mouse = find_device_by_name(device_mouse_name)

if device_mouse:
    print(f"Device found: {device_mouse.name}")
    
    # Чтение событий с устройства
    for event in device_mouse.read_loop():
        if event.type == ecodes.EV_KEY:  # Событие клавиши
            if event.value == 1:  # Нажатие кнопки (1 - нажата, 0 - отпущена)
                if event.code == ecodes.BTN_LEFT:
                    print("Left click")
                elif event.code == ecodes.BTN_RIGHT:
                    print("Right click")
                elif event.code == ecodes.BTN_MIDDLE:
                    print("Middle click")
else:
    print(f"Device '{device_mouse_name}' not found.")
