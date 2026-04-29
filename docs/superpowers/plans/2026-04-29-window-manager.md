# Window Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python window manager for macOS that snaps the focused window to halves or fullscreen using Magnet-compatible keyboard shortcuts.

**Architecture:** Three modules — `window_controller.py` owns all Accessibility API interaction, `hotkeys.py` maps keyboard combos to controller functions, and `main.py` is the entry point that checks permissions and starts the listener. All macOS-specific imports are at module level so tests can mock them via `conftest.py`.

**Tech Stack:** Python 3.9+, `pyobjc-framework-ApplicationServices`, `pyobjc-framework-Cocoa`, `pynput`

---

## File Map

| Path | Action | Responsibility |
|---|---|---|
| `requirements.txt` | Create | Pinned dependencies |
| `.gitignore` | Create | Python + macOS ignores |
| `src/__init__.py` | Create | Package marker |
| `src/window_controller.py` | Create | Accessibility API: get window, get screen frame, move/resize, snap functions |
| `src/hotkeys.py` | Create | Hotkey map + listener factory |
| `main.py` | Create | Permission check + startup |
| `tests/__init__.py` | Create | Test package marker |
| `tests/conftest.py` | Create | Stub pyobjc modules before any import |
| `tests/test_window_controller.py` | Create | Unit tests for all controller functions |
| `tests/test_hotkeys.py` | Create | Unit tests for hotkey map |
| `tests/test_main.py` | Create | Unit tests for permission check and startup |
| `README.md` | Create | Full usage guide |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create `requirements.txt`**

```
pyobjc-framework-ApplicationServices>=9.0
pyobjc-framework-Cocoa>=9.0
pynput>=1.7.6
pytest>=7.0
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/
.DS_Store
*.log
```

- [ ] **Step 3: Create package markers**

```bash
touch src/__init__.py tests/__init__.py
```

- [ ] **Step 4: Create `tests/conftest.py`**

This file stubs out all pyobjc modules so tests can run without macOS dependencies installed and without the Accessibility permission dialog appearing.

```python
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
```

- [ ] **Step 5: Install dependencies in a virtualenv**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Expected: all packages install without error.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore src/__init__.py tests/__init__.py tests/conftest.py
git commit -m "chore: project scaffolding"
```

---

## Task 2: Window Controller — Screen Frame and Move Helpers

**Files:**
- Create: `src/window_controller.py`
- Create: `tests/test_window_controller.py`

- [ ] **Step 1: Write failing tests for `_get_screen_frame` and `_move_window`**

```python
# tests/test_window_controller.py
from unittest.mock import MagicMock, patch, call
import pytest


def _make_frame(x, y, w, h):
    frame = MagicMock()
    frame.origin.x = x
    frame.origin.y = y
    frame.size.width = w
    frame.size.height = h
    return frame


class TestGetScreenFrame:
    def test_returns_visible_frame_components(self):
        frame = _make_frame(0, 23, 1920, 1057)
        with patch("src.window_controller.NSScreen") as mock_ns:
            mock_ns.mainScreen.return_value.visibleFrame.return_value = frame
            from src.window_controller import _get_screen_frame
            result = _get_screen_frame()
        assert result == (0, 23, 1920, 1057)

    def test_returns_floats_unchanged(self):
        frame = _make_frame(0.0, 0.0, 2560.0, 1394.0)
        with patch("src.window_controller.NSScreen") as mock_ns:
            mock_ns.mainScreen.return_value.visibleFrame.return_value = frame
            from src.window_controller import _get_screen_frame
            result = _get_screen_frame()
        assert result == (0.0, 0.0, 2560.0, 1394.0)


