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
