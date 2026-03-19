import sqlite3
from pathlib import Path

import pytest

from snip.models.snippet import Snippet
from snip.storage.database import Database, _parse_file, _to_file_text


class TestCreate:
    def test_assigns_string_id(self, tmp_db, sample_snippet):
        result = tmp_db.create(sample_snippet)
        assert result.id is not None
        assert isinstance(result.id, str)
        assert len(result.id) == 12

    def test_sets_timestamps(self, tmp_db, sample_snippet):
        result = tmp_db.create(sample_snippet)
        assert result.created_at is not None
        assert result.updated_at is not None

    def test_persists_all_fields(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        fetched = tmp_db.get_by_id(sample_snippet.id)
        assert fetched is not None
        assert fetched.title == sample_snippet.title
        assert fetched.content == sample_snippet.content
        assert fetched.language == sample_snippet.language
        assert fetched.description == sample_snippet.description
        assert fetched.tags == sample_snippet.tags

    def test_writes_markdown_file(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        files = list((tmp_db._dir).glob("*.md"))
        assert len(files) == 1

    def test_ids_are_unique(self, tmp_db):
        a = tmp_db.create(Snippet(title="A", content="a"))
        b = tmp_db.create(Snippet(title="B", content="b"))
        assert a.id != b.id


class TestGetAll:
    def test_empty_returns_empty_list(self, tmp_db):
        assert tmp_db.get_all() == []

    def test_returns_all_created_snippets(self, tmp_db):
        tmp_db.create(Snippet(title="A", content="a"))
        tmp_db.create(Snippet(title="B", content="b"))
        assert len(tmp_db.get_all()) == 2

    def test_pinned_snippets_come_first(self, tmp_db):
        tmp_db.create(Snippet(title="Normal", content="n"))
        tmp_db.create(Snippet(title="Pinned", content="p", pinned=True))
        results = tmp_db.get_all()
        assert results[0].title == "Pinned"


class TestUpdate:
    def test_updates_title(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        sample_snippet.title = "Updated Title"
        tmp_db.update(sample_snippet)
        fetched = tmp_db.get_by_id(sample_snippet.id)
        assert fetched.title == "Updated Title"

    def test_updates_tags(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        sample_snippet.tags = ["new", "tags"]
        tmp_db.update(sample_snippet)
        fetched = tmp_db.get_by_id(sample_snippet.id)
        assert fetched.tags == ["new", "tags"]

    def test_bumps_updated_at(self, tmp_db, sample_snippet):
        import time
        tmp_db.create(sample_snippet)
        before = sample_snippet.updated_at
        time.sleep(0.01)
        tmp_db.update(sample_snippet)
        fetched = tmp_db.get_by_id(sample_snippet.id)
        assert fetched.updated_at > before


class TestDelete:
    def test_delete_removes_snippet(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        assert tmp_db.delete(sample_snippet.id) is True
        assert tmp_db.get_by_id(sample_snippet.id) is None

    def test_delete_removes_file(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        tmp_db.delete(sample_snippet.id)
        assert not list(tmp_db._dir.glob("*.md"))

    def test_delete_nonexistent_returns_false(self, tmp_db):
        assert tmp_db.delete("nonexistentid") is False

    def test_count_decreases_after_delete(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        tmp_db.delete(sample_snippet.id)
        assert tmp_db.count() == 0


class TestSearch:
    def test_search_by_title(self, tmp_db):
        tmp_db.create(Snippet(title="Docker prune", content="docker system prune -a"))
        tmp_db.create(Snippet(title="Git reset", content="git reset --hard"))
        results = tmp_db.search("docker")
        assert len(results) == 1
        assert results[0].title == "Docker prune"

    def test_search_returns_all_on_empty_query(self, tmp_db):
        tmp_db.create(Snippet(title="A", content="a"))
        tmp_db.create(Snippet(title="B", content="b"))
        assert len(tmp_db.search("")) == 2

    def test_search_by_tag(self, tmp_db):
        tmp_db.create(Snippet(title="A", content="a", tags=["networking"]))
        tmp_db.create(Snippet(title="B", content="b", tags=["git"]))
        results = tmp_db.search("networking")
        assert len(results) == 1


class TestTogglePin:
    def test_pin_unpinned_snippet(self, tmp_db, sample_snippet):
        tmp_db.create(sample_snippet)
        result = tmp_db.toggle_pin(sample_snippet.id)
        assert result is True
        assert tmp_db.get_by_id(sample_snippet.id).pinned is True

    def test_unpin_pinned_snippet(self, tmp_db):
        s = Snippet(title="t", content="c", pinned=True)
        tmp_db.create(s)
        result = tmp_db.toggle_pin(s.id)
        assert result is False
        assert tmp_db.get_by_id(s.id).pinned is False

    def test_toggle_nonexistent_returns_false(self, tmp_db):
        assert tmp_db.toggle_pin("nonexistentid") is False


class TestCount:
    def test_empty_db_count_zero(self, tmp_db):
        assert tmp_db.count() == 0

    def test_count_reflects_creates(self, tmp_db):
        tmp_db.create(Snippet(title="A", content="a"))
        tmp_db.create(Snippet(title="B", content="b"))
        assert tmp_db.count() == 2


class TestSync:
    def test_new_instance_reads_existing_files(self, tmp_path):
        dir1 = tmp_path / "snippets"
        db1 = Database(dir1)
        db1.create(Snippet(title="Persisted", content="data"))

        db2 = Database(dir1)
        assert db2.count() == 1
        assert db2.get_all()[0].title == "Persisted"

    def test_file_added_externally_is_synced(self, tmp_path):
        from snip.storage.database import _to_file_text
        from datetime import datetime

        dir1 = tmp_path / "snippets"
        db1 = Database(dir1)

        s = Snippet(title="External", content="added externally")
        s.id = "externalabc1"
        s.created_at = datetime.now()
        s.updated_at = datetime.now()
        (dir1 / f"{s.id}.md").write_text(_to_file_text(s), encoding="utf-8")

        db2 = Database(dir1)
        assert db2.get_by_id("externalabc1") is not None


class TestMigration:
    def test_migrates_legacy_sqlite(self, tmp_path):
        import json
        from datetime import datetime

        snippets_dir = tmp_path / "snippets"
        old_db_path = tmp_path / "snip.db"

        conn = sqlite3.connect(old_db_path)
        conn.execute("""
            CREATE TABLE snippets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
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
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO snippets (title, content, language, description, tags, pinned, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("Old snippet", "old content", "python", "", json.dumps(["old"]), 0, now, now),
        )
        conn.commit()
        conn.close()

        db = Database(snippets_dir)
        assert db.count() == 1
        snippet = db.get_all()[0]
        assert snippet.title == "Old snippet"
        assert snippet.tags == ["old"]
        conn2 = sqlite3.connect(old_db_path)
        pragma = {row[1]: row[2] for row in conn2.execute("PRAGMA table_info(snippets)").fetchall()}
        conn2.close()
        assert pragma["id"] == "TEXT"

    def test_skips_migration_if_files_exist(self, tmp_path):
        import json
        from datetime import datetime

        snippets_dir = tmp_path / "snippets"
        snippets_dir.mkdir()
        old_db_path = tmp_path / "snip.db"

        conn = sqlite3.connect(old_db_path)
        conn.execute("""
            CREATE TABLE snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, content TEXT NOT NULL,
                language TEXT NOT NULL DEFAULT 'text',
                description TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '[]',
                pinned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )
        """)
        now = datetime.now().isoformat()
        conn.execute(
            "INSERT INTO snippets (title, content, language, description, tags, pinned, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("From old db", "content", "python", "", json.dumps([]), 0, now, now),
        )
        conn.commit()
        conn.close()

        existing = Snippet(title="Existing", content="already here")
        existing.id = "existingfile1"
        existing.created_at = datetime.now()
        existing.updated_at = datetime.now()
        (snippets_dir / f"{existing.id}.md").write_text(_to_file_text(existing), encoding="utf-8")

        db = Database(snippets_dir)
        titles = {s.title for s in db.get_all()}
        assert "Existing" in titles
        assert "From old db" not in titles


class TestFileFormat:
    def test_round_trip_preserves_content_with_separator(self, tmp_db):
        content = "line1\n---\nline2"
        s = tmp_db.create(Snippet(title="sep-test", content=content))
        fetched = tmp_db.get_by_id(s.id)
        assert fetched.content == content

    def test_round_trip_preserves_empty_tags(self, tmp_db):
        s = tmp_db.create(Snippet(title="t", content="c", tags=[]))
        fetched = tmp_db.get_by_id(s.id)
        assert fetched.tags == []

    def test_round_trip_preserves_description_with_colon(self, tmp_db):
        s = tmp_db.create(Snippet(title="t", content="c", description="key: value"))
        fetched = tmp_db.get_by_id(s.id)
        assert fetched.description == "key: value"

    def test_parse_file_invalid_raises(self):
        with pytest.raises((ValueError, KeyError)):
            _parse_file("no frontmatter here")
