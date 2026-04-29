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
