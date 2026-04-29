from ApplicationServices import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    AXUIElementSetAttributeValue,
    AXValueCreate,
    AXValueGetValue,
    kAXErrorSuccess,
    kAXFocusedApplicationAttribute,
    kAXFocusedWindowAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXValueTypeCGPoint,
    kAXValueTypeCGSize,
)
from AppKit import NSScreen
import Quartz


# ── Internal helpers ─────────────────────────────────────────────────────────

def _get_focused_window():
    system = AXUIElementCreateSystemWide()
    err, app = AXUIElementCopyAttributeValue(system, kAXFocusedApplicationAttribute, None)
    if err != kAXErrorSuccess or app is None:
        return None
    err, window = AXUIElementCopyAttributeValue(app, kAXFocusedWindowAttribute, None)
    if err != kAXErrorSuccess:
        return None
    return window


def _get_window_size(window):
    """Return (width, height) of the window, or None on error."""
    err, ax_size = AXUIElementCopyAttributeValue(window, kAXSizeAttribute, None)
    if err != kAXErrorSuccess:
        return None
    _, cgsize = AXValueGetValue(ax_size, kAXValueTypeCGSize, None)
    return cgsize.width, cgsize.height


def _get_window_center(window):
    """Return (cx, cy) center point of the window, or None on error."""
    err, ax_pos = AXUIElementCopyAttributeValue(window, kAXPositionAttribute, None)
    if err != kAXErrorSuccess:
        return None
    err, ax_size = AXUIElementCopyAttributeValue(window, kAXSizeAttribute, None)
    if err != kAXErrorSuccess:
        return None
    _, cgpoint = AXValueGetValue(ax_pos, kAXValueTypeCGPoint, None)
    _, cgsize = AXValueGetValue(ax_size, kAXValueTypeCGSize, None)
    return cgpoint.x + cgsize.width / 2, cgpoint.y + cgsize.height / 2


def _visible_frame_for_point(cx, cy):
    """Return visible frame (x, y, w, h) of the screen containing (cx, cy)."""
    for screen in NSScreen.screens():
        f = screen.frame()
        if (f.origin.x <= cx < f.origin.x + f.size.width and
                f.origin.y <= cy < f.origin.y + f.size.height):
            vf = screen.visibleFrame()
            return vf.origin.x, vf.origin.y, vf.size.width, vf.size.height
    vf = NSScreen.mainScreen().visibleFrame()
    return vf.origin.x, vf.origin.y, vf.size.width, vf.size.height


def _frame_for_window(window):
    """Return visible frame of the screen the window currently lives on."""
    center = _get_window_center(window)
    if center is None:
        vf = NSScreen.mainScreen().visibleFrame()
        return vf.origin.x, vf.origin.y, vf.size.width, vf.size.height
    return _visible_frame_for_point(*center)


def _screen_index_for_window(window):
    """Return (index, [NSScreen]) for the screen containing the window."""
    screens = NSScreen.screens()
    center = _get_window_center(window)
    if center is None:
        return 0, screens
    cx, cy = center
    for i, screen in enumerate(screens):
        f = screen.frame()
        if (f.origin.x <= cx < f.origin.x + f.size.width and
                f.origin.y <= cy < f.origin.y + f.size.height):
            return i, screens
    return 0, screens


def _move_window(window, x, y, w, h):
    pos_val = AXValueCreate(kAXValueTypeCGPoint, Quartz.CGPoint(x, y))
    size_val = AXValueCreate(kAXValueTypeCGSize, Quartz.CGSize(w, h))
    AXUIElementSetAttributeValue(window, kAXPositionAttribute, pos_val)
    AXUIElementSetAttributeValue(window, kAXSizeAttribute, size_val)


def _set_window_position(window, x, y):
    pos_val = AXValueCreate(kAXValueTypeCGPoint, Quartz.CGPoint(x, y))
    AXUIElementSetAttributeValue(window, kAXPositionAttribute, pos_val)


# ── Halves ───────────────────────────────────────────────────────────────────

def snap_left():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, w / 2, h)


def snap_right():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 2, y, w / 2, h)


def snap_top():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y + h / 2, w, h / 2)


def snap_bottom():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, w, h / 2)


# ── Fullscreen ───────────────────────────────────────────────────────────────

def snap_fullscreen():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, w, h)


# ── Quarters ─────────────────────────────────────────────────────────────────

def snap_top_left():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y + h / 2, w / 2, h / 2)


def snap_top_right():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 2, y + h / 2, w / 2, h / 2)


def snap_bottom_left():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, w / 2, h / 2)


def snap_bottom_right():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 2, y, w / 2, h / 2)


# ── Thirds ───────────────────────────────────────────────────────────────────

def snap_left_third():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, w / 3, h)


def snap_center_third():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 3, y, w / 3, h)


def snap_right_third():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + 2 * w / 3, y, w / 3, h)


# ── Two Thirds ────────────────────────────────────────────────────────────────

def snap_left_two_thirds():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x, y, 2 * w / 3, h)


def snap_center_two_thirds():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 6, y, 2 * w / 3, h)


def snap_right_two_thirds():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    _move_window(window, x + w / 3, y, 2 * w / 3, h)


# ── Center ────────────────────────────────────────────────────────────────────

def snap_center():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _frame_for_window(window)
    size = _get_window_size(window)
    if size is None:
        return
    win_w, win_h = size
    _set_window_position(window, x + (w - win_w) / 2, y + (h - win_h) / 2)


# ── Displays ──────────────────────────────────────────────────────────────────

def snap_next_display():
    window = _get_focused_window()
    if window is None:
        return
    idx, screens = _screen_index_for_window(window)
    if len(screens) <= 1:
        return
    vf = screens[(idx + 1) % len(screens)].visibleFrame()
    _move_window(window, vf.origin.x, vf.origin.y, vf.size.width, vf.size.height)


def snap_prev_display():
    window = _get_focused_window()
    if window is None:
        return
    idx, screens = _screen_index_for_window(window)
    if len(screens) <= 1:
        return
    vf = screens[(idx - 1) % len(screens)].visibleFrame()
    _move_window(window, vf.origin.x, vf.origin.y, vf.size.width, vf.size.height)
