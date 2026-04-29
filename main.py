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
    try:
        listener.start()
        listener.join()
    except KeyboardInterrupt:
        listener.stop()
        print("\nStopped.")


if __name__ == "__main__":
    main()
