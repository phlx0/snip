from __future__ import annotations

from pathlib import Path

from textual.app import App

from snip.storage.database import Database
from snip.ui.screens.main_screen import MainScreen


_DEFAULT_DB = Path.home() / ".config" / "snip" / "snip.db"


def _seed_demo(db: Database) -> None:
    """Populate a fresh database with helpful example snippets."""
    from snip.models.snippet import Snippet

    examples: list[Snippet] = [
        Snippet(
            title="List all listening ports",
            content="ss -tlnp\n# or on macOS:\nlsof -iTCP -sTCP:LISTEN -nP",
            language="bash",
            description="Show every port your machine is actively listening on",
            tags=["networking", "ports", "devops"],
            pinned=True,
        ),
        Snippet(
            title="Pretty-print JSON",
            content='cat file.json | python3 -m json.tool\n# or with jq:\ncat file.json | jq .',
            language="bash",
            description="Format messy JSON output",
            tags=["json", "cli", "utils"],
        ),
        Snippet(
            title="Reverse a list (Python)",
            content="items = [1, 2, 3, 4]\nreversed_items = items[::-1]\n\n# Or in-place:\nitems.reverse()",
            language="python",
            description="Reverse a list without importing anything",
            tags=["python", "list"],
        ),
        Snippet(
            title="Git: undo last commit (keep changes)",
            content="git reset --soft HEAD~1",
            language="bash",
            description="Undo a commit but keep your staged changes",
            tags=["git"],
        ),
        Snippet(
            title="Docker: clean up everything",
            content=(
                "# Remove stopped containers, unused images, volumes, networks\n"
                "docker system prune -a --volumes"
            ),
            language="bash",
            description="Free up all Docker disk space",
            tags=["docker", "devops"],
        ),
    ]

    for s in examples:
        db.create(s)


class SnipApp(App):
    """snip — a terminal snippet manager."""

    TITLE = "snip"
    SUB_TITLE = "your terminal snippet vault"

    CSS = """
    Screen {
        background: $surface;
    }
    Header {
        background: $panel;
        color: $text;
    }
    """

    def __init__(self, db_path: Path = _DEFAULT_DB) -> None:
        super().__init__()
        self._db = Database(db_path)
        if self._db.count() == 0:
            _seed_demo(self._db)

    def on_mount(self) -> None:
        self.push_screen(MainScreen(self._db))
