import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

st.write("# Welcome to your ML App!")

st.write(
    "Built using Phidata[https://phidata.com], [Streamlit](https://streamlit.io) and [FastAPI](https://fastapi.tiangolo.com)"  # noqa: E501
)

st.sidebar.success("Select a ML app above")
