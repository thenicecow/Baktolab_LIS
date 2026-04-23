"""Gemeinsamer Kopfbereich der Streamlit-App."""

from __future__ import annotations

import streamlit as st


def show_header(title: str | None = None) -> None:
    """Zeigt den Kopfbereich der Anwendung mit optionalem Seitentitel und Logo an.

    Args:
        title: Optionaler Seitentitel für die aktuelle Ansicht.
    """
    col1, col2 = st.columns([5, 1])

    with col1:
        if title:
            st.title(title)

    with col2:
        st.image("docs/images/BAKTOLABLOGO.jpeg", width=150)
