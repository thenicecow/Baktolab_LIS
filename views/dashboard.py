"""Streamlit-Seite fuer das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    DASHBOARD_HINWEIS,
    DASHBOARD_UNTERTITEL,
    DashboardAktionskarte,
    hole_anzeige_name,
    hole_hauptaktionskarten,
    hole_nebenaktionskarten,
)
from ui.header import show_header


def zeige_hauptaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine grosse Aktionskarte fuer die priorisierten Hauptaktionen."""
    icon_html = ""
    title_color = karte.color or "#2563eb"
    card_class = (
        f"dashboard-card-{karte.titel.lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')}"
    )
    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2.4rem; display:block; margin: 0 auto 0.5rem; color: {title_color};'>{icon_name}</span>"
        )

    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"<div style='text-align:center; margin-bottom: 0.5rem;'><div style='font-size: 2rem; font-weight: 700; margin: 0; color: {title_color};'>{icon_html}{karte.titel}</div></div>",
            unsafe_allow_html=True,
        )
        st.write(karte.beschreibung)
        st.markdown(
            f"<style>.{card_class} .stButton button, .{card_class} button[kind='primary'], .{card_class} button[kind='secondary'] {{ background: {title_color} !important; border-color: {title_color} !important; color: white !important; }} .{card_class} .stButton button:hover, .{card_class} button[kind='primary']:hover, .{card_class} button[kind='secondary']:hover {{ background: {title_color} !important; color: white !important; }} .{card_class} .stButton button:focus, .{card_class} button[kind='primary']:focus, .{card_class} button[kind='secondary']:focus {{ outline: none !important; box-shadow: none !important; }} </style>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_hauptaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)
    st.markdown("</div>", unsafe_allow_html=True)


def zeige_nebenaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine kompaktere Aktionskarte fuer weitere Dashboard-Ziele."""
    icon_html = ""
    title_color = karte.color or "#2563eb"
    card_class = (
        f"dashboard-card-{karte.titel.lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')}"
    )
    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2rem; display:block; margin: 0 auto 0.4rem; color: {title_color};'>{icon_name}</span>"
        )

    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"<div style='text-align:center; margin-bottom: 0.4rem;'><div style='font-size: 1.4rem; font-weight: 700; margin: 0; color: {title_color};'>{icon_html}{karte.titel}</div></div>",
            unsafe_allow_html=True,
        )
        st.caption(karte.beschreibung)
        st.markdown(
            f"<style>.{card_class} button {{ background-color: {title_color} !important; border-color: {title_color} !important; color: white !important; }}</style>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_nebenaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    """Rendert das Dashboard und bindet die fachlichen Inhalte ein."""
    anzeige_name = hole_anzeige_name(st.session_state)

    show_header(title="Dashboard")

    st.caption(DASHBOARD_UNTERTITEL)
    st.write(f"Willkommen, **{anzeige_name}**.")
    st.info(DASHBOARD_HINWEIS)

    hauptaktionen = hole_hauptaktionskarten()
    if hauptaktionen:
        st.markdown("### Hauptaktionen")
        hauptaktions_spalten = st.columns(2)

        for spalte, karte in zip(hauptaktions_spalten, hauptaktionen):
            with spalte:
                zeige_hauptaktionskarte(karte)

    nebenaktionen = hole_nebenaktionskarten()
    if nebenaktionen:
        st.markdown("### Weitere Aktionen")
        nebenaktions_spalten = st.columns(len(nebenaktionen))

        for spalte, karte in zip(nebenaktions_spalten, nebenaktionen):
            with spalte:
                zeige_nebenaktionskarte(karte)




main()
