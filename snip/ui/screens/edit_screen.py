from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from snip.models.snippet import Snippet, SUPPORTED_LANGUAGES


class EditScreen(ModalScreen[Snippet | None]):
    """Modal form for creating or editing a snippet."""

    DEFAULT_CSS = """
    EditScreen {
        align: center middle;
    }
    EditScreen > Vertical {
        width: 80;
        max-height: 90%;
        background: $surface;
        border: thick $accent;
        padding: 1 2;
    }
    EditScreen .form-label {
        color: $text-muted;
        padding: 0 0 0 0;
    }
    EditScreen Input, EditScreen Select {
        margin-bottom: 1;
    }
    EditScreen TextArea {
        height: 14;
        margin-bottom: 1;
    }
    EditScreen .btn-row {
        height: 3;
        align: right middle;
    }
    EditScreen Button {
        margin-left: 1;
    }
    EditScreen .modal-title {
        text-style: bold;
        color: $accent;
        padding: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, snippet: Snippet | None = None) -> None:
        super().__init__()
        self._editing = snippet
        self._is_new = snippet is None

    def compose(self) -> ComposeResult:
        s = self._editing
        title = "New Snippet" if self._is_new else "Edit Snippet"
        with Vertical():
            yield Label(title, classes="modal-title")

            yield Label("Title *", classes="form-label")
            yield Input(
                value=s.title if s else "",
                placeholder="e.g. Reverse a list in Python",
                id="input-title",
            )

            yield Label("Language", classes="form-label")
            options = [(lang, lang) for lang in SUPPORTED_LANGUAGES]
            current_lang = s.language if s else "text"
            yield Select(options, value=current_lang, id="input-language")

            yield Label("Description", classes="form-label")
            yield Input(
                value=s.description if s else "",
                placeholder="Optional short description",
                id="input-description",
            )

            yield Label("Tags (space-separated)", classes="form-label")
            yield Input(
                value=" ".join(s.tags) if s else "",
                placeholder="e.g. python list utils",
                id="input-tags",
            )

            yield Label("Code *", classes="form-label")
            yield TextArea(
                text=s.content if s else "",
                language=None,
                id="input-content",
                tab_behavior="indent",
            )

            with Horizontal(classes="btn-row"):
                yield Button("Cancel", variant="default", id="btn-cancel")
                yield Button("Save", variant="primary", id="btn-save")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-save":
            self._save()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _save(self) -> None:
        title = self.query_one("#input-title", Input).value.strip()
        if not title:
            self.query_one("#input-title", Input).focus()
            return

        content = self.query_one("#input-content", TextArea).text
        if not content.strip():
            self.query_one("#input-content", TextArea).focus()
            return

        lang_select: Select = self.query_one("#input-language", Select)
        language = str(lang_select.value) if lang_select.value != Select.BLANK else "text"

        description = self.query_one("#input-description", Input).value.strip()
        tags_raw = self.query_one("#input-tags", Input).value.strip()
        tags = [t for t in tags_raw.split() if t]

        if self._editing is not None:
            self._editing.title = title
            self._editing.content = content
            self._editing.language = language
            self._editing.description = description
            self._editing.tags = tags
            self.dismiss(self._editing)
        else:
            self.dismiss(Snippet(title=title, content=content, language=language,
                                  description=description, tags=tags))
