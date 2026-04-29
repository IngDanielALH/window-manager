from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXUIElementSetAttributeValue,
    AXValueCreate,
    kAXErrorSuccess,
    kAXFocusedWindowAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXValueTypeCGPoint,
    kAXValueTypeCGSize,
)
from AppKit import NSScreen, NSWorkspace
import Quartz


def _get_screen_frame():
    frame = NSScreen.mainScreen().visibleFrame()
    return frame.origin.x, frame.origin.y, frame.size.width, frame.size.height


def _move_window(window, x, y, w, h):
    point = Quartz.CGPoint(x, y)
    size = Quartz.CGSize(w, h)
    pos_val = AXValueCreate(kAXValueTypeCGPoint, point)
    size_val = AXValueCreate(kAXValueTypeCGSize, size)
    AXUIElementSetAttributeValue(window, kAXPositionAttribute, pos_val)
    AXUIElementSetAttributeValue(window, kAXSizeAttribute, size_val)


def _get_focused_window():
    workspace = NSWorkspace.sharedWorkspace()
    app = workspace.frontmostApplication()
    if app is None:
        return None
    pid = app.processIdentifier()
    ax_app = AXUIElementCreateApplication(pid)
    err, window = AXUIElementCopyAttributeValue(ax_app, kAXFocusedWindowAttribute, None)
    if err != kAXErrorSuccess:
        return None
    return window


def snap_left():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _get_screen_frame()
    _move_window(window, x, y, w / 2, h)


def snap_right():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _get_screen_frame()
    _move_window(window, x + w / 2, y, w / 2, h)


def snap_top():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _get_screen_frame()
    _move_window(window, x, y + h / 2, w, h / 2)


def snap_bottom():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _get_screen_frame()
    _move_window(window, x, y, w, h / 2)


def snap_fullscreen():
    window = _get_focused_window()
    if window is None:
        return
    x, y, w, h = _get_screen_frame()
    _move_window(window, x, y, w, h)
