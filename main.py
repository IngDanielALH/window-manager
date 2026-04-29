from ApplicationServices import AXIsProcessTrusted
from AppKit import NSEvent, NSRunLoop, NSDate
from src.hotkeys import start_listener
import subprocess
import sys

SHORTCUTS = [
    "  Halves",
    "    ⌃⌥←       Left        ⌃⌥→       Right",
    "    ⌃⌥↑       Top         ⌃⌥↓       Bottom",
    "  Fullscreen & Center",
    "    ⌃⌥↩       Fullscreen  ⌃⌥C       Center",
    "  Quarters",
    "    ⌃⌥U       Top Left    ⌃⌥I       Top Right",
    "    ⌃⌥J       Bottom Left ⌃⌥K       Bottom Right",
    "  Thirds",
    "    ⌃⌥D       Left        ⌃⌥F       Center      ⌃⌥G       Right",
    "  Two Thirds",
    "    ⌃⌥E       Left        ⌃⌥R       Center      ⌃⌥T       Right",
    "  Displays",
    "    ⌃⌥⇧→      Next        ⌃⌥⇧←      Previous",
]


def main():
    if not AXIsProcessTrusted():
        print(
            "Accessibility permission required.\n"
            "Go to: System Settings → Privacy & Security → Accessibility\n"
            "Enable your terminal app (e.g. Terminal, iTerm2), then re-run.\n"
        )
        answer = input("Open System Settings now? [y/N]: ").strip().lower()
        if answer == "y":
            subprocess.run(
                ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"],
                check=False,
            )
        sys.exit(1)

    print("Window Manager running. Active shortcuts:")
    for s in SHORTCUTS:
        print(s)
    print("\nPress Ctrl+C to quit.\n")

    monitor = start_listener()
    try:
        while True:
            NSRunLoop.mainRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.5))
    except KeyboardInterrupt:
        NSEvent.removeMonitor_(monitor)
        print("\nStopped.")


if __name__ == "__main__":
    main()
