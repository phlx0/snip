from pathlib import Path

import pytest

from snip.storage.database import Database


@pytest.fixture
def tmp_db(tmp_path: Path) -> Database:
    return Database(tmp_path / "snippets")


@pytest.fixture
def sample_snippet():
    from snip.models.snippet import Snippet
    return Snippet(
        title="Hello World",
        content='print("hello world")',
        language="python",
        description="A classic",
        tags=["python", "beginner"],
    )
