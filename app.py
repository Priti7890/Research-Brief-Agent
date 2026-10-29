import logging
import streamlit as st
from pipeline import research_brief

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

st.title("Research Brief Agent")
topic = st.text_input("Enter a topic")
if st.button("Get brief") and topic.strip():
    with st.spinner("Searching and summarizing..."):
        st.markdown(research_brief(topic.strip()))