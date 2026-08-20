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
    if sys.platform == "darwin":
        try:
            subprocess.run(["pbcopy"], input=text.encode(), check=True)
            return True
        except Exception as e:
            print(f"snip: clipboard error — {e}", file=sys.stderr)
    elif sys.platform == "win32":
        try:
            subprocess.run(["clip"], input=text.encode("utf-16"), check=True)
            return True
        except Exception as e:
            print(f"snip: clipboard error — {e}", file=sys.stderr)
    else:
        for cmd in (
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
        ):
            try:
                result = subprocess.run(cmd, input=text.encode(), capture_output=True)
                if result.returncode == 0:
                    return True
            except FileNotFoundError:
                continue
            except Exception as e:
                print(f"snip: clipboard error — {e}", file=sys.stderr)
                break

    return False
