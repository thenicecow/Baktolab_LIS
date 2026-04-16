from __future__ import annotations

import streamlit as st


def erstelle_navigation():
    return st.navigation(
        {
            "Start": [
                st.Page(
                    "views/dashboard.py",
                    title="Dashboard",
                    icon=":material/dashboard:",
                    default=True,
                ),
                st.Page(
                    "views/patienten_erfassen.py",
                    title="Patienten erfassen",
                    icon=":material/person_add:",
                ),
                st.Page(
                    "views/material_erfassen.py",
                    title="Material erfassen",
                    icon=":material/science:",
                ),
                st.Page(
                    "views/patientenuebersicht.py",
                    title="Patientenübersicht",
                    icon=":material/groups:",
                ),
            ],
            "Weitere Funktionen": [
                st.Page(
                    "views/addition_calculator.py",
                    title="Rechner Resistenzmonitoring",
                    icon=":material/functions:",
                ),
            ],
        }
    )
