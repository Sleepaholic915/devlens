
import json

from devlens.agent import execute_tool
from devlens.tools import CodeTools


def test_execute_search_tool(tmp_path):
    (tmp_path / "app.py").write_text(
        "def get_user():\n    pass\n",
        encoding="utf-8",
    )
    tools = CodeTools(tmp_path)

    result = json.loads(
        execute_tool(
            tools,
            "search_code",
            '{"query": "get_user"}',
        )
    )

    assert result["ok"] is True
    assert result["result"][0]["file"] == "app.py"


def test_unknown_tool_rejected(tmp_path):
    tools = CodeTools(tmp_path)

    result = json.loads(
        execute_tool(tools, "delete_file", "{}")
    )

    assert result["ok"] is False
    assert "Unknown tool" in result["error"]


def test_invalid_arguments_rejected(tmp_path):
    tools = CodeTools(tmp_path)

    result = json.loads(
        execute_tool(tools, "search_code", "{bad json}")
    )

    assert result["ok"] is False


def test_path_escape_rejected(tmp_path):
    tools = CodeTools(tmp_path)

    result = json.loads(
        execute_tool(
            tools,
            "read_file",
            json.dumps({
                "relative_path": "../../secret.py",
                "start_line": 1,
                "end_line": 10,
            }),
        )
    )

    assert result["ok"] is False
