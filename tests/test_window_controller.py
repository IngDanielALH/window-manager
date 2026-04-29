from unittest.mock import MagicMock, patch, call
import pytest


def _make_frame(x, y, w, h):
    frame = MagicMock()
    frame.origin.x = x
    frame.origin.y = y
    frame.size.width = w
    frame.size.height = h
    return frame


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

        fake_system = MagicMock()
        fake_app = MagicMock()
        fake_window = MagicMock()

        ax.AXUIElementCreateSystemWide.return_value = fake_system
        ax.AXUIElementCopyAttributeValue.reset_mock()
        ax.AXUIElementCopyAttributeValue.side_effect = [
            (ax.kAXErrorSuccess, fake_app),
            (ax.kAXErrorSuccess, fake_window),
        ]

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        ax.AXUIElementCreateSystemWide.assert_called()
        assert result is fake_window

    def test_returns_none_when_no_focused_app(self):
        import sys
        ax = sys.modules["ApplicationServices"]

        ax.AXUIElementCreateSystemWide.return_value = MagicMock()
        ax.AXUIElementCopyAttributeValue.reset_mock()
        ax.AXUIElementCopyAttributeValue.side_effect = [(1, None)]

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None

    def test_returns_none_on_ax_error(self):
        import sys
        ax = sys.modules["ApplicationServices"]

        ax.AXUIElementCreateSystemWide.return_value = MagicMock()
        ax.AXUIElementCopyAttributeValue.reset_mock()
        ax.AXUIElementCopyAttributeValue.side_effect = [
            (ax.kAXErrorSuccess, MagicMock()),
            (1, None),
        ]

        from src.window_controller import _get_focused_window
        result = _get_focused_window()

        assert result is None


class TestSnapFunctions:
    # SCREEN = (x, y, w, h) — values chosen for clean division by 2, 3, 6
    SCREEN = (0, 0, 1920, 1200)

    def _setup(self, monkeypatch):
        import src.window_controller as wc
        fake_window = MagicMock()
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_frame_for_window", lambda w: self.SCREEN)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        return fake_window, mock_move

    @pytest.mark.parametrize("fn_name,expected", [
        # Halves
        ("snap_left",            (0,    0,    960,  1200)),
        ("snap_right",           (960,  0,    960,  1200)),
        ("snap_top",             (0,    600,  1920, 600)),
        ("snap_bottom",          (0,    0,    1920, 600)),
        ("snap_fullscreen",      (0,    0,    1920, 1200)),
        # Quarters
        ("snap_top_left",        (0,    600,  960,  600)),
        ("snap_top_right",       (960,  600,  960,  600)),
        ("snap_bottom_left",     (0,    0,    960,  600)),
        ("snap_bottom_right",    (960,  0,    960,  600)),
        # Thirds
        ("snap_left_third",      (0,    0,    640,  1200)),
        ("snap_center_third",    (640,  0,    640,  1200)),
        ("snap_right_third",     (1280, 0,    640,  1200)),
        # Two Thirds
        ("snap_left_two_thirds",   (0,   0,    1280, 1200)),
        ("snap_center_two_thirds", (320, 0,    1280, 1200)),
        ("snap_right_two_thirds",  (640, 0,    1280, 1200)),
    ])
    def test_snap_positions(self, monkeypatch, fn_name, expected):
        import src.window_controller as wc
        w, move = self._setup(monkeypatch)
        getattr(wc, fn_name)()
        move.assert_called_once_with(w, *expected)

    def test_snap_skips_when_no_window(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: None)
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        for fn in [wc.snap_left, wc.snap_right, wc.snap_top, wc.snap_bottom,
                   wc.snap_fullscreen, wc.snap_top_left, wc.snap_top_right,
                   wc.snap_bottom_left, wc.snap_bottom_right,
                   wc.snap_left_third, wc.snap_center_third, wc.snap_right_third,
                   wc.snap_left_two_thirds, wc.snap_center_two_thirds, wc.snap_right_two_thirds]:
            fn()
        mock_move.assert_not_called()


class TestSnapCenter:
    SCREEN = (0, 0, 1920, 1200)

    def test_centers_window_without_resizing(self, monkeypatch):
        import sys
        import src.window_controller as wc
        ax = sys.modules["ApplicationServices"]
        quartz = sys.modules["Quartz"]

        fake_window = MagicMock()
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_frame_for_window", lambda w: self.SCREEN)
        monkeypatch.setattr(wc, "_get_window_size", lambda w: (800, 600))

        ax.AXUIElementSetAttributeValue.reset_mock()
        ax.AXValueCreate.reset_mock(side_effect=True)
        quartz.CGPoint.reset_mock()

        wc.snap_center()

        # Window 800x600 centered on 1920x1200 → x=560, y=300
        quartz.CGPoint.assert_called_once_with(560.0, 300.0)
        ax.AXUIElementSetAttributeValue.assert_called_once()

    def test_skips_when_no_window(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: None)
        mock_set = MagicMock()
        monkeypatch.setattr(wc, "_set_window_position", mock_set)
        wc.snap_center()
        mock_set.assert_not_called()

    def test_skips_when_size_unavailable(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: MagicMock())
        monkeypatch.setattr(wc, "_frame_for_window", lambda w: self.SCREEN)
        monkeypatch.setattr(wc, "_get_window_size", lambda w: None)
        mock_set = MagicMock()
        monkeypatch.setattr(wc, "_set_window_position", mock_set)
        wc.snap_center()
        mock_set.assert_not_called()


class TestDisplaySnaps:
    def _make_screen(self, x, y, w, h):
        screen = MagicMock()
        screen.visibleFrame.return_value.origin.x = x
        screen.visibleFrame.return_value.origin.y = y
        screen.visibleFrame.return_value.size.width = w
        screen.visibleFrame.return_value.size.height = h
        return screen

    def test_next_display_moves_to_next_screen(self, monkeypatch):
        import src.window_controller as wc
        fake_window = MagicMock()
        screens = [self._make_screen(0, 0, 1920, 1200),
                   self._make_screen(1920, 0, 2560, 1440)]
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_screen_index_for_window", lambda w: (0, screens))
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        wc.snap_next_display()
        mock_move.assert_called_once_with(fake_window, 1920, 0, 2560, 1440)

    def test_prev_display_moves_to_previous_screen(self, monkeypatch):
        import src.window_controller as wc
        fake_window = MagicMock()
        screens = [self._make_screen(0, 0, 1920, 1200),
                   self._make_screen(1920, 0, 2560, 1440)]
        monkeypatch.setattr(wc, "_get_focused_window", lambda: fake_window)
        monkeypatch.setattr(wc, "_screen_index_for_window", lambda w: (1, screens))
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        wc.snap_prev_display()
        mock_move.assert_called_once_with(fake_window, 0, 0, 1920, 1200)

    def test_skips_when_single_display(self, monkeypatch):
        import src.window_controller as wc
        monkeypatch.setattr(wc, "_get_focused_window", lambda: MagicMock())
        monkeypatch.setattr(wc, "_screen_index_for_window",
                            lambda w: (0, [MagicMock()]))
        mock_move = MagicMock()
        monkeypatch.setattr(wc, "_move_window", mock_move)
        wc.snap_next_display()
        wc.snap_prev_display()
        mock_move.assert_not_called()
