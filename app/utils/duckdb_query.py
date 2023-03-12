import duckdb


def run_sql(duckdb_connection: duckdb.DuckDBPyConnection, sql: str):
    # Remove backtics
    sql = sql.replace("`", "")
    # If there are multiple statements, only run the first one
    sql = sql.split(";")[0]
    try:
        result = duckdb_connection.sql(sql)
        if result is None:
            rendered_output = "No output"
        else:
            try:
                results_as_python_objects = result.fetchall()
                rendered_rows = []
                for row in results_as_python_objects:
                    if len(row) == 1:
                        rendered_rows.append(str(row[0]))
                    else:
                        rendered_rows.append(",".join(str(x) for x in row))

                rendered_data = "\n".join(rendered_rows)
                rendered_output = ",".join(result.columns) + "\n" + rendered_data
            except AttributeError:
                rendered_output = str(result)
        return rendered_output
    except duckdb.ProgrammingError as e:
        return str(e)
    except duckdb.Error as e:
        return str(e)
    except Exception as e:
        return str(e)


def describe_table_or_view(duckdb_connection, table):
    statement = f"select column_name, data_type from information_schema.columns where table_name='{table}';"
    table_description = run_sql(duckdb_connection, statement)
    return f"{table}\n{table_description}"
