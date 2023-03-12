import os
from typing import List

import duckdb
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile


def create_duckdb(duckdb_path: str = ":memory:") -> duckdb.DuckDBPyConnection:
    # By default, duckdb is fully in-memory - we can provide a path to get
    # persistent storage

    duckdb_connection = duckdb.connect(duckdb_path)
    try:
        duckdb_connection.sql("INSTALL httpfs;")
        duckdb_connection.sql("LOAD httpfs;")
    except Exception:
        print(
            "Failed to install httpfs extension. Only loading from local files will be supported"
        )

    duckdb_connection.sql(
        "create temporary table if not exists _qabot_queries(query VARCHAR PRIMARY KEY, result VARCHAR)"
    )

    return duckdb_connection


def load_file(
    duckdb_connection: duckdb.DuckDBPyConnection, uploaded_file: UploadedFile
) -> str:
    # Get the file name without extension from the uploaded_file
    table_name, extension = os.path.splitext(uploaded_file.name)
    if extension == ".csv":
        duckdb.read_csv(uploaded_file)
    # elif extension == ".json":
    #     duckdb.read_json(uploaded_file)
    # elif extension == ".parquet":
    #     duckdb.read_parquet(uploaded_file)

    # If the table_name isn't a valid SQL identifier, we'll need to use something else
    table_name = (
        table_name.replace("-", "_")
        .replace(".", "_")
        .replace(" ", "_")
        .replace("/", "_")
    )
    create_statement = (
        f"create table '{table_name}' as select * from '{uploaded_file}';"
    )
    st.write(f"create_statement: {create_statement}")
    st.write(f"Created table: {table_name} from: {uploaded_file.name}")
    # duckdb_connection.sql(create_statement)
    return create_statement


def load_files(
    duckdb_connection: duckdb.DuckDBPyConnection, files: List[UploadedFile]
) -> List[str]:
    executed_sql = []
    for file_path in files:
        executed_sql.append(load_file(duckdb_connection, file_path))
    return executed_sql
