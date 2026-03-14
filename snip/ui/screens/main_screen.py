from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, ListView, Static

from snip.models.snippet import Snippet
from snip.ui.widgets.snippet_list import SnippetItem, SnippetList
from snip.ui.widgets.snippet_preview import SnippetPreview


class MainScreen(Screen):
    """The primary TUI screen."""

    MIN_WIDTH = 60
    MIN_HEIGHT = 12

    BINDINGS = [
        Binding("j", "move_down", "Down", show=False),
        Binding("k", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False, priority=True),
        Binding("up", "move_up", "Up", show=False, priority=True),
        Binding("n", "new_snippet", "New"),
        Binding("e", "edit_snippet", "Edit"),
        Binding("d", "delete_snippet", "Delete"),
        Binding("y", "yank_snippet", "Copy"),
        Binding("p", "pin_snippet", "Pin"),
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear", show=False),
        Binding("q", "quit", "Quit"),
    ]

    DEFAULT_CSS = """
    MainScreen {
        background: $surface;
        layers: base overlay;
    }
    MainScreen .search-bar {
        height: 3;
        border-bottom: tall $panel;
        padding: 0 1;
        overflow: hidden;
    }
    MainScreen Input {
        border: none;
        background: transparent;
        height: 1;
        padding: 1 0;
        width: 1fr;
        min-width: 8;
    }
    MainScreen .search-label {
        color: $accent;
        width: auto;
        min-width: 2;
        padding: 1 1 1 0;
    }
    MainScreen .status-bar {
        height: 1;
        background: $panel;
        padding: 0 1;
        color: $text-muted;
    }
    MainScreen .panels {
        height: 1fr;
        min-height: 4;
    }
    MainScreen #too-small-overlay {
        layer: overlay;
        display: none;
        width: 100%;
        height: 100%;
        background: $surface;
        align: center middle;
    }
    MainScreen #too-small-overlay Static {
        color: $warning;
        text-align: center;
        width: auto;
    }
    """

    def __init__(self, db) -> None:  # type: ignore[override]
        super().__init__()
        self._db = db
        self._query = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(classes="search-bar"):
            yield Label("/", classes="search-label")
            yield Input(placeholder="Search snippets…", id="search-input")
        with Horizontal(classes="panels"):
            yield SnippetList(id="snippet-list")
            yield SnippetPreview(id="snippet-preview")
        yield Label("", id="status-bar", classes="status-bar")
        yield Footer()
        with Vertical(id="too-small-overlay"):
            yield Static(
                f"Terminal too small\nMinimum size: {self.MIN_WIDTH}\u00d7{self.MIN_HEIGHT}"
            )

    def on_mount(self) -> None:
        self._refresh_list()
        self.query_one("#snippet-list", SnippetList).query_one(
            "#list-view", ListView
        ).focus()

    def on_resize(self, event) -> None:  # type: ignore[override]
        too_small = event.size.width < self.MIN_WIDTH or event.size.height < self.MIN_HEIGHT
        self.query_one("#too-small-overlay").display = too_small

    # ------------------------------------------------------------------
    # List / search helpers
    # ------------------------------------------------------------------

    def _refresh_list(self, query: str = "") -> None:
        snippets = self._db.search(query) if query else self._db.get_all()
        sl: SnippetList = self.query_one("#snippet-list", SnippetList)
        sl.snippets = snippets

        if snippets:
            self._update_preview(snippets[0])
        else:
            self.query_one("#snippet-preview", SnippetPreview).snippet = None

        self._update_status(len(snippets), self._db.count())

    def _update_preview(self, snippet: Snippet | None) -> None:
        self.query_one("#snippet-preview", SnippetPreview).snippet = snippet

    def _update_status(self, shown: int, total: int) -> None:
        count = f"  {shown}/{total} snippet{'s' if total != 1 else ''}"
        filt = f'  \u00b7  filter: "{self._query}"' if self._query else ""
        self.query_one("#status-bar", Label).update(count + filt)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._query = event.value
            self._refresh_list(self._query)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        if isinstance(event.item, SnippetItem):
            self._update_preview(event.item.snippet)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def action_move_down(self) -> None:
        self.query_one("#snippet-list", SnippetList).move_down()

    def action_move_up(self) -> None:
        self.query_one("#snippet-list", SnippetList).move_up()

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_clear_search(self) -> None:
        inp = self.query_one("#search-input", Input)
        if inp.value:
            inp.clear()
            self._query = ""
            self._refresh_list()
        else:
            self.query_one("#snippet-list", SnippetList).query_one(
                "#list-view", ListView
            ).focus()

    def action_new_snippet(self) -> None:
        from snip.ui.screens.edit_screen import EditScreen

        def _on_result(result: Snippet | None) -> None:
            if result is not None:
                self._db.create(result)
                self._refresh_list(self._query)
                self._flash(f"Created '{result.title}'")

        self.app.push_screen(EditScreen(), _on_result)

    def action_edit_snippet(self) -> None:
        from snip.ui.screens.edit_screen import EditScreen

        snippet = self.query_one("#snippet-list", SnippetList).highlighted_snippet()
        if snippet is None:
            return

        def _on_result(result: Snippet | None) -> None:
            if result is not None:
                self._db.update(result)
                self._refresh_list(self._query)
                self._flash(f"Updated '{result.title}'")

        self.app.push_screen(EditScreen(snippet), _on_result)

    def action_delete_snippet(self) -> None:
        snippet = self.query_one("#snippet-list", SnippetList).highlighted_snippet()
        if snippet is None or snippet.id is None:
            return
        self._db.delete(snippet.id)
        self._refresh_list(self._query)
        self._flash(f"Deleted '{snippet.title}'")

    def action_yank_snippet(self) -> None:
        snippet = self.query_one("#snippet-list", SnippetList).highlighted_snippet()
        if snippet is None:
            return
        from snip.utils.clipboard import copy_to_clipboard

        if copy_to_clipboard(snippet.content):
            self._flash(f"Copied '{snippet.title}' to clipboard")
        else:
            self._flash("Clipboard not available \u2013 install pyperclip")

    def action_pin_snippet(self) -> None:
        snippet = self.query_one("#snippet-list", SnippetList).highlighted_snippet()
        if snippet is None or snippet.id is None:
            return
        pinned = self._db.toggle_pin(snippet.id)
        self._refresh_list(self._query)
        state = "pinned" if pinned else "unpinned"
        self._flash(f"{snippet.title!r} {state}")

    def action_quit(self) -> None:
        self.app.exit()

    def _flash(self, msg: str) -> None:
        self.query_one("#status-bar", Label).update(f"  \u2713 {msg}")
