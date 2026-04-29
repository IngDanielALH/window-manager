# Window Manager — Design Spec
**Date:** 2026-04-29  
**Status:** Approved

## Overview

A lightweight macOS window manager written in Python that replicates Magnet's core snapping behavior using keyboard shortcuts. Runs as a foreground process via `python3 main.py`, no App Store required.

## Goals

- Snap the focused window to left half, right half, top half, bottom half, or fullscreen
- Use the same default keyboard shortcuts as Magnet
- Work with any macOS application
- Zero configuration required to start

## Out of Scope

- Menu bar icon
- Autostart at login
- Window thirds or quarter layouts
- Multi-monitor targeting (uses the screen where the focused window lives)

## Architecture

```
window-manager/
├── main.py                  # Entry point
├── src/
│   ├── window_controller.py # Accessibility API: move and resize windows
│   └── hotkeys.py           # Hotkey map → actions
├── requirements.txt
├── .gitignore
└── README.md
```

## Data Flow

```
Keypress → pynput GlobalHotKeys → hotkeys.py dispatches action
    → window_controller.py reads active screen (NSScreen)
    → gets focused window AXUIElement via Accessibility API
    → computes new frame based on action
    → applies position + size via AXUIElementSetAttributeValue
```

## Modules

### `window_controller.py`

Exposes five public functions:

| Function | Behavior |
|---|---|
| `snap_left()` | Left 50% of screen |
| `snap_right()` | Right 50% of screen |
| `snap_top()` | Top 50% of screen |
| `snap_bottom()` | Bottom 50% of screen |
| `snap_fullscreen()` | 100% of screen (respects menu bar) |

**Implementation detail:** Each function calls `_get_focused_window()` which reads the frontmost app PID via `NSWorkspace.sharedWorkspace().frontmostApplication()`, builds an `AXUIElement` via `AXUIElementCreateApplication(pid)`, and reads the focused window attribute. Screen dimensions come from `NSScreen.mainScreen().visibleFrame()` (excludes Dock and menu bar). Position and size are written via `AXUIElementSetAttributeValue` with `AXValueCreate` wrapping `CGPoint` and `CGSize` values.

### `hotkeys.py`

Dictionary mapping Magnet-compatible combos to controller functions, passed to `pynput.keyboard.GlobalHotKeys`.

| Shortcut | Action |
|---|---|
| `⌃⌥←` (`<ctrl>+<alt>+left`) | `snap_left` |
| `⌃⌥→` (`<ctrl>+<alt>+right`) | `snap_right` |
| `⌃⌥↑` (`<ctrl>+<alt>+up`) | `snap_top` |
| `⌃⌥↓` (`<ctrl>+<alt>+down`) | `snap_bottom` |
| `⌃⌥↩` (`<ctrl>+<alt>+enter`) | `snap_fullscreen` |

### `main.py`

1. Calls `AXIsProcessTrusted()` — if `False`, prints a clear message with instructions to enable Accessibility permissions and exits
2. Instantiates the hotkey listener from `hotkeys.py`
3. Prints a status message with active shortcuts
4. Blocks with `listener.join()`

## Dependencies

```
pyobjc-framework-ApplicationServices
pyobjc-framework-Cocoa
pynput
```

## Permissions

The user must grant Accessibility access once:  
**System Settings → Privacy & Security → Accessibility → enable the terminal app (e.g. iTerm, Terminal)**

The script detects missing permissions at startup and exits with a clear error message.

## Error Handling

- No focused window detected → silently skip (no crash)
- Accessibility permission missing → exit with instructions at startup
- Window that cannot be resized (e.g. fullscreen app) → silently skip
