"""Streamlit-Seite fuer das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    DASHBOARD_HINWEIS,
    DASHBOARD_STANDPUNKTE,
    DASHBOARD_UNTERTITEL,
    DashboardAktionskarte,
    hole_anzeige_name,
    hole_hauptaktionskarten,
    hole_nebenaktionskarten,
)
from ui.header import show_header


def zeige_hauptaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine grosse Aktionskarte fuer die priorisierten Hauptaktionen."""
    with st.container(border=True):
        st.subheader(karte.titel)
        st.write(karte.beschreibung)

        if st.button(
            karte.button_text,
            use_container_width=True,
            type=karte.button_typ,
        ):
            st.switch_page(karte.seitenpfad)


def zeige_nebenaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine kompaktere Aktionskarte fuer weitere Dashboard-Ziele."""
    with st.container(border=True):
        st.markdown(f"**{karte.titel}**")
        st.caption(karte.beschreibung)

        if st.button(
            karte.button_text,
            use_container_width=True,
            type=karte.button_typ,
        ):
            st.switch_page(karte.seitenpfad)


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

    st.markdown("### Aktueller Stand")
    for standpunkt in DASHBOARD_STANDPUNKTE:
        st.markdown(f"- {standpunkt}")


main()
