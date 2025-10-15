import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

_pg_pool = None

def init_db():
    global _pg_pool
    _pg_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        dsn=DB_URL
    )
    print(" database connection pool created")

@contextmanager
def get_conn():
    conn = _pg_pool.getconn()
    try:
        yield conn
    finally:
        _pg_pool.putconn(conn)
def execute_query(query, params=None):
    """Run a SQL query and return results as a list of dicts"""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if cur.description:  # if it’s a SELECT query
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:
                conn.commit()
                return []