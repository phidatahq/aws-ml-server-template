import streamlit as st

st.set_page_config(
    page_title="ML Apps",
    page_icon="🚝",
)

st.write("## ML Apps!")
st.write(
    "- Built using [Streamlit](https://streamlit.io), [FastAPI](https://fastapi.tiangolo.com) and [Phidata](https://phidata.com)"  # noqa: E501
)

st.sidebar.success("Select an App from above")
