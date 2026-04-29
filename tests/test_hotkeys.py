from unittest.mock import MagicMock
import pytest
import src.hotkeys as hk


class TestKeyMap:
    def test_all_18_entries_registered(self):
        assert len(hk.KEY_MAP) == 18

    def test_key_map_values_are_callable(self):
        for key, action in hk.KEY_MAP.items():
            assert callable(action), f"{key} maps to non-callable"

    def test_ctrl_opt_shift_entries_use_correct_modifier(self):
        # next/prev display must include shift
        assert (_CTRL_OPT_SHIFT := hk._CTRL_OPT_SHIFT)
        shift_entries = [(flags, kc) for flags, kc in hk.KEY_MAP if flags == hk._CTRL_OPT_SHIFT]
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
    def test_dispatches_matching_action(self, monkeypatch):
        mock_action = MagicMock()
        monkeypatch.setitem(hk.KEY_MAP, (hk._CTRL_OPT, 9999), mock_action)

        fake_event = MagicMock()
        # Extra bits in modifierFlags should be stripped by _MOD_MASK
        fake_event.modifierFlags.return_value = hk._CTRL_OPT | 0xFF
        fake_event.keyCode.return_value = 9999

        hk._handle_event(fake_event)
        mock_action.assert_called_once()

    def test_ignores_unregistered_key(self):
        fake_event = MagicMock()
        fake_event.modifierFlags.return_value = 0
        fake_event.keyCode.return_value = 9998
        hk._handle_event(fake_event)  # must not raise
