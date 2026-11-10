import pytest

from devlens.tools import CodeTools


@pytest.fixture
def repo(tmp_path):
    """Create an isolated test repository."""
    (tmp_path / "app.py").write_text(
        "def get_user(user_id):\n"
        "    return database.find_user(user_id)\n"
        "\n"
        "def health_check():\n"
        "    return True\n",
        encoding="utf-8",
    )

    (tmp_path / "config.py").write_text(
        "DATABASE_URL = 'test-db'\n",
        encoding="utf-8",
    )

    return CodeTools(tmp_path)


def test_search_code(repo):
    results = repo.search_code("find_user")

    assert len(results) == 1
    assert results[0]["file"] == "app.py"
    assert results[0]["line"] == 2


def test_search_is_case_insensitive(repo):
    results = repo.search_code("database_url")

    assert len(results) == 1
    assert results[0]["file"] == "config.py"


def test_read_file(repo):
    result = repo.read_file("app.py", 1, 2)

    assert result["start_line"] == 1
    assert result["end_line"] == 2
    assert "1: def get_user" in result["content"]
    assert "2:     return database.find_user" in result["content"]


def test_reject_path_traversal(repo):
    with pytest.raises(ValueError):
        repo.read_file("../../secret.py")


def test_reject_absolute_path(repo):
    with pytest.raises(ValueError):
        repo.read_file("C:/Windows/example.py")


def test_reject_large_read(repo):
    with pytest.raises(ValueError):
        repo.read_file("app.py", 1, 500)


def test_reject_non_python_file(repo, tmp_path):
    (tmp_path / "notes.txt").write_text("hello")

    with pytest.raises(ValueError):
        repo.read_file("notes.txt")


def test_search_result_limit(repo):
    results = repo.search_code("def")

    assert len(results) <= repo.MAX_SEARCH_RESULTS
