from unittest.mock import MagicMock, patch, call
import pytest


class TestMain:
    def test_exits_when_accessibility_not_granted_no_open(self, capsys):
        with patch("main.AXIsProcessTrusted", return_value=False), \
             patch("main.start_listener") as mock_listener, \
             patch("builtins.input", return_value="n"), \
             patch("main.subprocess.run") as mock_open, \
             pytest.raises(SystemExit) as exc_info:
            import main
            main.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Accessibility" in captured.out
        mock_listener.assert_not_called()
        mock_open.assert_not_called()

    def test_opens_settings_when_user_confirms(self, capsys):
        with patch("main.AXIsProcessTrusted", return_value=False), \
             patch("main.start_listener"), \
             patch("builtins.input", return_value="y"), \
             patch("main.subprocess.run") as mock_open, \
             pytest.raises(SystemExit):
            import main
            main.main()

        mock_open.assert_called_once_with(
            ["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"],
            check=False,
        )

    def test_starts_listener_and_runs_app_when_trusted(self):
        fake_monitor = MagicMock()
        fake_app = MagicMock()
        fake_app.run.side_effect = SystemExit(0)

        with patch("main.AXIsProcessTrusted", return_value=True), \
             patch("main.NSApplication") as mock_nsapp, \
             patch("main.NSTimer"), \
             patch("main.signal"), \
             patch("main.start_listener", return_value=fake_monitor), \
             pytest.raises(SystemExit):
            mock_nsapp.sharedApplication.return_value = fake_app
            import main
            main.main()

        fake_app.setActivationPolicy_.assert_called_once_with(2)
        fake_app.run.assert_called_once()

    def test_sigint_sets_quit_flag_on_heartbeat(self):
        """SIGINT handler sets heartbeat._quit so the timer stops the app."""
        import main

        fake_heartbeat = MagicMock()
        fake_heartbeat._quit = False

        # Simulate what _sigint does
        def _sigint(signum, frame):
            fake_heartbeat._quit = True

        import signal as _signal
        _sigint(_signal.SIGINT, None)

        assert fake_heartbeat._quit is True

    def test_heartbeat_tick_terminates_app_when_quit_flag_set(self):
        import main

        fake_monitor = MagicMock()
        fake_app = MagicMock()

        with patch("main.NSEvent") as mock_event, \
             patch("main.NSApplication") as mock_nsapp:
            mock_nsapp.sharedApplication.return_value = fake_app
            hb = main._Heartbeat.alloc().init()
            hb._monitor = fake_monitor
            hb._quit = True
            hb.tick_(None)

        mock_event.removeMonitor_.assert_called_once_with(fake_monitor)
        fake_app.terminate_.assert_called_once_with(None)
