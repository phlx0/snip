from unittest.mock import MagicMock, patch

from snip.utils.clipboard import copy_to_clipboard


class TestCopyToClipboard:
    def test_uses_pyperclip_when_available(self):
        mock_pyperclip = MagicMock()
        with patch.dict("sys.modules", {"pyperclip": mock_pyperclip}):
            result = copy_to_clipboard("hello")
        assert result is True
        mock_pyperclip.copy.assert_called_once_with("hello")

    def test_returns_false_when_no_mechanism(self):
        with patch.dict("sys.modules", {"pyperclip": None}):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                with patch("sys.platform", "linux"):
                    result = copy_to_clipboard("hello")
        assert result is False

    def test_handles_pyperclip_exception_gracefully(self):
        mock_pyperclip = MagicMock()
        mock_pyperclip.copy.side_effect = Exception("clipboard error")
        with patch.dict("sys.modules", {"pyperclip": mock_pyperclip}):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                with patch("sys.platform", "linux"):
                    result = copy_to_clipboard("hello")
        assert result is False
    def test_falls_back_to_xsel_when_xclip_missing(self):
        def fake_run(cmd, **kwargs):
            if cmd[0] == "xclip":
                raise FileNotFoundError
            return MagicMock(returncode=0)

        with patch.dict("sys.modules", {"pyperclip": None}):
            with patch("subprocess.run", side_effect=fake_run):
                with patch("sys.platform", "linux"):
                    result = copy_to_clipboard("hello")
        assert result is True

    def test_uses_xclip_when_xsel_missing(self):
        def fake_run(cmd, **kwargs):
            if cmd[0] == "xclip":
                return MagicMock(returncode=0)
            raise FileNotFoundError

        with patch.dict("sys.modules", {"pyperclip": None}):
            with patch("subprocess.run", side_effect=fake_run):
                with patch("sys.platform", "linux"):
                    result = copy_to_clipboard("hello")
        assert result is True

    def test_returns_false_when_neither_tool_installed(self):
        with patch.dict("sys.modules", {"pyperclip": None}):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                with patch("sys.platform", "linux"):
                    result = copy_to_clipboard("hello")
        assert result is False
