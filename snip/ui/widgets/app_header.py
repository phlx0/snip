from __future__ import annotations

import datetime

from rich.table import Table
from rich.text import Text
from textual.widgets import Static


class AppHeader(Static):
    """Branded header: ◆ snip logo on the left, live clock on the right."""

    def on_mount(self) -> None:
        self.set_interval(1.0, self._tick)
        self._tick()

    def _tick(self) -> None:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(justify="right")
        logo = Text.assemble(
            ("\u25c6 ", "bold #7aa2f7"),
            ("snip", "bold #c0caf5"),
            ("  \u00b7  terminal snippet vault", "#3b3f5c"),
        )
        grid.add_row(logo, Text(now, style="#3b3f5c"))
        self.update(grid)
