"""Zentrale Streamlit-Navigation der App."""

from __future__ import annotations

import streamlit as st


SICHTBARE_NAVIGATION_URL_SCHLUESSEL = "sichtbare_navigation_url"

DASHBOARD_URL_PFAD = "dashboard"
PATIENTEN_ERFASSEN_URL_PFAD = "patienten-erfassen"
PATIENTENUEBERSICHT_URL_PFAD = "patientenuebersicht"
MATERIAL_ERFASSEN_URL_PFAD = "material-erfassen"
KULTUREN_ABLESEN_URL_PFAD = "kulturen-ablesen"
RESISTENZRECHNER_URL_PFAD = "rechner-resistenzmonitoring"


def erstelle_navigation():
    """Erzeugt die sichtbare Hauptnavigation der App."""
    return st.navigation(
        [
            st.Page(
                "views/dashboard.py",
                title="Dashboard",
                icon=":material/dashboard:",
                default=True,
                url_path=DASHBOARD_URL_PFAD,
            ),
            st.Page(
                "views/patienten_erfassen.py",
                title="Patienten erfassen",
                icon=":material/person_add:",
                url_path=PATIENTEN_ERFASSEN_URL_PFAD,
            ),
            st.Page(
                "views/patientenuebersicht.py",
                title="Patientenuebersicht",
                icon=":material/groups:",
                url_path=PATIENTENUEBERSICHT_URL_PFAD,
            ),
            st.Page(
                "views/material_erfassen.py",
                title="Material erfassen",
                icon=":material/science:",
                url_path=MATERIAL_ERFASSEN_URL_PFAD,
            ),
            st.Page(
                "views/kulturen_ablesen.py",
                title="Kulturen ablesen",
                icon=":material/biotech:",
                url_path=KULTUREN_ABLESEN_URL_PFAD,
            ),
            st.Page(
                "views/addition_calculator.py",
                title="Rechner Resistenzmonitoring",
                icon=":material/functions:",
                url_path=RESISTENZRECHNER_URL_PFAD,
            ),
        ]
    )


def hole_sichtbare_navigation_url(navigationseintrag: object) -> str | None:
    """Liest den URL-Pfad der aktuell in der Seitenleiste gewaehlten sichtbaren Seite."""
    url_path = getattr(navigationseintrag, "url_path", None)

    if not isinstance(url_path, str):
        return None

    bereinigt = url_path.strip()
    return bereinigt or None
