from os import getenv
from typing import Optional, List, Dict

import openai
import streamlit as st
from streamlit_chat import message

from app.utils.duckdb_loader import create_duckdb, load_files

#
# -*- Get OpenAI API key
#
# Get OpenAI API key from environment variable
openai_api_key: Optional[str] = getenv("OPENAI_API_KEY")
# If not found, get it from user input
if openai_api_key is None:
    text = "Enter OpenAI API key"
    st.text_input("Enter Openai API key", value=text, key="api_key")
    openai_api_key = text


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


def querybot_demo():
    from streamlit.runtime.uploaded_file_manager import UploadedFile

    # Create session variable to store the chat
    if "all_messages" not in st.session_state:
        st.session_state["all_messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # Create a duckdb connection
    if "duckdb_connection" not in st.session_state:
        st.session_state["duckdb_connection"] = create_duckdb()
        st.write("✅  Created duckdb connection")

    # Load files into duckdb
    if "files" not in st.session_state:
        st.session_state["files"] = []

    uploaded_files: List[UploadedFile] = st.file_uploader(
        "Upload files",
        type=["csv", "json", "parquet", "txt"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        st.write("Uploading files:")
        for uploaded_file in uploaded_files:
            st.session_state["files"].append(uploaded_file)
            st.write(f"\t    - {uploaded_file.name}")

        executed_sql = load_files(
            st.session_state["duckdb_connection"], st.session_state["files"]
        )
        st.write(f"executed_sql: {executed_sql}")
        executed_sql_str = "\n".join(executed_sql)
        st.write(f"Files loaded using:\n{executed_sql_str}")
        st.write("✅  Loaded file into duckdb")

    user_message = st.text_input("Message:", key="input")
    if user_message:
        new_message = {"role": "user", "content": user_message}
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


st.set_page_config(page_title="Query bot", page_icon="🤖")
st.markdown("# Query a dataset using GPT-3.5 Turbo")
st.write(
    """Querybot runs Natural Language Queries on files.
    Built using Langchain and OpenAI.
    Provide a dataset, ask a question and it will respond.
    """
)

st.sidebar.header("Querybot Demo")
querybot_demo()
