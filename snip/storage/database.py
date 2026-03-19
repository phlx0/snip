from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from snip.models.snippet import Snippet

_SEP = "\n---\n"


def _now() -> datetime:
    return datetime.now()


def _parse_file(text: str) -> Snippet:
    if not text.startswith("---\n"):
        raise ValueError("missing frontmatter")
    rest = text[4:]
    sep = rest.index(_SEP)
    front = rest[:sep]
    content = rest[sep + len(_SEP):]

    meta: dict[str, str] = {}
    for line in front.splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            meta[k] = v
        elif line.endswith(":"):
            meta[line[:-1]] = ""

    tags_raw = meta.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

    return Snippet(
        id=meta["id"],
        title=meta["title"],
        content=content,
        language=meta.get("language", "text"),
        description=meta.get("description", ""),
        tags=tags,
        pinned=meta.get("pinned", "false") == "true",
        created_at=datetime.fromisoformat(meta["created_at"]),
        updated_at=datetime.fromisoformat(meta["updated_at"]),
    )


def _to_file_text(snippet: Snippet) -> str:
    lines = [
        "---",
        f"id: {snippet.id}",
        f"title: {snippet.title}",
        f"language: {snippet.language}",
        f"description: {snippet.description}",
        f"tags: {', '.join(snippet.tags)}",
        f"pinned: {str(snippet.pinned).lower()}",
        f"created_at: {snippet.created_at.isoformat()}",
        f"updated_at: {snippet.updated_at.isoformat()}",
        "---",
        snippet.content,
    ]
    return "\n".join(lines)


def _row_to_snippet(row: sqlite3.Row) -> Snippet:
    tags_raw = row["tags"]
    tags = json.loads(tags_raw) if tags_raw else []
    return Snippet(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        language=row["language"],
        description=row["description"],
        tags=tags,
        pinned=bool(row["pinned"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def _row_to_snippet_legacy(row: sqlite3.Row) -> Snippet:
    tags_raw = row["tags"]
    try:
        tags = json.loads(tags_raw) if tags_raw else []
    except Exception:
        tags = []
    return Snippet(
        title=row["title"],
        content=row["content"],
        language=row["language"],
        description=row["description"],
        tags=tags,
        pinned=bool(row["pinned"]),
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


class Database:
    def __init__(self, snippets_dir: Path) -> None:
        self._dir = snippets_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._db_path = snippets_dir.parent / "snip.db"
        self._ensure_gitignore()
        self._migrate_legacy()
        self._init_index()
        self._sync()

    def _ensure_gitignore(self) -> None:
        gi = self._dir.parent / ".gitignore"
        if not gi.exists():
            gi.write_text("snip.db\n", encoding="utf-8")
        elif "snip.db" not in gi.read_text(encoding="utf-8"):
            with gi.open("a", encoding="utf-8") as f:
                f.write("snip.db\n")

    def _migrate_legacy(self) -> None:
        if not self._db_path.exists():
            return
        if any(self._dir.glob("*.md")):
            return
        try:
            conn = sqlite3.connect(self._db_path)
            conn.row_factory = sqlite3.Row
            pragma = {row["name"]: row["type"] for row in conn.execute("PRAGMA table_info(snippets)").fetchall()}
            if pragma.get("id") != "INTEGER":
                conn.close()
                return
            rows = conn.execute("SELECT * FROM snippets ORDER BY id").fetchall()
            conn.close()
        except Exception:
            return
        for row in rows:
            try:
                snippet = _row_to_snippet_legacy(row)
                snippet.id = uuid.uuid4().hex[:12]
                self._write_file(snippet)
            except Exception:
                continue
        self._db_path.unlink()

    def _init_index(self) -> None:
        with self._connect() as conn:
            pragma = {
                row["name"]: row["type"]
                for row in conn.execute("PRAGMA table_info(snippets)").fetchall()
            }
            if pragma.get("id") == "INTEGER":
                conn.execute("DROP TABLE snippets")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id          TEXT PRIMARY KEY,
                    title       TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    language    TEXT NOT NULL DEFAULT 'text',
                    description TEXT NOT NULL DEFAULT '',
                    tags        TEXT NOT NULL DEFAULT '[]',
                    pinned      INTEGER NOT NULL DEFAULT 0,
                    created_at  TEXT NOT NULL,
                    updated_at  TEXT NOT NULL
                )
            """)

    def _sync(self) -> None:
        file_snippets = {s.id: s for s in self._read_all_files()}
        with self._connect() as conn:
            db_state = {
                row["id"]: row["updated_at"]
                for row in conn.execute("SELECT id, updated_at FROM snippets").fetchall()
            }
            for sid, snippet in file_snippets.items():
                if sid not in db_state or db_state[sid] != snippet.updated_at.isoformat():
                    self._upsert_index(conn, snippet)
            for sid in db_state:
                if sid not in file_snippets:
                    conn.execute("DELETE FROM snippets WHERE id = ?", (sid,))

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _read_all_files(self) -> list[Snippet]:
        snippets = []
        for path in sorted(self._dir.glob("*.md")):
            try:
                snippets.append(_parse_file(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return snippets

    def _write_file(self, snippet: Snippet) -> None:
        path = self._dir / f"{snippet.id}.md"
        path.write_text(_to_file_text(snippet), encoding="utf-8")

    def _delete_file(self, snippet_id: str) -> bool:
        path = self._dir / f"{snippet_id}.md"
        if not path.exists():
            return False
        path.unlink()
        return True

    def _upsert_index(self, conn: sqlite3.Connection, snippet: Snippet) -> None:
        conn.execute(
            """
            INSERT OR REPLACE INTO snippets
                (id, title, content, language, description, tags, pinned, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snippet.id,
                snippet.title,
                snippet.content,
                snippet.language,
                snippet.description,
                json.dumps(snippet.tags),
                int(snippet.pinned),
                snippet.created_at.isoformat(),
                snippet.updated_at.isoformat(),
            ),
        )

    def create(self, snippet: Snippet) -> Snippet:
        now = _now()
        snippet.id = uuid.uuid4().hex[:12]
        snippet.created_at = now
        snippet.updated_at = now
        self._write_file(snippet)
        with self._connect() as conn:
            self._upsert_index(conn, snippet)
        return snippet

    def get_all(self) -> list[Snippet]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM snippets ORDER BY pinned DESC, updated_at DESC"
            ).fetchall()
        return [_row_to_snippet(row) for row in rows]

    def get_by_id(self, snippet_id: str) -> Snippet | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM snippets WHERE id = ?", (snippet_id,)
            ).fetchone()
        return _row_to_snippet(row) if row else None

    def update(self, snippet: Snippet) -> Snippet:
        snippet.updated_at = _now()
        self._write_file(snippet)
        with self._connect() as conn:
            self._upsert_index(conn, snippet)
        return snippet

    def delete(self, snippet_id: str) -> bool:
        deleted = self._delete_file(snippet_id)
        with self._connect() as conn:
            conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        return deleted

    def search(self, query: str) -> list[Snippet]:
        return [s for s in self.get_all() if s.matches(query)]

    def toggle_pin(self, snippet_id: str) -> bool:
        snippet = self.get_by_id(snippet_id)
        if snippet is None:
            return False
        snippet.pinned = not snippet.pinned
        self.update(snippet)
        return snippet.pinned

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) as n FROM snippets").fetchone()["n"]
