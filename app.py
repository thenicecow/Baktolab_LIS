"""Einstiegspunkt und Router der Streamlit-App."""

from __future__ import annotations

import streamlit as st

from functions.kulturen.navigation import (
    deaktiviere_kulturen_ablesen,
    ist_kulturen_ablesen_aktiv,
)
from functions.patienten.navigation import (
    deaktiviere_patientenbearbeitung,
    deaktiviere_patientendetailansicht,
    ist_patientenbearbeitung_aktiv,
    ist_patientendetailansicht_aktiv,
)
from ui.navigation import (
    KULTUREN_ABLESEN_URL_PFAD,
    PATIENTENUEBERSICHT_URL_PFAD,
    SICHTBARE_NAVIGATION_URL_SCHLUESSEL,
    erstelle_navigation,
    hole_sichtbare_navigation_url,
)
from utils.data_manager import DataManager
from utils.login_manager import LoginManager


st.set_page_config(
    page_title="Baktolab",
    page_icon=":material/biotech:",
    layout="wide",
)


data_manager = DataManager(
    fs_protocol="webdav",
    fs_root_folder="BMLD_APP_DATA",
)
login_manager = LoginManager(data_manager)
login_manager.login_register(
    login_title="Anmelden",
    register_title="Benutzerkonto erstellen",
)

navigation = erstelle_navigation()
aktuelle_sichtbare_navigation_url = hole_sichtbare_navigation_url(navigation)

if aktuelle_sichtbare_navigation_url is not None:
    st.session_state[SICHTBARE_NAVIGATION_URL_SCHLUESSEL] = aktuelle_sichtbare_navigation_url
else:
    st.session_state.pop(SICHTBARE_NAVIGATION_URL_SCHLUESSEL, None)

if (
    aktuelle_sichtbare_navigation_url != KULTUREN_ABLESEN_URL_PFAD
    and ist_kulturen_ablesen_aktiv()
):
    deaktiviere_kulturen_ablesen()

if aktuelle_sichtbare_navigation_url != PATIENTENUEBERSICHT_URL_PFAD:
    if ist_patientenbearbeitung_aktiv():
        deaktiviere_patientenbearbeitung()

    if ist_patientendetailansicht_aktiv():
        deaktiviere_patientendetailansicht()

navigation.run()
