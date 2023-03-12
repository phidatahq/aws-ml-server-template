import os
from typing import Optional

import streamlit as st
from streamlit_chat import message

from app.utils.duckdb_agent import create_duckdb_llm_agent
from app.utils.duckdb_loader import create_duckdb_conn, load_s3_path
from app.utils.duckdb_query import run_sql

# -*- Test Datasets
TEST_DATASETS = {
    "Titanic": "s3://phidata-public/demo_data/titanic.csv",
    "Census": "s3://phidata-public/demo_data/census_2017.csv",
    "Covid": "s3://phidata-public/demo_data/covid_19_data.csv",
    "Air Quality": "s3://phidata-public/demo_data/air_quality.csv",
}


#
# -*- Create Sidebar
#
def querybot_sidebar():
    st.sidebar.markdown("## Querybot Settings")

    # Get OpenAI API key from environment variable
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    # If not found, get it from user input
    if OPENAI_API_KEY is None:
        api_key = st.sidebar.text_input("OpenAI API key", value="sk-***", key="api_key")
        if api_key != "sk-***":
            OPENAI_API_KEY = api_key
    # Store it in session state and environment variable
    if OPENAI_API_KEY is not None:
        st.session_state["OPENAI_API_KEY"] = OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    # Get the data source
    data_source = st.sidebar.radio("Select Data Source", options=["Test Data", "S3"])
    st.session_state["data_source"] = data_source

    s3_data_path = None
    if data_source == "Test Data":
        selected_test_dataset = st.sidebar.selectbox(
            "Select Dataset", TEST_DATASETS.keys()
        )
        if selected_test_dataset in TEST_DATASETS:
            s3_data_path = TEST_DATASETS[selected_test_dataset]
    elif data_source == "S3":
        selected_s3_path = st.sidebar.text_input(
            "S3 Path", value="s3://bucket-name/path/to/file"
        )
        s3_data_path = selected_s3_path
    st.session_state["s3_data_path"] = s3_data_path

    st.sidebar.markdown("---")
    st.sidebar.markdown("## Querybot Status")
    if "OPENAI_API_KEY" in st.session_state:
        st.sidebar.markdown("🔑  OpenAI API key set")
    if "duckdb_connection" in st.session_state:
        st.sidebar.markdown("📡  duckdb connection created")
    if "data_loaded" in st.session_state:
        st.sidebar.markdown("🦆  data loaded to duckdb")
    if "agent" in st.session_state:
        st.sidebar.markdown("🤖  agent created")

    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Create Main Page
#
def querybot_main():
    st.markdown("---")

    # Load data from S3 into duckdb
    duckdb_connection = st.session_state.get("duckdb_connection", None)
    s3_data_path = st.session_state.get("s3_data_path", None)
    executed_queries = None
    if st.button("Read Data"):
        if duckdb_connection is None:
            # Create a duckdb connection
            if "duckdb_connection" not in st.session_state:
                duckdb_connection = create_duckdb_conn()
                st.session_state["duckdb_connection"] = duckdb_connection

        # Load data into duckdb
        if duckdb_connection is not None and s3_data_path is not None:
            executed_queries = load_s3_path(duckdb_connection, s3_data_path)

    # Check if table is loaded
    table_name = st.session_state.get("table_name")
    if table_name is None:
        st.write("🦆  Waiting for data")
        return
    else:
        st.write(f"🦆  {table_name} loaded")

    # Create an OpenAI agent
    agent = st.session_state.get("agent")
    if agent is None:
        agent = create_duckdb_llm_agent(duckdb_connection=duckdb_connection)
        st.session_state["agent"] = agent
    if agent is not None:
        st.write("🤖  LLM Agent created")

    # Create a session variable to store the chat
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            {
                "role": "system",
                "content": f"""
                Startup SQL Queries:
                ```
                {executed_queries}
                ```
            """,
            }
        ]

    # User query
    user_query = st.text_input("Query:", key="input")
    if user_query:
        new_message = {"role": "user", "content": user_query}
        st.session_state["chat_history"].append(new_message)
        inputs = {
            "input": st.session_state["chat_history"],
            "table_names": run_sql(duckdb_connection, "show tables"),
        }
        # Generate response
        result = agent(inputs)
        # st.write(result)
        # Store the output
        if "output" in result:
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": result["output"]}
            )
        else:
            st.session_state["chat_history"].append(
                {
                    "role": "assistant",
                    "content": "Could not understand, please try again",
                }
            )

    if st.session_state["chat_history"]:
        for i in range(len(st.session_state["chat_history"]) - 1, -1, -1):
            msg = st.session_state["chat_history"][i]
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=str(i))
            elif msg["role"] == "assistant":
                message(msg["content"], key=str(i))
            elif msg["role"] == "system":
                message(msg["content"], key=str(i), seed=42)

        # for msg in st.session_state["chat_history"]:
        #     if msg["role"] == "user":
        #         message(msg["content"], is_user=True)
        #     elif msg["role"] == "assistant":
        #         message(msg["content"])

    st.markdown("---")
    # Show the data
    if "table_name" in st.session_state:
        table_name = st.session_state["table_name"]
        if st.session_state.get("show_data", True):
            if st.button(f"📊  Show table: {table_name}"):
                st.session_state["show_data"] = True

        if st.session_state.get("show_data", False):
            df = (
                st.session_state["duckdb_connection"]
                .sql(f"SELECT * FROM {table_name};")
                .fetchdf()
            )
            st.table(df.head(10))


#
# -*- Run the app
#
st.set_page_config(page_title="Query bot", page_icon="🤖")
st.markdown("## Run Natural Language Queries on files")
st.write(
    """Querybot uses OpenAI, DuckDb and Langchain to run Natural Language Queries on files.
    Provide a dataset, ask a question and it will respond.
    """
)

querybot_sidebar()
querybot_main()