class TestMoveWindow:
    def test_sets_position_then_size(self):
        import sys
        ax = sys.modules["ApplicationServices"]
        quartz = sys.modules["Quartz"]

        fake_window = MagicMock()
        fake_pos_val = MagicMock()
        fake_size_val = MagicMock()

        ax.AXValueCreate.side_effect = [fake_pos_val, fake_size_val]

        from src.window_controller import _move_window
        _move_window(fake_window, 10, 20, 960, 1057)

        quartz.CGPoint.assert_called_once_with(10, 20)
        quartz.CGSize.assert_called_once_with(960, 1057)
        ax.AXUIElementSetAttributeValue.assert_any_call(
            fake_window, ax.kAXPositionAttribute, fake_pos_val
        )
        ax.AXUIElementSetAttributeValue.assert_any_call(
            fake_window, ax.kAXSizeAttribute, fake_size_val
        )
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate
pytest tests/test_window_controller.py -v
```

Expected: `ImportError` — `src.window_controller` does not exist yet.

- [ ] **Step 3: Create `src/window_controller.py` with the two helpers**

```python
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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/test_window_controller.py -v
```

Expected:
```
PASSED tests/test_window_controller.py::TestGetScreenFrame::test_returns_visible_frame_components
PASSED tests/test_window_controller.py::TestGetScreenFrame::test_returns_floats_unchanged
PASSED tests/test_window_controller.py::TestMoveWindow::test_sets_position_then_size
```

- [ ] **Step 5: Commit**

```bash
git add src/window_controller.py tests/test_window_controller.py
git commit -m "feat: window controller screen frame and move helpers"
```

---

## Task 3: Window Controller — Focused Window

**Files:**
- Modify: `src/window_controller.py` — add `_get_focused_window()`
- Modify: `tests/test_window_controller.py` — add `TestGetFocusedWindow`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_window_controller.py`:

```python
class TestGetFocusedWindow:
    def test_returns_window_on_success(self):
        import sys
        ax = sys.modules["ApplicationServices"]
        appkit = sys.modules["AppKit"]

        fake_pid = 1234
        fake_app_element = MagicMock()
        fake_window = MagicMock()

        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value.processIdentifier.return_value = fake_pid
        ax.AXUIElementCreateApplication.return_value = fake_app_element
        ax.AXUIElementCopyAttributeValue.return_value = (ax.kAXErrorSuccess, fake_window)

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        ax.AXUIElementCreateApplication.assert_called_once_with(fake_pid)
        assert result is fake_window

    def test_returns_none_when_no_frontmost_app(self):
        import sys
        appkit = sys.modules["AppKit"]
        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value = None

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None

    def test_returns_none_on_ax_error(self):
        import sys
        ax = sys.modules["ApplicationServices"]
        appkit = sys.modules["AppKit"]

        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value.processIdentifier.return_value = 42
        ax.AXUIElementCopyAttributeValue.return_value = (1, None)  # non-zero = error

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_window_controller.py::TestGetFocusedWindow -v
```

Expected: `AttributeError` — `_get_focused_window` not defined.

- [ ] **Step 3: Add `_get_focused_window` to `src/window_controller.py`**

Add after `_move_window`:

```python
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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/test_window_controller.py -v
```

Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/window_controller.py tests/test_window_controller.py
git commit -m "feat: window controller focused window helper"
```

---

## Task 4: Window Controller — Snap Functions

**Files:**
- Modify: `src/window_controller.py` — add 5 snap functions
- Modify: `tests/test_window_controller.py` — add `TestSnapFunctions`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_window_controller.py`:

```python
class TestSnapFunctions:
    """Each snap function: get window, compute target frame, call _move_window."""

    SCREEN = (0, 23, 1920, 1057)  # x, y, w, h from visibleFrame

    def _setup(self, monkeypatch):
        import src.window_controller as wc
        fake_window = MagicMock()
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_get_screen_frame", lambda: self.SCREEN)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        return fake_window, mock_move

    def test_snap_left(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_left()
        move.assert_called_once_with(w, 0, 23, 960, 1057)

    def test_snap_right(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_right()
        move.assert_called_once_with(w, 960, 23, 960, 1057)

    def test_snap_top(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_top()
        move.assert_called_once_with(w, 0, 23 + 528.5, 1920, 528.5)

    def test_snap_bottom(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_bottom()
        move.assert_called_once_with(w, 0, 23, 1920, 528.5)

    def test_snap_fullscreen(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_fullscreen()
        move.assert_called_once_with(w, 0, 23, 1920, 1057)

    def test_snap_skips_when_no_window(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: None)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        wc.snap_left()
        mock_move.assert_not_called()
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_window_controller.py::TestSnapFunctions -v
```

