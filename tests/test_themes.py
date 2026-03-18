from __future__ import annotations

import json
from pathlib import Path

import pytest

from snip import themes
from snip.themes import Theme, load, list_themes, get_active_name, set_active, import_theme


# ---------------------------------------------------------------------------
# load
# ---------------------------------------------------------------------------

class TestLoad:
    def test_loads_builtin_tokyo_night(self):
        t = load("tokyo-night")
        assert t.name == "tokyo-night"
        assert t.bg == "#0d0f18"

    def test_loads_builtin_dracula(self):
        t = load("dracula")
        assert t.name == "dracula"

    def test_missing_theme_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load("nonexistent-theme")

    def test_loads_custom_theme_from_disk(self, theme_dir):
        custom = {"name": "my-theme", "colors": {"bg": "#111111"}}
        (theme_dir / "my-theme.json").write_text(json.dumps(custom))
        t = load("my-theme")
        assert t.name == "my-theme"
        assert t.bg == "#111111"

    def test_unknown_color_key_is_ignored(self, theme_dir):
        custom = {"name": "safe", "colors": {"not_a_real_field": "#ff0000"}}
        (theme_dir / "safe.json").write_text(json.dumps(custom))
        t = load("safe")
        assert not hasattr(t, "not_a_real_field")


# ---------------------------------------------------------------------------
# list_themes
# ---------------------------------------------------------------------------

class TestListThemes:
    def test_always_includes_builtins(self):
        names = list_themes()
        assert "tokyo-night" in names
        assert "dracula" in names

    def test_includes_custom_themes(self, theme_dir):
        (theme_dir / "custom-one.json").write_text(json.dumps({"colors": {}}))
        names = list_themes()
        assert "custom-one" in names

    def test_returns_sorted_unique(self):
        names = list_themes()
        assert names == sorted(set(names))


# ---------------------------------------------------------------------------
# get_active_name / set_active
# ---------------------------------------------------------------------------

class TestActiveTheme:
    def test_default_is_tokyo_night(self, config_dir):
        assert get_active_name() == "tokyo-night"

    def test_set_and_get_active(self, config_dir):
        set_active("dracula")
        assert get_active_name() == "dracula"

    def test_set_active_creates_config_file(self, config_dir):
        set_active("dracula")
        config = config_dir / "config.json"
        assert config.exists()
        data = json.loads(config.read_text())
        assert data["theme"] == "dracula"

    def test_set_active_preserves_other_config_keys(self, config_dir):
        config = config_dir / "config.json"
        config.write_text(json.dumps({"other_key": "value", "theme": "dracula"}))
        set_active("tokyo-night")
        data = json.loads(config.read_text())
        assert data["other_key"] == "value"
        assert data["theme"] == "tokyo-night"

    def test_corrupt_config_returns_default(self, config_dir, capsys):
        config = config_dir / "config.json"
        config.write_text("not json {{{")
        result = get_active_name()
        assert result == "tokyo-night"
        assert "warning" in capsys.readouterr().err.lower()


# ---------------------------------------------------------------------------
# import_theme
# ---------------------------------------------------------------------------

class TestImportTheme:
    def test_imports_valid_theme(self, tmp_path, theme_dir):
        src = tmp_path / "my.json"
        src.write_text(json.dumps({"name": "my-theme", "colors": {"bg": "#abcdef"}}))
        name = import_theme(src)
        assert name == "my-theme"
        assert (theme_dir / "my-theme.json").exists()

    def test_uses_filename_as_name_when_missing(self, tmp_path, theme_dir):
        src = tmp_path / "fallback.json"
        src.write_text(json.dumps({"colors": {"bg": "#000000"}}))
        name = import_theme(src)
        assert name == "fallback"

    def test_missing_colors_key_raises_value_error(self, tmp_path):
        src = tmp_path / "bad.json"
        src.write_text(json.dumps({"name": "bad"}))
        with pytest.raises(ValueError, match="colors"):
            import_theme(src)

    def test_invalid_json_raises_value_error(self, tmp_path):
        src = tmp_path / "broken.json"
        src.write_text("not json")
        with pytest.raises(ValueError):
            import_theme(src)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolate_config(tmp_path, monkeypatch):
    """Redirect all theme config I/O to a temp directory."""
    monkeypatch.setattr(themes, "_CONFIG_DIR", tmp_path / "snip")
    return tmp_path / "snip"


@pytest.fixture
def config_dir(tmp_path):
    d = tmp_path / "snip"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def theme_dir(tmp_path):
    d = tmp_path / "snip" / "themes"
    d.mkdir(parents=True, exist_ok=True)
    return d
