from unittest.mock import MagicMock, patch
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
             patch("main.NSEvent"), \
             patch("main.signal"), \
             patch("main.start_listener", return_value=fake_monitor), \
             pytest.raises(SystemExit):
            mock_nsapp.sharedApplication.return_value = fake_app
            import main
            main.main()

        fake_app.setActivationPolicy_.assert_called_once_with(2)
        fake_app.run.assert_called_once()
