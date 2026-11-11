
import json
import pytest

from devlens.agent import execute_tool
from devlens.tools import CodeTools

from types import SimpleNamespace
from unittest.mock import Mock
from devlens.agent import investigate
from devlens.models import InvestigationReport



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


def fake_call(name, arguments, call_id="call_1"):
    """Create a simulated model tool-call item."""
    item = Mock()
    item.type = "function_call"
    item.name = name
    item.arguments = json.dumps(arguments)
    item.call_id = call_id
    item.model_dump.return_value = {
        "type": "function_call",
        "name": name,
        "arguments": item.arguments,
        "call_id": call_id,
    }
    return item


def fake_response(*items, status="completed"):
    """Create a simulated Responses API result."""
    return SimpleNamespace(
        status=status,
        output=list(items),
    )


@pytest.fixture
def mock_client():
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(
        status="completed",
        output_parsed=InvestigationReport(
            observations=["The lookup may return None."],
            hypotheses=["Missing user handling causes the error."],
            next_steps=["Handle missing users explicitly."],
        ),
    )
    return client


@pytest.fixture
def sample_repo(tmp_path):
    (tmp_path / "app.py").write_text(
        "def get_user(user_id):\n"
        "    user = USERS.get(user_id)\n"
        "    return user['id']\n",
        encoding="utf-8",
    )
    return tmp_path


def test_agent_executes_tool_and_returns_report(
    mock_client, sample_repo
):
    mock_client.responses.create.side_effect = [
        fake_response(
            fake_call(
                "search_code",
                {"query": "get_user"},
            )
        ),
        fake_response(),
    ]

    report, trace = investigate(
        "GET /users/999 returned HTTP 500",
        str(sample_repo),
        client=mock_client,
        model="test-model",
    )

    assert len(trace) == 1
    assert trace[0]["tool"] == "search_code"
    assert trace[0]["ok"] is True
    assert report.observations
    assert report.next_steps

    # The second model request must receive the tool output.
    second_input = mock_client.responses.create.call_args_list[1]
    conversation = second_input.kwargs["input"]

    assert any(
        item.get("type") == "function_call_output"
        for item in conversation
    )


def test_agent_recovers_from_tool_error(
    mock_client, sample_repo
):
    mock_client.responses.create.side_effect = [
        fake_response(
            fake_call(
                "read_file",
                {
                    "relative_path": "app.py",
                    "start_line": 1,
                    "end_line": 100,
                },
                call_id="call_1",
            )
        ),
        fake_response(
            fake_call(
                "read_file",
                {
                    "relative_path": "app.py",
                    "start_line": 1,
                    "end_line": 3,
                },
                call_id="call_2",
            )
        ),
        fake_response(),
    ]

    _, trace = investigate(
        "GET /users/999 returned HTTP 500",
        str(sample_repo),
        client=mock_client,
        model="test-model",
    )

    assert len(trace) == 2
    assert trace[0]["ok"] is False
    assert "too many lines" in trace[0]["error"].lower()
    assert trace[1]["ok"] is True


def test_agent_respects_tool_budget(
    mock_client, sample_repo
):
    mock_client.responses.create.side_effect = [
        fake_response(
            fake_call(
                "search_code",
                {"query": "get_user"},
                call_id="call_1",
            )
        ),
        fake_response(
            fake_call(
                "search_code",
                {"query": "USERS"},
                call_id="call_2",
            )
        ),
    ]

    _, trace = investigate(
        "GET /users/999 returned HTTP 500",
        str(sample_repo),
        client=mock_client,
        model="test-model",
        max_tool_calls=2,
    )

    assert len(trace) == 2
    assert mock_client.responses.create.call_count == 2
    assert mock_client.responses.parse.call_count == 1


def test_agent_rejects_invalid_budget(
    mock_client, sample_repo
):
    with pytest.raises(ValueError):
        investigate(
            "API failure",
            str(sample_repo),
            client=mock_client,
            model="test-model",
            max_tool_calls=0,
        )

