import streamlit as st
from langdetect import detect
from iso639 import languages

st.title("Language Detector")

text = "Enter text to detect language"
st.text_input("Enter text to detect language", value=text, key="text")

res = detect(st.session_state.text)

st.write(languages.get(alpha2=res).name)
