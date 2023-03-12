from os import getenv
from typing import Optional, List, Dict

import openai
import streamlit as st
from streamlit_chat import message

from app.utils.duckdb_loader import create_duckdb_conn, load_s3_path

# -*- Test Datasets
TEST_DATASETS = {
    "Titanic": "s3://phidata-public/demo_data/titanic.csv",
    "Covid": "s3://phidata-public/demo_data/titanic.csv",
}


#
# -*- Create Sidebar
#
def querybot_sidebar():
    st.sidebar.markdown("## Querybot Settings")

    # Get OpenAI API key from environment variable
    OPENAI_API_KEY: Optional[str] = getenv("OPENAI_API_KEY")
    # If not found, get it from user input
    if OPENAI_API_KEY is None:
        api_key = st.sidebar.text_input("OpenAI API key", value="sk-***", key="api_key")
        if api_key != "sk-***":
            OPENAI_API_KEY = api_key
    # Store it in session state
    if OPENAI_API_KEY is not None:
        st.session_state["OPENAI_API_KEY"] = OPENAI_API_KEY

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

    if st.sidebar.button("Load Data"):
        # Create a duckdb connection
        if "duckdb_connection" not in st.session_state:
            st.session_state["duckdb_connection"] = create_duckdb_conn()

        # Load the data into duckdb
        if s3_data_path is not None:
            load_s3_path(st.session_state["duckdb_connection"], s3_data_path)

    st.sidebar.markdown("---")
    if "OPENAI_API_KEY" in st.session_state:
        st.sidebar.markdown("🔑  OpenAI API key set")
    if "duckdb_connection" in st.session_state:
        st.sidebar.markdown("📡  duckdb connection created")
    if "data_loaded" in st.session_state:
        st.sidebar.markdown("🦆  data loaded to duckdb")
    if "table_name" in st.session_state:
        table_name = st.session_state["table_name"]
        st.sidebar.markdown(f"📊  Table: {table_name}")
        if st.sidebar.button("Show Data"):
            df = (
                st.session_state["duckdb_connection"]
                .sql(f"SELECT * FROM {table_name};")
                .fetchdf()
            )
            st.table(df.head(10))
    if st.sidebar.button("Clear Session"):
        st.session_state.clear()


def generate_response(messages: List[Dict[str, str]]) -> str:
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
        # stream=True,
        max_tokens=2048,
    )
    # st.write(completion)
    response = completion.choices[0].message
    return response


#
# -*- Create Main Page
#
def querybot_main():
    # Create a session variable to store the chat
    if "all_messages" not in st.session_state:
        st.session_state["all_messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # User query
    user_query = st.text_input("Query:", key="input")
    if user_query:
        new_message = {"role": "user", "content": user_query}
        st.session_state["all_messages"].append(new_message)

        # Generate response
        output = generate_response(st.session_state["all_messages"])
        # Store the output
        st.session_state["all_messages"].append(output)

    if st.session_state["all_messages"]:
        for msg in st.session_state["all_messages"]:
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key="user")
            elif msg["role"] == "assistant":
                message(msg["content"], key="assistant")


#
# -*- Run the app
#
st.set_page_config(page_title="Query bot", page_icon="🤖")
st.markdown("# Query bot")
st.markdown("## Run Natural Language Queries on files")
st.write(
    """Querybot uses OpenAI, DuckDb and Langchain to run Natural Language Queries on files.
    Provide a dataset, ask a question and it will respond.
    """
)

querybot_sidebar()
querybot_main()
