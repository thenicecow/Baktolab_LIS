import streamlit as st

def show_header(title=None):
    """Displays the application header with an optional title and a logo.
    Args:
        title (str, optional): The title to display in the header. Defaults to None.
    """
    col1, col2 = st.columns([5, 1])

    with col1:
        if title:
            st.title(title)

    with col2:
        st.image("docs/images/BAKTOLABLOGO.jpeg", width=150)