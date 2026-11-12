
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_fixture(name):
    """Load a fixture without importing it as a project package."""
    path = ROOT / "examples" / name / "app.py"

    spec = importlib.util.spec_from_file_location(
        f"fixture_{name}", path
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def test_incorrect_total_reproduces_bug():
    app = load_fixture("incorrect_total")

    response = app.calculate_total(100, 2, 0.10)

    assert response["status"] == 200
    assert response["body"]["total"] == pytest.approx(199.90)
    assert response["body"]["total"] != pytest.approx(180.00)


def test_missing_authorization_reproduces_bug():
    app = load_fixture("missing_authorization")

    response = app.get_order(102, current_user_id=1)

    assert response["status"] == 200
    assert response["body"]["owner_id"] == 2
