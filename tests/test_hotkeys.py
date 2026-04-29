from unittest.mock import MagicMock, patch
import pytest
import src.hotkeys as hk

EXPECTED_SHORTCUTS = [
    "<ctrl>+<alt>+<left>",
    "<ctrl>+<alt>+<right>",
    "<ctrl>+<alt>+<up>",
    "<ctrl>+<alt>+<down>",
    "<ctrl>+<alt>+<enter>",
    "<ctrl>+<alt>+u",
    "<ctrl>+<alt>+i",
    "<ctrl>+<alt>+j",
    "<ctrl>+<alt>+k",
    "<ctrl>+<alt>+d",
    "<ctrl>+<alt>+f",
    "<ctrl>+<alt>+g",
    "<ctrl>+<alt>+e",
    "<ctrl>+<alt>+r",
    "<ctrl>+<alt>+t",
    "<ctrl>+<alt>+c",
    "<ctrl>+<alt>+<shift>+<right>",
    "<ctrl>+<alt>+<shift>+<left>",
]


class TestHotkeyMap:
    def test_all_shortcuts_registered(self):
        keys = list(hk.HOTKEY_MAP.keys())
        for shortcut in EXPECTED_SHORTCUTS:
            assert shortcut in keys, f"Missing shortcut: {shortcut}"

    def test_hotkey_map_values_are_callable(self):
        for combo, action in hk.HOTKEY_MAP.items():
            assert callable(action), f"{combo} maps to non-callable"

    def test_start_listener_returns_globalhotkeys_instance(self):
        fake_listener = MagicMock()
        with patch("src.hotkeys.keyboard") as mock_kb:
            mock_kb.GlobalHotKeys.return_value = fake_listener
            result = hk.start_listener()

        mock_kb.GlobalHotKeys.assert_called_once_with(hk.HOTKEY_MAP)
        assert result is fake_listener
