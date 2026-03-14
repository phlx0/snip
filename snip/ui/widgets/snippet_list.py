from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static

from snip.models.snippet import Snippet


class SnippetItem(ListItem):
    """A single row in the snippet list."""

    DEFAULT_CSS = """
    SnippetItem {
        height: 3;
        padding: 0 1;
    }
    SnippetItem:hover {
        background: $boost;
    }
    SnippetItem.-selected {
        background: $accent 20%;
    }
    SnippetItem > .item-title {
        text-style: bold;
    }
    SnippetItem > .item-meta {
        color: $text-muted;
    }
    """

    def __init__(self, snippet: Snippet) -> None:
        super().__init__()
        self.snippet = snippet

    def compose(self) -> ComposeResult:
        pin = " 📌" if self.snippet.pinned else ""
        yield Static(f"{self.snippet.title}{pin}", classes="item-title")
        meta = f"[dim]{self.snippet.language}[/dim]"
        if self.snippet.tags:
            meta += f"  [dim cyan]{self.snippet.tags_display}[/dim cyan]"
        yield Static(meta, markup=True, classes="item-meta")


class SnippetList(Widget):
    """Left-panel: searchable, navigable list of snippets."""

    COMPONENT_CLASSES = {"snippet-list--empty"}

    DEFAULT_CSS = """
    SnippetList {
        width: 35%;
        border-right: tall $panel;
    }
    SnippetList ListView {
        height: 1fr;
    }
    SnippetList .empty-label {
        color: $text-muted;
        text-align: center;
        padding: 2;
    }
    """

    snippets: reactive[list[Snippet]] = reactive([], layout=True)

    def compose(self) -> ComposeResult:
        yield ListView(id="list-view")

    def watch_snippets(self, snippets: list[Snippet]) -> None:
        lv: ListView = self.query_one("#list-view", ListView)
        lv.clear()
        if snippets:
            for s in snippets:
                lv.append(SnippetItem(s))
        else:
            lv.append(ListItem(Static("No snippets found.", classes="empty-label")))

    def highlighted_snippet(self) -> Snippet | None:
        lv: ListView = self.query_one("#list-view", ListView)
        if lv.highlighted_child is None:
            return None
        item = lv.highlighted_child
        if isinstance(item, SnippetItem):
            return item.snippet
        return None

    def move_down(self) -> None:
        self.query_one("#list-view", ListView).action_cursor_down()

    def move_up(self) -> None:
        self.query_one("#list-view", ListView).action_cursor_up()
