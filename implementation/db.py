import sqlite3, json, os

from init_db import DB_PATH, create_database

ALLOWED_METRICS = {"count", "avg", "sum", "min", "max"}
ALLOWED_OPERATORS = {"=", ">", "<", ">=", "<=", "!=", "like"}

class ValidationError(Exception):
    """Raised khi request không hợp lệ."""

class SQLiteAdapter:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        if not os.path.exists(db_path):
            create_database()
    
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def list_tables(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        return [row['name'] for row in rows]
    
    def get_table_schema(self, table):
        self._validate_table(table)
        with self._connect() as conn:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return [{"name": row['name'], "type": row['type'], "notnull": bool(row['notnull']), "pk": bool(row['pk'])} for row in rows]

    # Validation helpers
    def _validate_table(self, table):
        if table not in self.list_tables():
            raise ValidationError(f"Table '{table}' does not exist in the database.")

    def _validate_columns(self, table, columns):
        valid = {c["name"] for c in self.get_table_schema(table)}
        bad = [c for c in columns if c not in valid]
        if bad:
            raise ValidationError(f"Invalid columns for table '{table}': {bad}")

    def _build_where(self, table: str, filters: dict | None):
          """filters = {"column": value} hoặc {"column": {"op": ">=", "value": 80}}"""
          if not filters:
              return "", []
          clauses, params = [], []
          valid_cols = {c["name"] for c in self.get_table_schema(table)}
          for col, spec in filters.items():
              if col not in valid_cols:
                  raise ValidationError(f"Unknown filter column: '{col}'")
              if isinstance(spec, dict):
                  op = spec.get("op", "=").lower()
                  val = spec["value"]
              else:
                  op, val = "=", spec
              if op not in ALLOWED_OPERATORS:
                  raise ValidationError(f"Unsupported operator: '{op}'")
              clauses.append(f"{col} {op} ?")
              params.append(val)
          return "WHERE " + " AND ".join(clauses), params
    
    # ── Core operations ─────────────────────────────────────────────────────

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        self._validate_table(table)
        schema_cols = [c["name"] for c in self.get_table_schema(table)]
        if columns:
            self._validate_columns(table, columns)
            select = ", ".join(columns)
        else:
            select = "*"
        where_sql, params = self._build_where(table, filters)
        order_sql = ""
        if order_by:
            if order_by not in schema_cols:
                raise ValidationError(f"Unknown order_by column: '{order_by}'")
            direction = "DESC" if descending else "ASC"
            order_sql = f"ORDER BY {order_by} {direction}"
        sql = f"SELECT {select} FROM {table} {where_sql} {order_sql} LIMIT ? OFFSET ?"
        params += [limit, offset]
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return {"rows": [dict(r) for r in rows], "count": len(rows)}

    def insert(self, table, values: dict):
        if not values:
            raise ValidationError("'values' must not be empty")
        self._validate_table(table)
        self._validate_columns(table, list(values.keys()))
        cols = ", ".join(values.keys())
        placeholders = ", ".join(["?"] * len(values))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        with self._connect() as conn:
            cur = conn.execute(sql, list(values.values()))
            conn.commit()
            last_id = cur.lastrowid
        return {"inserted": True, "id": last_id, **values}

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        metric = metric.lower()
        if metric not in ALLOWED_METRICS:
            raise ValidationError(f"Unsupported metric: '{metric}'. Allowed: {ALLOWED_METRICS}")
        self._validate_table(table)
        if metric != "count" and not column:
            raise ValidationError(f"metric='{metric}' requires a column")
        if column:
            self._validate_columns(table, [column])
        agg_expr = f"{metric.upper()}({column})" if column else "COUNT(*)"
        where_sql, params = self._build_where(table, filters)
        group_sql = ""
        if group_by:
            self._validate_columns(table, [group_by])
            group_sql = f"GROUP BY {group_by}"
            select = f"{group_by}, {agg_expr} AS value"
        else:
            select = f"{agg_expr} AS value"
        sql = f"SELECT {select} FROM {table} {where_sql} {group_sql}"
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return {"metric": metric, "column": column, "rows": [dict(r) for r in rows]}

    def full_schema(self) -> dict:
        schema = {}
        for table in self.list_tables():
            schema[table] = self.get_table_schema(table)
        return schema