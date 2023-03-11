import streamlit as st
from streamlit_observable import observable

st.title("US County Selector")

observers = observable(
    "County Brush",
    notebook="d/4f9aa5feff9761c9",
    targets=["viewof countyCodes"],
    observe=["selectedCounties"],
)

selectedCounties = observers.get("selectedCounties")
