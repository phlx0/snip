import pytest
from pathlib import Path

from snip.models.snippet import Snippet
from snip.storage.database import Database


class TestCreate:
    def test_assigns_id_after_create(self, tmp_db, sample_snippet):
        result = tmp_db.create(sample_snippet)
        assert result.id is not None
        assert result.id > 0

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

    def test_delete_nonexistent_returns_false(self, tmp_db):
        assert tmp_db.delete(9999) is False

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
        assert tmp_db.toggle_pin(9999) is False


class TestCount:
    def test_empty_db_count_zero(self, tmp_db):
        assert tmp_db.count() == 0

    def test_count_reflects_creates(self, tmp_db):
        tmp_db.create(Snippet(title="A", content="a"))
        tmp_db.create(Snippet(title="B", content="b"))
        assert tmp_db.count() == 2
