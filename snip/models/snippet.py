from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
SUPPORTED_LANGUAGES = [
    "text", "python", "javascript", "typescript", "bash", "go", "rust",
    "c", "cpp", "java", "json", "yaml", "toml", "sql", "html", "css",
    "markdown", "dockerfile", "powershell", "ruby", "php", "swift", "kotlin",
]


@dataclass
class Snippet:
    title: str
    content: str
    language: str = "text"
    description: str = ""
    tags: list[str] = field(default_factory=list)
    pinned: bool = False
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
        if self.language not in SUPPORTED_LANGUAGES:
            self.language = "text"

    @property
    def tags_display(self) -> str:
        return " ".join(f"#{t}" for t in self.tags) if self.tags else ""

    @property
    def short_description(self) -> str:
        if self.description:
            return self.description[:60] + ("…" if len(self.description) > 60 else "")
        first_line = self.content.strip().splitlines()[0] if self.content.strip() else ""
        return first_line[:60] + ("…" if len(first_line) > 60 else "")

    def matches(self, query: str) -> bool:
        if not query:
            return True
        q = query.lower()
        return (
            q in self.title.lower()
            or q in self.description.lower()
            or q in self.content.lower()
            or any(q in tag.lower() for tag in self.tags)
            or q in self.language.lower()
        )
