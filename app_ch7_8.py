import streamlit as st

if "learned_concepts" not in st.session_state:
    st.session_state.learned_concepts = {
        "7": set(),
        "8": set()
    }
