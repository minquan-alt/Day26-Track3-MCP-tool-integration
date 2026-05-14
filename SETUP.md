# SQLite Lab MCP Server — Setup & Demo Guide

## Prerequisites

```bash
pip install fastmcp
# or with conda
conda activate aip && pip install fastmcp
```

## Project Structure

```
implementation/
  db.py             — SQLiteAdapter: all database logic and validation
  init_db.py        — creates lab.db with students/courses/enrollments tables + seed data
  mcp_server.py     — FastMCP server (tools + resources)
  verify_server.py  — manual smoke test script
  start_inspector.sh— launches MCP Inspector
  tests/
    test_server.py  — automated pytest suite
```

## Step 1 — Initialize the database

```bash
cd implementation
python init_db.py
```

Creates `lab.db` with 3 tables and sample rows.

## Step 2 — Run the server

```bash
python mcp_server.py
```

The server starts in stdio mode and waits for an MCP client.

## Step 3 — Run automated tests

```bash
cd implementation
pytest tests/ -v
```

Expected: **9 passed**.

## Step 4 — Run manual verification

```bash
cd implementation
python verify_server.py
```

Demonstrates: search with filter, insert, count, avg by group, error on unknown table, error on bad operator.

## Step 5 — MCP Inspector

```bash
cd implementation
./start_inspector.sh
```

Open the Inspector UI in your browser. Verify:
- Tools listed: `search`, `insert`, `aggregate`
- Resources listed: `schema://database`, `schema://table/{table_name}`
- Valid call returns rows
- Invalid call (e.g., table=`hackers`) returns `{"error": "..."}`

## Step 6 — Claude Code client

The `.mcp.json` at the project root configures Claude Code:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "type": "stdio",
      "command": "/home/quang_ai/miniconda3/envs/aip/bin/python3.10",
      "args": ["/home/quang_ai/admin/AIThucChien/Phase2-Track3/MCPIntegration/implementation/mcp_server.py"],
      "env": {}
    }
  }
}
```

In Claude Code, reference the schema resource with:
```
@sqlite-lab:schema://database
```

## Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `search` | `table`, `filters?`, `columns?`, `limit?`, `offset?`, `order_by?`, `descending?` | Query rows with optional filter, sort, pagination |
| `insert` | `table`, `values` | Insert a new row, returns payload + generated id |
| `aggregate` | `table`, `metric`, `column?`, `filters?`, `group_by?` | count / avg / sum / min / max |

## Resources

| URI | Description |
|-----|-------------|
| `schema://database` | Full schema of all tables as JSON |
| `schema://table/{table_name}` | Schema of a single table |

## Example Calls

```python
# Search students in cohort A1
search(table="students", filters={"cohort": "A1"})

# Insert a new student
insert(table="students", values={"name": "Frank", "cohort": "B2", "score": 77.0})

# Count all students
aggregate(table="students", metric="count")

# Average score per cohort
aggregate(table="students", metric="avg", column="score", group_by="cohort")

# Error case — unknown table
search(table="hackers")  # → {"error": "Table 'hackers' does not exist in the database."}
```
