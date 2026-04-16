from __future__ import annotations

import streamlit as st

from ui.platzhalter import zeige_platzhalterseite


def main() -> None:
    zeige_platzhalterseite(
        titel="Patienten erfassen",
        beschreibung=(
            "Hier entsteht die Eingabemaske zur Erfassung neuer Patienten für das "
            "Laborinformationssystem."
        ),
        vorbereitete_punkte=[
            "Bereich für eine einfache Erfassungsmaske mit deutschen Feldbezeichnungen",
            "Anschluss an spätere Metadaten wie erstellt_am und erstellt_von_user_id",
            "Saubere Vorbereitung für die dateibasierte Persistenz in Switchdrive",
        ],
    )

    linke_spalte, rechte_spalte = st.columns(2)
    with linke_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurück zum Dashboard",
            icon=":material/dashboard:",
        )
    with rechte_spalte:
        st.page_link(
            "views/material_erfassen.py",
            label="Weiter zu Material erfassen",
            icon=":material/science:",
        )


main()
