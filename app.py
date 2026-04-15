from __future__ import annotations

import streamlit as st

from ui.navigation import erstelle_navigation
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
navigation.run()

