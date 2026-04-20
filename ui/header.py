import streamlit as st

def show_header(title=None):
    col1, col2 = st.columns([5, 1])

    with col1:
        if title:
            st.title(title)

    with col2:
        st.image("docs/images/BAKTOLABLOGO.jpeg", width=100)