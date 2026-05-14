import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastmcp import FastMCP
from db import SQLiteAdapter, ValidationError

mcp = FastMCP("SQLite Lab MCP Server")
adapter = SQLiteAdapter()

# Tools
@mcp.tool("search")
def search(
    table: str,
    filters: dict | None = None,
    columns: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    descending: bool = False,
) -> dict:
    """Tìm kiếm rows trong một bảng với filter, sắp xếp và phân trang."""
    try:
        return adapter.search(table, columns, filters, limit, offset, order_by, descending)
    except ValidationError as e:
        return {"error": str(e)}

@mcp.tool(name="insert")
def insert(table: str, values: dict) -> dict:
    """Chèn một row mới vào bảng và trả về payload đã chèn."""
    try:
        return adapter.insert(table, values)
    except ValidationError as e:
        return {"error": str(e)}

@mcp.tool(name="aggregate")
def aggregate(
    table: str,
    metric: str,
    column: str | None = None,
    filters: dict | None = None,
    group_by: str | None = None,
) -> dict:
    """Thực hiện count/avg/sum/min/max, có thể kèm GROUP BY và filter."""
    try:
        return adapter.aggregate(table, metric, column, filters, group_by)
    except ValidationError as e:
        return {"error": str(e)}
    
# Resources
@mcp.resource("schema://database")
def database_schema() -> str:
    """Trả về toàn bộ schema của database dưới dạng JSON."""
    return json.dumps(adapter.full_schema(), indent=2)
  
@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str) -> str:
    """Trả về schema của một bảng cụ thể dưới dạng JSON."""
    try:
        cols = adapter.get_table_schema(table_name)
        return json.dumps({"table": table_name, "columns": cols}, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()