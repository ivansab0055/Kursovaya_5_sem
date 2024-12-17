from alembic import op
from sqlalchemy import text


def column_exists(table_name, column_name):
    """Helper function to check if a column exists in the specified table."""
    conn = op.get_bind()
    query = text("SELECT column_name FROM information_schema.columns WHERE table_name=:table AND column_name=:column")
    result = conn.execute(query, {"table": table_name, "column": column_name})

    return result.fetchone() is not None
