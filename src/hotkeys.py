from pynput import keyboard
from src.window_controller import (
    snap_left,
    snap_right,
    snap_top,
    snap_bottom,
    snap_fullscreen,
    snap_top_left,
    snap_top_right,
    snap_bottom_left,
    snap_bottom_right,
    snap_left_third,
    snap_center_third,
    snap_right_third,
    snap_left_two_thirds,
    snap_center_two_thirds,
    snap_right_two_thirds,
    snap_center,
    snap_next_display,
    snap_prev_display,
)

HOTKEY_MAP = {
    # Halves
    "<ctrl>+<alt>+<left>":  snap_left,
    "<ctrl>+<alt>+<right>": snap_right,
    "<ctrl>+<alt>+<up>":    snap_top,
    "<ctrl>+<alt>+<down>":  snap_bottom,
    # Fullscreen
    "<ctrl>+<alt>+<enter>": snap_fullscreen,
    # Quarters
    "<ctrl>+<alt>+u": snap_top_left,
    "<ctrl>+<alt>+i": snap_top_right,
    "<ctrl>+<alt>+j": snap_bottom_left,
    "<ctrl>+<alt>+k": snap_bottom_right,
    # Thirds
    "<ctrl>+<alt>+d": snap_left_third,
    "<ctrl>+<alt>+f": snap_center_third,
    "<ctrl>+<alt>+g": snap_right_third,
    # Two Thirds
    "<ctrl>+<alt>+e": snap_left_two_thirds,
    "<ctrl>+<alt>+r": snap_center_two_thirds,
    "<ctrl>+<alt>+t": snap_right_two_thirds,
    # Center & Displays
    "<ctrl>+<alt>+c":               snap_center,
    "<ctrl>+<alt>+<shift>+<right>": snap_next_display,
    "<ctrl>+<alt>+<shift>+<left>":  snap_prev_display,
}


def start_listener():
    return keyboard.GlobalHotKeys(HOTKEY_MAP)
