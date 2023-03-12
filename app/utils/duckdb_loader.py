import duckdb
import streamlit as st


def create_duckdb_conn(db_path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    """
    Create a duckdb connection

    Args:
        db_path (str, optional): Path to the database. Defaults to ":memory:".

    Returns:
        duckdb.DuckDBPyConnection: duckdb connection
    """
    duckdb_connection = duckdb.connect(db_path)
    try:
        duckdb_connection.sql("INSTALL httpfs;")
        duckdb_connection.sql("LOAD httpfs;")
        duckdb_connection.sql("SET s3_region='us-east-1';")
    except Exception:
        st.write(
            "Failed to install httpfs extension. Only local files will be supported"
        )

    duckdb_connection.sql(
        "create temporary table if not exists _querybot(query VARCHAR PRIMARY KEY, result VARCHAR)"
    )

    return duckdb_connection


def load_s3_path(
    duckdb_connection: duckdb.DuckDBPyConnection, load_s3_path: str
) -> str:
    """
    Load a file from S3 into duckdb

    Args:
        duckdb_connection (duckdb.DuckDBPyConnection): duckdb connection
        load_s3_path (str): S3 path to load

    Returns:
        str: SQL statement used to load the file
    """
    import os

    # Get the file name from the s3 path
    file_name = load_s3_path.split("/")[-1]
    # Get the file name without extension from the s3 path
    table_name, extension = os.path.splitext(file_name)
    # If the table_name isn't a valid SQL identifier, we'll need to use something else
    table_name = (
        table_name.replace("-", "_")
        .replace(".", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )

    create_statement = (
        f"CREATE OR REPLACE TABLE '{table_name}' AS SELECT * FROM '{load_s3_path}';"
    )
    duckdb_connection.sql(create_statement)
    st.session_state["table_name"] = table_name
    st.session_state["data_loaded"] = True
    st.write(f"▶️▶️ Created table: {table_name}")
    return create_statement
