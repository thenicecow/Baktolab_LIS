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

st.markdown(
    """
    <style>
    /* Gesamthintergrund: etwas kräftigeres, modernes Hellblau */
    body, .stApp {
        background: linear-gradient(180deg, #cfe5ff 0%, #b7d7ff 100%) !important;
        color: #1f2937 !important;
    }

    /* Hauptbereich */
    .block-container {
        background: #ffffff !important;
        border-radius: 18px !important;
        padding: 2rem !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #e0efff !important;
        border-right: none !important;
    }

    /* Alle Buttons: rote Umrandung + rot entfernen */
    .stButton > button,
    button[kind="primary"],
    button[kind="secondary"],
    .stDownloadButton > button,
    .stForm button {
        background: #3b82f6 !important;
        color: white !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
    }

    /* Hover */
    .stButton > button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    .stDownloadButton > button:hover,
    .stForm button:hover {
        background: #2563eb !important;
        color: white !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* Fokus / Klick: rote oder blaue Outline komplett entfernen */
    .stButton > button:focus,
    .stButton > button:active,
    button:focus,
    button:active,
    button:focus-visible {
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Inputfelder wieder normaler statt extra rund/blau */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input,
    .stSelectbox div,
    .stMultiselect div {
        background: white !important;
        color: #111827 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }

    /* Fokus Inputs neutral */
    input:focus,
    textarea:focus,
    select:focus {
        outline: none !important;
        box-shadow: none !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Tabs */
    .stTabs [role="tab"] {
        background: #dbeafe !important;
        color: #1e3a8a !important;
        border-radius: 4px 4px 0 0 !important;
    }

    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }

    /* Container */
    .stContainer, .stExpander, .stMetric, .stDataFrame, .stTable {
        background: white !important;
        border: 1px solid #dbeafe !important;
        box-shadow: none !important;
        border-radius: 10px !important;
    }

    /* Überschriften */
    h1, h2, h3, h4 {
        color: #1d4ed8 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
