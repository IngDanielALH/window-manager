from unittest.mock import MagicMock, patch
import pytest


class TestMain:
    def test_exits_when_accessibility_not_granted(self, capsys):
        with patch("main.AXIsProcessTrusted", return_value=False), \
             patch("main.start_listener") as mock_listener, \
             pytest.raises(SystemExit) as exc_info:
            import main
            main.main()

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Accessibility" in captured.out
        mock_listener.assert_not_called()

    def test_starts_listener_when_trusted(self):
        fake_listener = MagicMock()
        with patch("main.AXIsProcessTrusted", return_value=True), \
             patch("main.start_listener", return_value=fake_listener):
            import main
            main.main()

        fake_listener.start.assert_called_once()
        fake_listener.join.assert_called_once()
