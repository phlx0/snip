from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from snip.models.snippet import Snippet


_LANG_MAP: dict[str, str] = {
    "bash": "bash",
    "c": "c",
    "cpp": "cpp",
    "css": "css",
    "dockerfile": "dockerfile",
    "go": "go",
    "html": "html",
    "java": "java",
    "javascript": "javascript",
    "json": "json",
    "kotlin": "kotlin",
    "markdown": "markdown",
    "php": "php",
    "powershell": "powershell",
    "python": "python",
    "ruby": "ruby",
    "rust": "rust",
    "sql": "sql",
    "swift": "swift",
    "toml": "toml",
    "typescript": "typescript",
    "yaml": "yaml",
    "text": "text",
}


class SnippetPreview(Widget):
    """Right-panel: syntax-highlighted code preview."""

    snippet: reactive[Snippet | None] = reactive(None, layout=True)

    def compose(self) -> ComposeResult:
        yield Static("", id="preview-header")
        with Vertical(classes="preview-code-wrap", id="preview-code-wrap"):
            yield Static("", id="preview-code")
        yield Static("", id="preview-footer")

    def watch_snippet(self, snippet: Snippet | None) -> None:
        if snippet is None:
            self._show_empty()
        else:
            self._render_snippet(snippet)

    def _show_empty(self) -> None:
        from rich.text import Text

        self.query_one("#preview-header", Static).update(
            Text("select a snippet to preview", style="#2a2c42")
        )
        self.query_one("#preview-footer", Static).update("")
        self.query_one("#preview-code-wrap").display = False

    def _render_snippet(self, snippet: Snippet) -> None:
        from rich.text import Text

        # Build a single multi-line header: pin + title + description + tags
        header = Text()
        if snippet.pinned:
            header.append("\u2605 pinned\n", style="bold #bb9af7")
        header.append(snippet.title, style="bold #e0e7ff")
        if snippet.description:
            header.append("\n" + snippet.description, style="#565f89")
        if snippet.tags:
            header.append("\n" + snippet.tags_display, style="#73daca")
        self.query_one("#preview-header", Static).update(header)

        # Code block
        self.query_one("#preview-code-wrap").display = True
        self._render_code(snippet)

        # Footer meta line
        created = snippet.created_at.strftime("%Y-%m-%d") if snippet.created_at else ""
        updated = snippet.updated_at.strftime("%Y-%m-%d") if snippet.updated_at else ""
        meta = f"{snippet.language}  \u00b7  {created}"
        if updated and updated != created:
            meta += f"  \u00b7  updated {updated}"
        self.query_one("#preview-footer", Static).update(Text(meta, style="#565f89"))

    def _render_code(self, snippet: Snippet) -> None:
        try:
            from rich.syntax import Syntax

            syntax = Syntax(
                snippet.content,
                _LANG_MAP.get(snippet.language, "text"),
                theme="nord",
                line_numbers=True,
                word_wrap=False,
            )
            self.query_one("#preview-code", Static).update(syntax)
        except Exception:
            self.query_one("#preview-code", Static).update(snippet.content)
