"""Gemeinsamer Kopfbereich der Streamlit-App."""

from __future__ import annotations

import streamlit as st


# Mapping von Seitentiteln zu Icons
TITEL_ICONS = {
    "Dashboard": ":material/dashboard:",
    "Patient erfassen": ":material/person_add:",
    "Patientenübersicht": ":material/people:",
    "Patientenuebersicht": ":material/people:",
    "Material erfassen": ":material/science:",
    "Kulturen ablesen": ":material/biotech:",
    "Resistenzmonitoring": ":material/functions:",
    "Patient bearbeiten": ":material/edit:",
    "Patientendetails": ":material/person:",
    "Befund": ":material/description:",
}


def _render_material_icon(icon_code: str) -> str:
    """Rendert ein Material-Icon aus dem Streamlit-Icon-Code."""
    if not icon_code.startswith(":material/") or not icon_code.endswith(":"):
        return icon_code

    icon_name = icon_code[len(":material/"):-1]
    return (
        f"<span class='material-icons' style='vertical-align: middle; font-size: 1.2em; margin-right: 0.45rem;'>"
        f"{icon_name}</span>"
    )


def show_header(title: str | None = None) -> None:
    """Zeigt den Kopfbereich der Anwendung mit optionalem Seitentitel und Logo an.

    Args:
        title: Optionaler Seitentitel für die aktuelle Ansicht.
    """
    st.markdown(
        "<link href='https://fonts.googleapis.com/icon?family=Material+Icons' rel='stylesheet'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='height: 30px; width: 100%; border-radius: 10px; background: linear-gradient(90deg, #2563eb 0%, #60a5fa 50%, #93c5fd 100%); margin-bottom: 18px;'></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 1])

    with col1:
        if title:
            icon_code = TITEL_ICONS.get(title, "")
            icon_html = _render_material_icon(icon_code) if icon_code else ""
            title_text = f"{icon_html}{title}" if icon_html else title
            st.markdown(
                f"<div style='font-size: 3.6rem; line-height: 1.05; margin: 0; font-weight: 700; color: #1d4ed8;'>{title_text}</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("<div style='margin-top: 14px'></div>", unsafe_allow_html=True)
        st.image("docs/images/BAKTOLABLOGO.jpeg", width=150)
