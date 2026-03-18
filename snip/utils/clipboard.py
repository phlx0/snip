from __future__ import annotations

import subprocess
import sys


def copy_to_clipboard(text: str) -> bool:
    """Copy *text* to the system clipboard.

    Returns True on success, False if no clipboard mechanism is available.
    """
    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"snip: pyperclip error — {e}", file=sys.stderr)

    # Fallback: platform native commands
    try:
        if sys.platform == "darwin":
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        if sys.platform == "win32":
            subprocess.run(
                ["clip"], input=text.encode("utf-16"), check=True
            )
            return True
        # Linux – try xclip or xsel
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
            result = subprocess.run(cmd, input=text.encode(), capture_output=True)
            if result.returncode == 0:
                return True
    except Exception as e:
        print(f"snip: clipboard error — {e}", file=sys.stderr)

    return False
