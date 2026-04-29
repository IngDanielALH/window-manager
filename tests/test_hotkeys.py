from unittest.mock import MagicMock, patch
import pytest


class TestHotkeyMap:
    def test_all_magnet_shortcuts_are_registered(self):
        with patch("pynput.keyboard") as mock_kb:
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
        with patch("pynput.keyboard"):
            import src.hotkeys as hk
            import importlib
            importlib.reload(hk)

        for combo, action in hk.HOTKEY_MAP.items():
            assert callable(action), f"{combo} maps to non-callable"

    def test_start_listener_returns_globalhotkeys_instance(self):
        with patch("pynput.keyboard") as mock_kb:
            import src.hotkeys as hk
            import importlib
            importlib.reload(hk)

            fake_listener = MagicMock()
            mock_kb.GlobalHotKeys.return_value = fake_listener

            result = hk.start_listener()

            mock_kb.GlobalHotKeys.assert_called_once_with(hk.HOTKEY_MAP)
            assert result is fake_listener
