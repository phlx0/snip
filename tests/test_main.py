from __future__ import annotations

import json
from pathlib import Path

import pytest

from snip.__main__ import (
    _lang_from_ext,
    _resolve,
    _run_add,
    _run_export,
    _run_import,
)
from snip.models.snippet import Snippet
from snip.storage.database import Database

# ---------------------------------------------------------------------------
# _lang_from_ext
# ---------------------------------------------------------------------------

class TestLangFromExt:
    def test_python(self, tmp_path):
        assert _lang_from_ext(tmp_path / "foo.py") == "python"

    def test_dockerfile_no_extension(self, tmp_path):
        assert _lang_from_ext(tmp_path / "Dockerfile") == "dockerfile"

    def test_dotdockerfile(self, tmp_path):
        assert _lang_from_ext(tmp_path / ".dockerfile") == "dockerfile"

    def test_unknown_extension_falls_back_to_text(self, tmp_path):
        assert _lang_from_ext(tmp_path / "file.xyz") == "text"

    def test_yaml_variants(self, tmp_path):
        assert _lang_from_ext(tmp_path / "config.yaml") == "yaml"
        assert _lang_from_ext(tmp_path / "config.yml") == "yaml"

    def test_case_insensitive(self, tmp_path):
        assert _lang_from_ext(tmp_path / "SCRIPT.PY") == "python"


# ---------------------------------------------------------------------------
# _resolve
# ---------------------------------------------------------------------------

class TestResolve:
    def test_exact_match(self, tmp_db_path):
        db = Database(tmp_db_path)
        db.create(Snippet(title="Deploy script", content="./deploy.sh"))
        result = _resolve("Deploy script", tmp_db_path)
        assert result.title == "Deploy script"

    def test_case_insensitive_exact_match(self, tmp_db_path):
        db = Database(tmp_db_path)
        db.create(Snippet(title="Deploy script", content="./deploy.sh"))
        result = _resolve("deploy script", tmp_db_path)
        assert result.title == "Deploy script"

    def test_substring_match(self, tmp_db_path):
        db = Database(tmp_db_path)
        db.create(Snippet(title="Deploy script", content="./deploy.sh"))
        result = _resolve("deploy", tmp_db_path)
        assert result.title == "Deploy script"

    def test_no_match_exits(self, tmp_db_path):
        Database(tmp_db_path)
        with pytest.raises(SystemExit):
            _resolve("nonexistent", tmp_db_path)

    def test_multiple_matches_exits(self, tmp_db_path):
        db = Database(tmp_db_path)
        db.create(Snippet(title="git push", content="git push"))
        db.create(Snippet(title="git pull", content="git pull"))
        with pytest.raises(SystemExit):
            _resolve("git", tmp_db_path)


# ---------------------------------------------------------------------------
# _run_add
# ---------------------------------------------------------------------------

class TestRunAdd:
    def test_adds_file_as_snippet(self, tmp_path, tmp_db_path):
        f = tmp_path / "hello.py"
        f.write_text('print("hello")')
        _run_add(str(f), tmp_db_path)
        db = Database(tmp_db_path)
        snippets = db.get_all()
        assert len(snippets) == 1
        assert snippets[0].language == "python"
        assert snippets[0].content == 'print("hello")'

    def test_missing_file_exits(self, tmp_db_path):
        with pytest.raises(SystemExit):
            _run_add("/nonexistent/file.py", tmp_db_path)

    def test_non_utf8_file_does_not_crash(self, tmp_path, tmp_db_path):
        f = tmp_path / "binary.sh"
        f.write_bytes(b"echo hello\xff\xfe")
        _run_add(str(f), tmp_db_path)
        db = Database(tmp_db_path)
        assert db.count() == 1


# ---------------------------------------------------------------------------
# _run_export + _run_import round-trip
# ---------------------------------------------------------------------------

class TestExport:
    def test_exports_all_snippets(self, tmp_db_path, capsys):
        db = Database(tmp_db_path)
        db.create(Snippet(title="A", content="aaa", tags=["x"]))
        db.create(Snippet(title="B", content="bbb"))
        _run_export(tmp_db_path)
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 2
        titles = {d["title"] for d in data}
        assert titles == {"A", "B"}

    def test_export_empty_db(self, tmp_db_path, capsys):
        _run_export(tmp_db_path)
        data = json.loads(capsys.readouterr().out)
        assert data == []


class TestImport:
    def _write_json(self, path: Path, payload) -> Path:
        f = path / "import.json"
        f.write_text(json.dumps(payload))
        return f

    def test_imports_valid_snippets(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, [
            {"title": "foo", "content": "bar", "language": "python"},
        ])
        _run_import(str(f), tmp_db_path)
        db = Database(tmp_db_path)
        assert db.count() == 1
        assert db.get_all()[0].title == "foo"

    def test_non_array_root_exits(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, {"title": "foo", "content": "bar"})
        with pytest.raises(SystemExit):
            _run_import(str(f), tmp_db_path)

    def test_invalid_json_exits(self, tmp_path, tmp_db_path):
        f = tmp_path / "bad.json"
        f.write_text("not json {{{")
        with pytest.raises(SystemExit):
            _run_import(str(f), tmp_db_path)

    def test_missing_file_exits(self, tmp_db_path):
        with pytest.raises(SystemExit):
            _run_import("/nonexistent/file.json", tmp_db_path)

    def test_skips_non_dict_entries(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, [
            "just a string",
            {"title": "valid", "content": "ok"},
        ])
        _run_import(str(f), tmp_db_path)
        db = Database(tmp_db_path)
        assert db.count() == 1

    def test_skips_entries_missing_required_fields(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, [
            {"title": "no content"},
            {"content": "no title"},
            {"title": "both", "content": "present"},
        ])
        _run_import(str(f), tmp_db_path)
        db = Database(tmp_db_path)
        assert db.count() == 1

    def test_tags_string_coerced_to_empty_list(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, [
            {"title": "t", "content": "c", "tags": "python"},
        ])
        _run_import(str(f), tmp_db_path)
        snippet = Database(tmp_db_path).get_all()[0]
        assert snippet.tags == []

    def test_tags_list_of_strings_preserved(self, tmp_path, tmp_db_path):
        f = self._write_json(tmp_path, [
            {"title": "t", "content": "c", "tags": ["a", "b"]},
        ])
        _run_import(str(f), tmp_db_path)
        snippet = Database(tmp_db_path).get_all()[0]
        assert snippet.tags == ["a", "b"]

    def test_round_trip(self, tmp_path, tmp_db_path, capsys):
        db = Database(tmp_db_path)
        db.create(Snippet(title="round", content="trip", tags=["x"], pinned=True))
        _run_export(tmp_db_path)
        exported = capsys.readouterr().out

        tmp_db2 = tmp_path / "db2_snippets"
        import_file = tmp_path / "export.json"
        import_file.write_text(exported)
        _run_import(str(import_file), tmp_db2)

        result = Database(tmp_db2).get_all()[0]
        assert result.title == "round"
        assert result.tags == ["x"]
        assert result.pinned is True


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "snippets"
