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
sys.modules.setdefault("AppKit", MagicMock())
sys.modules.setdefault("Quartz", MagicMock())
