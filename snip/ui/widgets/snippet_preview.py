from __future__ import annotations

from textual.app import ComposeResult
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

    DEFAULT_CSS = """
    SnippetPreview {
        width: 1fr;
        padding: 0 1;
    }
    SnippetPreview .preview-header {
        color: $text;
        text-style: bold;
        padding: 0 0 1 0;
    }
    SnippetPreview .preview-description {
        color: $text-muted;
        padding: 0 0 1 0;
    }
    SnippetPreview .preview-tags {
        color: $accent;
        padding: 0 0 1 0;
    }
    SnippetPreview .preview-meta {
        color: $text-muted;
        padding: 1 0 0 0;
    }
    SnippetPreview .preview-empty {
        color: $text-muted;
        text-align: center;
        padding: 4 2;
    }
    """

    snippet: reactive[Snippet | None] = reactive(None, layout=True)

    def compose(self) -> ComposeResult:
        yield Static("", id="preview-header", classes="preview-header")
        yield Static("", id="preview-description", classes="preview-description")
        yield Static("", id="preview-tags", classes="preview-tags")
        yield Static("", id="preview-code")
        yield Static("", id="preview-meta", classes="preview-meta")

    def watch_snippet(self, snippet: Snippet | None) -> None:
        if snippet is None:
            self._show_empty()
            return
        self._render_snippet(snippet)

    def _show_empty(self) -> None:
        self.query_one("#preview-header", Static).update(
            "[dim]Select a snippet to preview[/dim]"
        )
        self.query_one("#preview-description", Static).update("")
        self.query_one("#preview-tags", Static).update("")
        self.query_one("#preview-code", Static).update("")
        self.query_one("#preview-meta", Static).update("")

    def _render_snippet(self, snippet: Snippet) -> None:
        pin = " 📌" if snippet.pinned else ""
        self.query_one("#preview-header", Static).update(
            f"[bold]{snippet.title}[/bold]{pin}"
        )

        desc = snippet.description or ""
        self.query_one("#preview-description", Static).update(
            f"[dim]{desc}[/dim]" if desc else ""
        )

        tags_text = snippet.tags_display
        self.query_one("#preview-tags", Static).update(
            f"[cyan]{tags_text}[/cyan]" if tags_text else ""
        )

        self._render_code(snippet)

        created = snippet.created_at.strftime("%Y-%m-%d %H:%M") if snippet.created_at else ""
        updated = snippet.updated_at.strftime("%Y-%m-%d %H:%M") if snippet.updated_at else ""
        self.query_one("#preview-meta", Static).update(
            f"[dim]lang: {snippet.language}  ·  created: {created}  ·  updated: {updated}[/dim]"
        )

    def _render_code(self, snippet: Snippet) -> None:
        try:
            from rich.syntax import Syntax

            lexer = _LANG_MAP.get(snippet.language, "text")
            syntax = Syntax(
                snippet.content,
                lexer,
                theme="monokai",
                line_numbers=True,
                word_wrap=True,
            )
            self.query_one("#preview-code", Static).update(syntax)
        except Exception:
            self.query_one("#preview-code", Static).update(snippet.content)
