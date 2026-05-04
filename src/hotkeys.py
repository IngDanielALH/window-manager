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

# Special keys (arrows, enter) — matched by hardware key code, layout-independent
KEYCODE_MAP = {
    (_CTRL_OPT, 123): snap_left,            # left arrow
    (_CTRL_OPT, 124): snap_right,           # right arrow
    (_CTRL_OPT, 126): snap_top,             # up arrow
    (_CTRL_OPT, 125): snap_bottom,          # down arrow
    (_CTRL_OPT, 36):  snap_fullscreen,      # return
    (_CTRL_OPT_SHIFT, 124): snap_next_display,  # shift + right arrow
    (_CTRL_OPT_SHIFT, 123): snap_prev_display,  # shift + left arrow
}

# Letter keys — matched by character (layout-aware, works on any keyboard)
CHAR_MAP = {
    (_CTRL_OPT, 'u'): snap_top_left,
    (_CTRL_OPT, 'i'): snap_top_right,
    (_CTRL_OPT, 'j'): snap_bottom_left,
    (_CTRL_OPT, 'k'): snap_bottom_right,
    (_CTRL_OPT, 'd'): snap_left_third,
    (_CTRL_OPT, 'f'): snap_center_third,
    (_CTRL_OPT, 'g'): snap_right_third,
    (_CTRL_OPT, 'e'): snap_left_two_thirds,
    (_CTRL_OPT, 'r'): snap_center_two_thirds,
    (_CTRL_OPT, 't'): snap_right_two_thirds,
    (_CTRL_OPT, 'c'): snap_center,
}


def _handle_event(event):
    flags = event.modifierFlags() & _MOD_MASK

    # 1. Try special keys (arrows, enter) by key code
    action = KEYCODE_MAP.get((flags, event.keyCode()))

    # 2. Try letter keys by character, ignoring modifiers (layout-aware)
    if action is None:
        chars = event.charactersIgnoringModifiers()
        if chars:
            action = CHAR_MAP.get((flags, chars.lower()))

    if action:
        action()


def start_listener():
    return NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
        NSEventMaskKeyDown, _handle_event
    )
