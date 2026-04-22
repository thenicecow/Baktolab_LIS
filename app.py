"""Einstiegspunkt und Router der Streamlit-App."""

from __future__ import annotations

from pathlib import Path
import runpy

import streamlit as st

from functions.kulturen.navigation import (
    deaktiviere_kulturen_ablesen,
    hat_gueltige_kulturen_ablesen_route,
    ist_kulturen_ablesen_aktiv,
)
from functions.patienten.navigation import (
    deaktiviere_patientendetailansicht,
    hat_gueltige_patientendetail_route,
    ist_patientendetailansicht_aktiv,
)
from ui.navigation import erstelle_navigation
from utils.data_manager import DataManager
from utils.login_manager import LoginManager


st.set_page_config(
    page_title="Baktolab",
    page_icon=":material/biotech:",
    layout="wide",
)


def zeige_patientendetailansicht() -> None:
    """Fuehrt die interne Patientendetailansicht aus."""
    detailansicht_pfad = Path(__file__).parent / "views" / "patientendetail.py"
    runpy.run_path(str(detailansicht_pfad), run_name="__main__")


def zeige_kulturen_ablesen() -> None:
    """Fuehrt die interne Seite ``Kulturen ablesen`` aus."""
    kulturen_ablesen_pfad = Path(__file__).parent / "views" / "kulturen_ablesen.py"
    runpy.run_path(str(kulturen_ablesen_pfad), run_name="__main__")


data_manager = DataManager(
    fs_protocol="webdav",
    fs_root_folder="BMLD_APP_DATA",
)
login_manager = LoginManager(data_manager)
login_manager.login_register(
    login_title="Anmelden",
    register_title="Benutzerkonto erstellen",
)

kulturen_ablesen_aktiv = ist_kulturen_ablesen_aktiv()

if hat_gueltige_kulturen_ablesen_route():
    zeige_kulturen_ablesen()
else:
    if kulturen_ablesen_aktiv:
        deaktiviere_kulturen_ablesen()
        st.warning(
            "Die Seite 'Kulturen ablesen' konnte nicht geoeffnet werden, "
            "weil keine gueltige Materialreferenz vorhanden ist."
        )

    detailansicht_aktiv = ist_patientendetailansicht_aktiv()

    if hat_gueltige_patientendetail_route():
        zeige_patientendetailansicht()
    else:
        if detailansicht_aktiv:
            deaktiviere_patientendetailansicht()
            st.warning(
                "Die Patientendetailansicht konnte nicht geoeffnet werden, "
                "weil keine gueltige Patienten-ID vorhanden ist."
            )

        navigation = erstelle_navigation()
        navigation.run()
