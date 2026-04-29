from pynput import keyboard
from src.window_controller import (
    snap_left,
    snap_right,
    snap_top,
    snap_bottom,
    snap_fullscreen,
)

HOTKEY_MAP = {
    "<ctrl>+<alt>+left": snap_left,
    "<ctrl>+<alt>+right": snap_right,
    "<ctrl>+<alt>+up": snap_top,
    "<ctrl>+<alt>+down": snap_bottom,
    "<ctrl>+<alt>+<enter>": snap_fullscreen,
}


def start_listener():
    return keyboard.GlobalHotKeys(HOTKEY_MAP)
