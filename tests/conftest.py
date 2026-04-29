import sys
from unittest.mock import MagicMock

def _ax_stub():
    m = MagicMock()
    m.kAXErrorSuccess = 0
    m.kAXFocusedWindowAttribute = "AXFocusedWindow"
    m.kAXPositionAttribute = "AXPosition"
    m.kAXSizeAttribute = "AXSize"
    m.kAXValueTypeCGPoint = 1
    m.kAXValueTypeCGSize = 2
    return m

sys.modules.setdefault("ApplicationServices", _ax_stub())
def _appkit_stub():
    m = MagicMock()
    m.NSEventModifierFlagControl = 1 << 18  # 262144
    m.NSEventModifierFlagOption  = 1 << 19  # 524288
    m.NSEventModifierFlagShift   = 1 << 17  # 131072
    m.NSEventMaskKeyDown         = 1 << 10  # 1024
    return m

sys.modules.setdefault("AppKit", _appkit_stub())
sys.modules.setdefault("Quartz", MagicMock())
