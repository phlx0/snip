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


def _make_syntax(content: str, language: str):
    """Return a Rich Syntax renderable using a Tokyo Night palette."""
    from rich.syntax import Syntax

    try:
        from pygments.style import Style
        from pygments.token import (
            Comment, Generic, Keyword, Name, Number,
            Operator, String, Token,
        )

        class _TokyoNight(Style):
            background_color = "#0a0b14"
            default_style = "#c0caf5"
            styles = {
                Token:              "#c0caf5",
                Comment:            "italic #565f89",
                Keyword:            "#7aa2f7",
                Keyword.Constant:   "#ff9e64",
                Keyword.Type:       "#73daca",
                Name.Builtin:       "#73daca",
                Name.Function:      "#7aa2f7",
                Name.Decorator:     "#bb9af7",
                Name.Exception:     "#f7768e",
                Name.Variable:      "#c0caf5",
                String:             "#9ece6a",
                String.Escape:      "#ff9e64",
                Number:             "#ff9e64",
                Operator:           "#89ddff",
                Operator.Word:      "#7aa2f7",
                Generic.Heading:    "bold #7aa2f7",
                Generic.Subheading: "#73daca",
                Generic.Error:      "#f7768e",
            }

        from rich.syntax import PygmentsSyntaxTheme
        theme = PygmentsSyntaxTheme(_TokyoNight)
    except Exception:
        # If Pygments or PygmentsSyntaxTheme is unavailable, fall back.
        theme = "monokai"  # type: ignore[assignment]

    return Syntax(
        content,
        language,
        theme=theme,
        line_numbers=True,
        word_wrap=False,
    )


class SnippetPreview(Widget):
    """Right-panel: syntax-highlighted code preview."""

    snippet: reactive[Snippet | None] = reactive(None, layout=True)

    def compose(self) -> ComposeResult:
        yield Static("", id="preview-header")
        with Vertical(classes="preview-code-wrap", id="preview-code-wrap"):
            yield Static("", id="preview-code", markup=False)
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

        header = Text()
        if snippet.pinned:
            header.append("\u2605 pinned\n", style="bold #bb9af7")
        header.append(snippet.title, style="bold #e0e7ff")
        if snippet.description:
            header.append("\n" + snippet.description, style="#565f89")
        if snippet.tags:
            header.append("\n" + snippet.tags_display, style="#73daca")
        self.query_one("#preview-header", Static).update(header)

        self.query_one("#preview-code-wrap").display = True
        self._render_code(snippet)

        created = snippet.created_at.strftime("%Y-%m-%d") if snippet.created_at else ""
        updated = snippet.updated_at.strftime("%Y-%m-%d") if snippet.updated_at else ""
        meta = f"{snippet.language}  \u00b7  {created}"
        if updated and updated != created:
            meta += f"  \u00b7  updated {updated}"
        self.query_one("#preview-footer", Static).update(Text(meta, style="#565f89"))

    def _render_code(self, snippet: Snippet) -> None:
        language = _LANG_MAP.get(snippet.language, "text")
        try:
            syntax = _make_syntax(snippet.content, language)
            self.query_one("#preview-code", Static).update(syntax)
        except Exception:
            from rich.text import Text
            self.query_one("#preview-code", Static).update(
                Text(snippet.content, style="#c0caf5")
            )
