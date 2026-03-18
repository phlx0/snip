from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from snip.models.snippet import Snippet


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT    NOT NULL,
                    content     TEXT    NOT NULL,
                    language    TEXT    NOT NULL DEFAULT 'text',
                    description TEXT    NOT NULL DEFAULT '',
                    tags        TEXT    NOT NULL DEFAULT '[]',
                    pinned      INTEGER NOT NULL DEFAULT 0,
                    created_at  TEXT    NOT NULL,
                    updated_at  TEXT    NOT NULL
                )
            """)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, snippet: Snippet) -> Snippet:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """INSERT INTO snippets
                       (title, content, language, description, tags, pinned, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    snippet.title,
                    snippet.content,
                    snippet.language,
                    snippet.description,
                    json.dumps(snippet.tags),
                    int(snippet.pinned),
                    now,
                    now,
                ),
            )
            snippet.id = cursor.lastrowid
        snippet.created_at = datetime.fromisoformat(now)
        snippet.updated_at = datetime.fromisoformat(now)
        return snippet

    def get_all(self) -> list[Snippet]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM snippets ORDER BY pinned DESC, updated_at DESC"
            ).fetchall()
        return [self._row_to_snippet(row) for row in rows]

    def get_by_id(self, snippet_id: int) -> Snippet | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM snippets WHERE id = ?", (snippet_id,)
            ).fetchone()
        return self._row_to_snippet(row) if row else None

    def update(self, snippet: Snippet) -> Snippet:
        now = datetime.now().isoformat()
        with self._connect() as conn:
            conn.execute(
                """UPDATE snippets
                   SET title=?, content=?, language=?, description=?, tags=?, pinned=?, updated_at=?
                   WHERE id=?""",
                (
                    snippet.title,
                    snippet.content,
                    snippet.language,
                    snippet.description,
                    json.dumps(snippet.tags),
                    int(snippet.pinned),
                    now,
                    snippet.id,
                ),
            )
        snippet.updated_at = datetime.fromisoformat(now)
        return snippet

    def delete(self, snippet_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM snippets WHERE id = ?", (snippet_id,)
            )
        return cursor.rowcount > 0

    def search(self, query: str) -> list[Snippet]:
        snippets = self.get_all()
        return [s for s in snippets if s.matches(query)]

    def toggle_pin(self, snippet_id: int) -> bool:
        snippet = self.get_by_id(snippet_id)
        if snippet is None:
            return False
        snippet.pinned = not snippet.pinned
        self.update(snippet)
        return snippet.pinned

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as n FROM snippets").fetchone()
        return row["n"]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _row_to_snippet(row: sqlite3.Row) -> Snippet:
        return Snippet(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            language=row["language"],
            description=row["description"],
            tags=json.loads(row["tags"]),
            pinned=bool(row["pinned"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
