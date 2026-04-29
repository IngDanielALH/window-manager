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

        ax.AXUIElementSetAttributeValue.reset_mock()
        ax.AXValueCreate.reset_mock()
        ax.AXValueCreate.side_effect = [fake_pos_val, fake_size_val]

        from src.window_controller import _move_window
        _move_window(fake_window, 10, 20, 960, 1057)

        quartz.CGPoint.assert_called_once_with(10, 20)
        quartz.CGSize.assert_called_once_with(960, 1057)
        expected_calls = [
            call(fake_window, ax.kAXPositionAttribute, fake_pos_val),
            call(fake_window, ax.kAXSizeAttribute, fake_size_val),
        ]
        assert ax.AXUIElementSetAttributeValue.call_args_list == expected_calls


class TestGetFocusedWindow:
    def test_returns_window_on_success(self):
        import sys
        ax = sys.modules["ApplicationServices"]
        appkit = sys.modules["AppKit"]

        fake_pid = 1234
        fake_app_element = MagicMock()
        fake_window = MagicMock()

        appkit.NSWorkspace.reset_mock()
        ax.AXUIElementCreateApplication.reset_mock()
        ax.AXUIElementCopyAttributeValue.reset_mock()

        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value.processIdentifier.return_value = fake_pid
        ax.AXUIElementCreateApplication.return_value = fake_app_element
        ax.AXUIElementCopyAttributeValue.return_value = (ax.kAXErrorSuccess, fake_window)

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        ax.AXUIElementCreateApplication.assert_called_once_with(fake_pid)
        assert result is fake_window

    def test_returns_none_when_no_frontmost_app(self):
        import sys
        appkit = sys.modules["AppKit"]
        appkit.NSWorkspace.reset_mock()
        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value = None

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None

    def test_returns_none_on_ax_error(self):
        import sys
        ax = sys.modules["ApplicationServices"]
        appkit = sys.modules["AppKit"]

        appkit.reset_mock()
        ax.AXUIElementCopyAttributeValue.reset_mock()

        fake_app = MagicMock()
        fake_app.processIdentifier.return_value = 42
        appkit.NSWorkspace.sharedWorkspace.return_value.frontmostApplication.return_value = fake_app
        ax.AXUIElementCopyAttributeValue.return_value = (1, None)  # non-zero = error

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None


class TestSnapFunctions:
    """Each snap function: get window, compute target frame, call _move_window."""

    SCREEN = (0, 23, 1920, 1057)  # x, y, w, h from visibleFrame

    def _setup(self, monkeypatch):
        import src.window_controller as wc
        fake_window = MagicMock()
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_get_screen_frame", lambda: self.SCREEN)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        return fake_window, mock_move

    def test_snap_left(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_left()
        move.assert_called_once_with(w, 0, 23, 960, 1057)

    def test_snap_right(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_right()
        move.assert_called_once_with(w, 960, 23, 960, 1057)

    def test_snap_top(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_top()
        move.assert_called_once_with(w, 0, 23 + 528.5, 1920, 528.5)

    def test_snap_bottom(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_bottom()
        move.assert_called_once_with(w, 0, 23, 1920, 528.5)

    def test_snap_fullscreen(self, monkeypatch):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        wc.snap_fullscreen()
        move.assert_called_once_with(w, 0, 23, 1920, 1057)

    def test_snap_skips_when_no_window(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: None)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        wc.snap_left()
        mock_move.assert_not_called()
