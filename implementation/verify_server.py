# implementation/verify_server.py
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from db import SQLiteAdapter, ValidationError

adapter = SQLiteAdapter()

print("=== Tables ===")
print(adapter.list_tables())

print("\n=== Search students in cohort A1 ===")
print(adapter.search("students", filters={"cohort": "A1"}))

print("\n=== Insert new student ===")
print(adapter.insert("students", {"name": "Frank", "cohort": "B2", "score": 77.0}))

print("\n=== Count students ===")
print(adapter.aggregate("students", "count"))

print("\n=== Avg score by cohort ===")
print(adapter.aggregate("students", "avg", column="score", group_by="cohort"))

print("\n=== Error: unknown table ===")
try:
    adapter.search("hackers")
except ValidationError as e:
    print(f"ValidationError: {e}")

print("\n=== Error: bad operator ===")
try:
    adapter.search("students", filters={"score": {"op": "DROP", "value": 0}})
except ValidationError as e:
    print(f"ValidationError: {e}")