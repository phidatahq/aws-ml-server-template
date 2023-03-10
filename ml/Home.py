import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Phidata!")

st.write("Operating System for data teams")

st.write(
    "Plug-n-play tools for building data products. Run locally using docker and production on AWS"
)

st.sidebar.success("Select a ML app above")
