from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static

from snip.models.snippet import Snippet


class SnippetItem(ListItem):
    """A single row in the snippet list."""

    def __init__(self, snippet: Snippet) -> None:
        super().__init__()
        self.snippet = snippet

    def compose(self) -> ComposeResult:
        from snip import themes
        t = themes.current
        pin = f"[bold {t.purple}]\u2605 [/bold {t.purple}]" if self.snippet.pinned else ""
        yield Static(
            f"{pin}[bold]{self.snippet.title}[/bold]",
            markup=True,
            classes="item-title",
        )
        lang = f"[{t.text_muted}]{self.snippet.language}[/{t.text_muted}]"
        tags = (
            f"  [{t.teal}]{self.snippet.tags_display}[/{t.teal}]"
            if self.snippet.tags
            else ""
        )
        yield Static(lang + tags, markup=True, classes="item-meta")


class SnippetList(Widget):
    """Left-panel: navigable list of snippets."""

    snippets: reactive[list[Snippet]] = reactive([], layout=True)

    def compose(self) -> ComposeResult:
        yield Static("SNIPPETS", classes="panel-label")
        yield ListView(id="list-view")

    def watch_snippets(self, snippets: list[Snippet]) -> None:
        lv: ListView = self.query_one("#list-view", ListView)
        lv.clear()
        if snippets:
            for s in snippets:
                lv.append(SnippetItem(s))
        else:
            lv.append(ListItem(Static("no snippets found", classes="empty-label")))

    def highlighted_snippet(self) -> Snippet | None:
        lv: ListView = self.query_one("#list-view", ListView)
        if lv.highlighted_child is None:
            return None
        item = lv.highlighted_child
        if isinstance(item, SnippetItem):
            return item.snippet
        return None

    def highlight_by_id(self, snippet_id: str | None) -> None:
        """Move the list cursor to the item matching snippet_id."""
        if snippet_id is None:
            return
        lv = self.query_one("#list-view", ListView)
        for i, child in enumerate(lv.children):
            if isinstance(child, SnippetItem) and child.snippet.id == snippet_id:
                lv.index = i
                return

    def move_down(self) -> None:
        self.query_one("#list-view", ListView).action_cursor_down()

    def move_up(self) -> None:
        self.query_one("#list-view", ListView).action_cursor_up()
