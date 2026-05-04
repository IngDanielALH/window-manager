from unittest.mock import MagicMock
import pytest
import src.hotkeys as hk


class TestKeymaps:
    def test_keycode_map_has_7_special_keys(self):
        assert len(hk.KEYCODE_MAP) == 7  # 4 arrows + enter + 2 display shifts

    def test_char_map_has_11_letter_keys(self):
        assert len(hk.CHAR_MAP) == 11  # u i j k d f g e r t c

    def test_all_keycode_map_values_are_callable(self):
        for key, action in hk.KEYCODE_MAP.items():
            assert callable(action), f"{key} maps to non-callable"

    def test_all_char_map_values_are_callable(self):
        for key, action in hk.CHAR_MAP.items():
            assert callable(action), f"{key} maps to non-callable"

    def test_display_shifts_require_ctrl_opt_shift(self):
        shift_entries = [k for k in hk.KEYCODE_MAP if k[0] == hk._CTRL_OPT_SHIFT]
        assert len(shift_entries) == 2  # next and prev display

    def test_start_listener_registers_nsmonitor(self):
        import sys
        appkit = sys.modules["AppKit"]
        fake_monitor = MagicMock()
        appkit.NSEvent.addGlobalMonitorForEventsMatchingMask_handler_.return_value = fake_monitor

        result = hk.start_listener()

        appkit.NSEvent.addGlobalMonitorForEventsMatchingMask_handler_.assert_called_once_with(
            appkit.NSEventMaskKeyDown, hk._handle_event
        )
        assert result is fake_monitor


class TestHandleEvent:
    def _make_event(self, flags, key_code, char=None):
        event = MagicMock()
        event.modifierFlags.return_value = flags
        event.keyCode.return_value = key_code
        event.charactersIgnoringModifiers.return_value = char
        return event

    def test_dispatches_special_key_by_key_code(self, monkeypatch):
        mock_action = MagicMock()
        monkeypatch.setitem(hk.KEYCODE_MAP, (hk._CTRL_OPT, 9999), mock_action)

        event = self._make_event(hk._CTRL_OPT | 0xFF, 9999, char=None)
        hk._handle_event(event)

        mock_action.assert_called_once()

    def test_dispatches_letter_key_by_character(self, monkeypatch):
        mock_action = MagicMock()
        monkeypatch.setitem(hk.CHAR_MAP, (hk._CTRL_OPT, 'z'), mock_action)

        # Key code doesn't match anything; character 'z' should match
        event = self._make_event(hk._CTRL_OPT, 99999, char='z')
        hk._handle_event(event)

        mock_action.assert_called_once()

    def test_character_matching_is_case_insensitive(self, monkeypatch):
        mock_action = MagicMock()
        monkeypatch.setitem(hk.CHAR_MAP, (hk._CTRL_OPT, 'u'), mock_action)

        event = self._make_event(hk._CTRL_OPT, 99999, char='U')
        hk._handle_event(event)

        mock_action.assert_called_once()

    def test_key_code_takes_priority_over_character(self, monkeypatch):
        mock_keycode = MagicMock()
        mock_char = MagicMock()
        monkeypatch.setitem(hk.KEYCODE_MAP, (hk._CTRL_OPT, 123), mock_keycode)
        monkeypatch.setitem(hk.CHAR_MAP, (hk._CTRL_OPT, 'x'), mock_char)

        event = self._make_event(hk._CTRL_OPT, 123, char='x')
        hk._handle_event(event)

        mock_keycode.assert_called_once()
        mock_char.assert_not_called()

    def test_ignores_unregistered_event(self):
        event = self._make_event(0, 9998, char=None)
        hk._handle_event(event)  # must not raise
