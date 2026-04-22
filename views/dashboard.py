"""Streamlit-Seite fuer das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    DASHBOARD_HINWEIS,
    DASHBOARD_STANDPUNKTE,
    DASHBOARD_UNTERTITEL,
    DashboardAktionskarte,
    hole_anzeige_name,
    hole_dashboard_aktionskarten,
)
from ui.header import show_header


def zeige_aktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine Aktionskarte mit Navigation."""
    with st.container(border=True):
        st.subheader(karte.titel)
        st.write(karte.beschreibung)

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

    karten = hole_dashboard_aktionskarten()
    spalten = st.columns(len(karten))

    for spalte, karte in zip(spalten, karten):
        with spalte:
            zeige_aktionskarte(karte)

    st.markdown("### Aktueller Stand")
    for standpunkt in DASHBOARD_STANDPUNKTE:
        st.markdown(f"- {standpunkt}")


main()
