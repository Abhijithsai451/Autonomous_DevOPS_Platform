import os
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver

DATABASE_URL = os.getenv("DATABASE_URL")

pool = ConnectionPool(conninfo = DATABASE_URL, max_size = 20, kwargs = {"autocommit": True})

def setup_checkpoint_tables():
    """
    Ensures LangGraph checkpoint tables (checkpoint, checkpoint_blobs, etc ) exist
    """
    with pool.connection as conn:
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()

def get_postgres_checkpointer():
    """
    Context manager yielding an initialized PostgresSaver instance bound to a pooled connection.
    """
    with pool.connection() as conn:
        checkpointer = PostgresSaver(conn)
        yield checkpointer