from ApplicationServices import (
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXUIElementSetAttributeValue,
    AXValueCreate,
    kAXFocusedWindowAttribute,
    kAXPositionAttribute,
    kAXSizeAttribute,
    kAXValueTypeCGPoint,
    kAXValueTypeCGSize,
    kAXErrorSuccess,
)
from AppKit import NSWorkspace, NSScreen
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
