# implementation/tests/test_server.py
import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from db import SQLiteAdapter, ValidationError

@pytest.fixture
def adapter():
    return SQLiteAdapter()

def test_list_tables(adapter):
    tables = adapter.list_tables()
    assert "students" in tables and "courses" in tables

def test_search_valid(adapter):
    result = adapter.search("students", filters={"cohort": "A1"})
    assert result["count"] > 0

def test_search_unknown_table(adapter):
    with pytest.raises(ValidationError):
        adapter.search("hackers")

def test_search_unknown_column(adapter):
    with pytest.raises(ValidationError):
        adapter.search("students", columns=["nonexistent"])

def test_insert_valid(adapter):
    r = adapter.insert("students", {"name": "Test", "cohort": "X9", "score": 50.0})
    assert r["inserted"] and "id" in r

def test_insert_empty(adapter):
    with pytest.raises(ValidationError):
        adapter.insert("students", {})

def test_aggregate_count(adapter):
    r = adapter.aggregate("students", "count")
    assert r["rows"][0]["value"] > 0

def test_aggregate_invalid_metric(adapter):
    with pytest.raises(ValidationError):
        adapter.aggregate("students", "drop")

def test_aggregate_group_by(adapter):
    r = adapter.aggregate("students", "avg", column="score", group_by="cohort")
    assert len(r["rows"]) >= 1