Expected: `AttributeError` — snap functions not defined.

- [ ] **Step 3: Add snap functions to `src/window_controller.py`**

Add at the bottom of the file:

```python
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
```

- [ ] **Step 4: Run all tests — expect pass**

```bash
pytest tests/test_window_controller.py -v
```

Expected: all 12 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/window_controller.py tests/test_window_controller.py
git commit -m "feat: window controller snap functions"
```

---

## Task 5: Hotkeys Module

**Files:**
- Create: `src/hotkeys.py`
- Create: `tests/test_hotkeys.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_hotkeys.py
from unittest.mock import MagicMock, patch
import pytest


class TestHotkeyMap:
    def test_all_magnet_shortcuts_are_registered(self):
        with patch("src.hotkeys.keyboard") as mock_kb:
            import src.hotkeys as hk
            import importlib
            importlib.reload(hk)
            keys = list(hk.HOTKEY_MAP.keys())

        assert "<ctrl>+<alt>+left" in keys
        assert "<ctrl>+<alt>+right" in keys
        assert "<ctrl>+<alt>+up" in keys
        assert "<ctrl>+<alt>+down" in keys
        assert "<ctrl>+<alt>+<enter>" in keys

    def test_hotkey_map_values_are_callable(self):
        with patch("src.hotkeys.keyboard"):
            import src.hotkeys as hk
            import importlib
            importlib.reload(hk)

        for combo, action in hk.HOTKEY_MAP.items():
            assert callable(action), f"{combo} maps to non-callable"

    def test_start_listener_returns_globalhotkeys_instance(self):
        with patch("src.hotkeys.keyboard") as mock_kb:
            import src.hotkeys as hk
            import importlib
            importlib.reload(hk)

            fake_listener = MagicMock()
            mock_kb.GlobalHotKeys.return_value = fake_listener

            result = hk.start_listener()

        mock_kb.GlobalHotKeys.assert_called_once_with(hk.HOTKEY_MAP)
        assert result is fake_listener
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_hotkeys.py -v
```

Expected: `ModuleNotFoundError` — `src.hotkeys` does not exist.

- [ ] **Step 3: Create `src/hotkeys.py`**

```python
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
```

- [ ] **Step 4: Run tests — expect pass**

```bash
pytest tests/test_hotkeys.py -v
```

Expected: all 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/hotkeys.py tests/test_hotkeys.py
git commit -m "feat: hotkeys module with Magnet-compatible shortcuts"
```

---

## Task 6: Main Entry Point

**Files:**
- Create: `main.py`
- Create: `tests/test_main.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_main.py
from unittest.mock import MagicMock, patch
import pytest


class TestMain:
    def test_exits_when_accessibility_not_granted(self, capsys):
        with patch("main.AXIsProcessTrusted", return_value=False), \
             patch("main.start_listener") as mock_listener, \
             pytest.raises(SystemExit) as exc_info:
            import main
            import importlib
            importlib.reload(main)

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Accessibility" in captured.out
        mock_listener.assert_not_called()

    def test_starts_listener_when_trusted(self):
        fake_listener = MagicMock()
        with patch("main.AXIsProcessTrusted", return_value=True), \
             patch("main.start_listener", return_value=fake_listener):
            import main
            import importlib
            importlib.reload(main)

        fake_listener.start.assert_called_once()
        fake_listener.join.assert_called_once()
```

- [ ] **Step 2: Run to confirm failure**

```bash
pytest tests/test_main.py -v
```

