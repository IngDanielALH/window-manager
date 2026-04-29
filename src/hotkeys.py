from AppKit import (
    NSEvent,
    NSEventMaskKeyDown,
    NSEventModifierFlagControl,
    NSEventModifierFlagOption,
    NSEventModifierFlagShift,
)
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

_CTRL_OPT       = NSEventModifierFlagControl | NSEventModifierFlagOption
_CTRL_OPT_SHIFT = _CTRL_OPT | NSEventModifierFlagShift
_MOD_MASK       = _CTRL_OPT_SHIFT

# macOS virtual key codes (hardware position, layout-independent)
KEY_MAP = {
    # Halves
    (_CTRL_OPT, 123): snap_left,
    (_CTRL_OPT, 124): snap_right,
    (_CTRL_OPT, 126): snap_top,
    (_CTRL_OPT, 125): snap_bottom,
    # Fullscreen
    (_CTRL_OPT, 36):  snap_fullscreen,
    # Quarters
    (_CTRL_OPT, 32):  snap_top_left,
    (_CTRL_OPT, 34):  snap_top_right,
    (_CTRL_OPT, 38):  snap_bottom_left,
    (_CTRL_OPT, 40):  snap_bottom_right,
    # Thirds
    (_CTRL_OPT, 2):   snap_left_third,
    (_CTRL_OPT, 3):   snap_center_third,
    (_CTRL_OPT, 5):   snap_right_third,
    # Two Thirds
    (_CTRL_OPT, 14):  snap_left_two_thirds,
    (_CTRL_OPT, 15):  snap_center_two_thirds,
    (_CTRL_OPT, 17):  snap_right_two_thirds,
    # Center & Displays
    (_CTRL_OPT, 8):         snap_center,
    (_CTRL_OPT_SHIFT, 124): snap_next_display,
    (_CTRL_OPT_SHIFT, 123): snap_prev_display,
}


def _handle_event(event):
    flags = event.modifierFlags() & _MOD_MASK
    action = KEY_MAP.get((flags, event.keyCode()))
    if action:
        action()


def start_listener():
    return NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
        NSEventMaskKeyDown, _handle_event
    )
