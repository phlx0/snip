import pytest
from pathlib import Path
from snip.storage.database import Database


@pytest.fixture
def tmp_db(tmp_path: Path) -> Database:
    """In-memory SQLite database scoped to each test."""
    return Database(tmp_path / "test.db")


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
