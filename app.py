from utils.data_manager import DataManager
from utils.login_manager import LoginManager

data_manager = DataManager(
    fs_protocol='webdav',
    fs_root_folder='BMLD_APP_DATA'
)
login_manager = LoginManager(data_manager)
login_manager.login_register()

import streamlit as st

st.set_page_config(page_title="Meine App", page_icon=":material/home:")

pg_home = st.Page("views/home.py", title="Home", icon=":material/home:", default=True)
pg_second = st.Page("views/addition_calculator.py", title="Rechner Resistenzmonitoring", icon=":material/info:")
placeholder = st.Page("views/placeholder.py", title="Placeholder", icon=":material/info:")
pg = st.navigation([pg_home, pg_second, placeholder])
pg.run()
