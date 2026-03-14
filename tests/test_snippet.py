from datetime import datetime

import pytest

from snip.models.snippet import Snippet, SUPPORTED_LANGUAGES


class TestSnippetDefaults:
    def test_timestamps_set_on_creation(self):
        s = Snippet(title="t", content="c")
        assert isinstance(s.created_at, datetime)
        assert isinstance(s.updated_at, datetime)

    def test_unknown_language_falls_back_to_text(self):
        s = Snippet(title="t", content="c", language="brainfuck")
        assert s.language == "text"

    def test_supported_language_preserved(self):
        s = Snippet(title="t", content="c", language="python")
        assert s.language == "python"

    def test_all_supported_languages_accepted(self):
        for lang in SUPPORTED_LANGUAGES:
            s = Snippet(title="t", content="c", language=lang)
            assert s.language == lang


class TestTagsDisplay:
    def test_no_tags_returns_empty(self):
        s = Snippet(title="t", content="c")
        assert s.tags_display == ""

    def test_tags_formatted_with_hash(self):
        s = Snippet(title="t", content="c", tags=["python", "cli"])
        assert s.tags_display == "#python #cli"


class TestShortDescription:
    def test_uses_description_when_set(self):
        s = Snippet(title="t", content="long content", description="Short desc")
        assert s.short_description == "Short desc"

    def test_falls_back_to_first_line_of_content(self):
        s = Snippet(title="t", content="first line\nsecond line")
        assert s.short_description == "first line"

    def test_truncates_long_description(self):
        s = Snippet(title="t", content="c", description="x" * 80)
        assert s.short_description.endswith("…")
        assert len(s.short_description) <= 61  # 60 chars + ellipsis


class TestMatches:
    def test_matches_title(self):
        s = Snippet(title="Hello World", content="c")
        assert s.matches("hello")

    def test_matches_content(self):
        s = Snippet(title="t", content="import sys")
        assert s.matches("import")

    def test_matches_tags(self):
        s = Snippet(title="t", content="c", tags=["networking"])
        assert s.matches("network")

    def test_matches_language(self):
        s = Snippet(title="t", content="c", language="python")
        assert s.matches("python")

    def test_no_match(self):
        s = Snippet(title="Hello", content="World", tags=["foo"])
        assert not s.matches("zzz_nomatch_zzz")

    def test_empty_query_always_matches(self):
        s = Snippet(title="t", content="c")
        assert s.matches("")

    def test_case_insensitive(self):
        s = Snippet(title="Hello World", content="c")
        assert s.matches("HELLO")
