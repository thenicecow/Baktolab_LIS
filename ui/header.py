"""Gemeinsamer Kopfbereich der Streamlit-App."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    hole_akzentfarbe_fuer_titel,
    hole_anzeigetext_fuer_titel,
)


TITEL_ICONS = {
    "Dashboard": ":material/dashboard:",
    "Patient erfassen": ":material/person_add:",
    "Patientenuebersicht": ":material/people:",
    "Material erfassen": ":material/science:",
    "Kulturen ablesen": ":material/biotech:",
    "Resistenzmonitoring": ":material/functions:",
    "Patient bearbeiten": ":material/edit:",
    "Patientendetails": ":material/person:",
    "Befund": ":material/description:",
    "Weitere Aktionen": ":material/menu:",
}

STANDARD_BANNER_HINTERGRUENDE = {
    "Dashboard": "linear-gradient(90deg, #2563eb 0%, #60a5fa 50%, #93c5fd 100%)",
    "Patient bearbeiten": "#94A3B8",
    "Patientendetails": "#94A3B8",
    "Weitere Aktionen": "linear-gradient(90deg, #64748B 0%, #94A3B8 50%, #CBD5E1 100%)",
}

STANDARD_TITLE_TEXT_COLORS = {
    "Dashboard": "#1d4ed8",
    "Patient bearbeiten": "#94A3B8",
    "Patientendetails": "#94A3B8",
    "Weitere Aktionen": "#475569",
}


def _render_material_icon(icon_code: str) -> str:
    """Rendert ein Material-Icon aus dem Streamlit-Icon-Code."""
    if not icon_code.startswith(":material/") or not icon_code.endswith(":"):
        return icon_code

    icon_name = icon_code[len(":material/"):-1]
    return (
        "<span class='material-icons' "
        "style='vertical-align: middle; font-size: 1.2em; margin-right: 0.45rem;'>"
        f"{icon_name}</span>"
    )


def _hole_banner_hintergrund_fuer_titel(title: str | None) -> str:
    """Liefert den farbigen Balken für den Kopfbereich einer Seite."""
    akzentfarbe = hole_akzentfarbe_fuer_titel(title)
    if akzentfarbe is not None:
        return akzentfarbe

    if title is None:
        return STANDARD_BANNER_HINTERGRUENDE["Dashboard"]

    return STANDARD_BANNER_HINTERGRUENDE.get(
        title,
        STANDARD_BANNER_HINTERGRUENDE["Dashboard"],
    )


def _hole_titelfarbe_fuer_titel(title: str | None) -> str:
    """Liefert die Titelfarbe für den Kopfbereich einer Seite."""
    akzentfarbe = hole_akzentfarbe_fuer_titel(title)
    if akzentfarbe is not None:
        return akzentfarbe

    if title is None:
        return STANDARD_TITLE_TEXT_COLORS["Dashboard"]

    return STANDARD_TITLE_TEXT_COLORS.get(
        title,
        STANDARD_TITLE_TEXT_COLORS["Dashboard"],
    )


def show_header(title: str | None = None) -> None:
    """Zeigt den Kopfbereich der Anwendung mit optionalem Seitentitel und Logo an."""
    st.markdown(
        "<link href='https://fonts.googleapis.com/icon?family=Material+Icons' rel='stylesheet'>",
        unsafe_allow_html=True,
    )

    banner_hintergrund = _hole_banner_hintergrund_fuer_titel(title)
    st.markdown(
        (
            "<div style='height: 30px; width: 100%; border-radius: 10px; "
            f"background: {banner_hintergrund}; margin-bottom: 18px;'></div>"
        ),
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([5, 1])

    with col1:
        if title:
            icon_code = TITEL_ICONS.get(title, "")
            icon_html = _render_material_icon(icon_code) if icon_code else ""
            anzeigetitel = hole_anzeigetext_fuer_titel(title) or title
            title_text = f"{icon_html}{anzeigetitel}" if icon_html else anzeigetitel
            title_color = _hole_titelfarbe_fuer_titel(title)
            st.markdown(
                (
                    "<div style='font-size: 3.6rem; line-height: 1.05; margin: 0; "
                    f"font-weight: 700; color: {title_color};'>{title_text}</div>"
                ),
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("<div style='margin-top: 14px'></div>", unsafe_allow_html=True)
        st.image("docs/images/BAKTOLABLOGO.jpeg", width=150)
