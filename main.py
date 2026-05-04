from ApplicationServices import AXIsProcessTrusted
from AppKit import NSApplication, NSEvent
from Foundation import NSObject, NSTimer
from src.hotkeys import start_listener
import signal
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


class _Heartbeat(NSObject):
    """
    Repeating timer whose sole purpose is to yield back to Python every
    0.5 s so that pending signals (e.g. SIGINT) can be processed.
    NSApp.run() is a C-level blocking call; without this, Ctrl+C is ignored.
    """
    # Set after alloc().init() to avoid custom NSObject init
    _monitor = None
    _quit = False

    def tick_(self, timer):
        if self._quit:
            NSEvent.removeMonitor_(self._monitor)
            NSApplication.sharedApplication().terminate_(None)


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

    # NSApplicationActivationPolicyProhibited (2): no Dock icon, purely background
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(2)

    monitor = start_listener()

    heartbeat = _Heartbeat.alloc().init()
    heartbeat._monitor = monitor
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        0.5, heartbeat, "tick:", None, True
    )

    def _sigint(signum, frame):
        # Set flag — the heartbeat timer will call app.terminate_() on the next tick
        heartbeat._quit = True

    signal.signal(signal.SIGINT, _sigint)

    app.run()
    print("\nStopped.")


if __name__ == "__main__":
    main()