Expected: `ModuleNotFoundError` — `main` does not exist.

- [ ] **Step 3: Create `main.py`**

```python
from ApplicationServices import AXIsProcessTrusted
from src.hotkeys import start_listener
import sys

SHORTCUTS = [
    "  ⌃⌥←   Snap left",
    "  ⌃⌥→   Snap right",
    "  ⌃⌥↑   Snap top",
    "  ⌃⌥↓   Snap bottom",
    "  ⌃⌥↩   Fullscreen",
]


def main():
    if not AXIsProcessTrusted():
        print(
            "Accessibility permission required.\n"
            "Go to: System Settings → Privacy & Security → Accessibility\n"
            "Enable your terminal app (e.g. Terminal, iTerm2), then re-run."
        )
        sys.exit(1)

    print("Window Manager running. Active shortcuts:")
    for s in SHORTCUTS:
        print(s)
    print("\nPress Ctrl+C to quit.\n")

    listener = start_listener()
    listener.start()
    listener.join()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests — expect pass**

```bash
pytest tests/ -v
```

Expected: all 16 tests pass.

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_main.py
git commit -m "feat: main entry point with permission check"
```

---

## Task 7: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

````markdown
# window-manager

A lightweight macOS window manager inspired by [Magnet](https://magnet.crowdcafe.com/). Snap any window to halves or fullscreen using keyboard shortcuts — no App Store required.

## Requirements

- macOS 12 or later
- Python 3.9+

## Installation

### 1. Clone the repo

```bash
git clone <repo-url>
cd window-manager
```

### 2. Create a virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Grant Accessibility permission

The app controls other windows via macOS's Accessibility API. You must grant permission once:

1. Open **System Settings → Privacy & Security → Accessibility**
2. Click the **+** button
3. Add your terminal app (e.g. **Terminal**, **iTerm2**, **Warp**)
4. Make sure the toggle is **enabled**

> Without this permission the app exits immediately with an error message.

## Usage

```bash
source .venv/bin/activate
python3 main.py
```

You should see:

```
Window Manager running. Active shortcuts:
  ⌃⌥←   Snap left
  ⌃⌥→   Snap right
  ⌃⌥↑   Snap top
  ⌃⌥↓   Snap bottom
  ⌃⌥↩   Fullscreen

Press Ctrl+C to quit.
```

Press **Ctrl+C** in the terminal to stop it.

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `⌃⌥←` (Control + Option + Left) | Snap to left half |
| `⌃⌥→` (Control + Option + Right) | Snap to right half |
| `⌃⌥↑` (Control + Option + Up) | Snap to top half |
| `⌃⌥↓` (Control + Option + Down) | Snap to bottom half |
| `⌃⌥↩` (Control + Option + Enter) | Fullscreen (respects menu bar & Dock) |

## How It Works

1. **`src/window_controller.py`** — reads the focused window and screen frame using the macOS Accessibility API (`ApplicationServices` framework via `pyobjc`), then sets the window's position and size.
2. **`src/hotkeys.py`** — maps key combinations to controller functions using `pynput.keyboard.GlobalHotKeys`.
3. **`main.py`** — verifies the Accessibility permission at startup, then starts the listener and blocks until Ctrl+C.

## Running Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

Tests mock all pyobjc calls so they run without macOS framework dependencies or Accessibility permissions.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Accessibility permission required` on startup | Follow the Installation step 3 above |
| Shortcut doesn't work | Make sure the terminal running `main.py` has Accessibility access; some apps block shortcut capture |
| Window doesn't move | Some windows (e.g. full-screen spaces) are not resizable via the Accessibility API — this is expected |
| `ModuleNotFoundError: ApplicationServices` | Run `pip install -r requirements.txt` inside the virtualenv |
````

- [ ] **Step 2: Run tests one final time**

```bash
pytest tests/ -v
```

Expected: all 16 tests pass, no warnings.

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with full usage guide"
```
