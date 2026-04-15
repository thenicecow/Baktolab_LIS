from __future__ import annotations

import streamlit as st

from ui.platzhalter import zeige_platzhalterseite


def main() -> None:
    zeige_platzhalterseite(
        titel="Patientenübersicht",
        beschreibung=(
            "Hier entsteht die gemeinsame Übersicht aller Patienten. Später sehen "
            "alle angemeldeten Benutzer denselben Datenbestand."
        ),
        vorbereitete_punkte=[
            "Platzhalter für eine spätere Liste aller Patienten",
            "Vorbereitung für eine gemeinsame, nicht benutzerspezifische Datenablage",
            "Trennung von Anzeige, Domänenmodell und dateibasierter Persistenz",
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
            "views/patienten_erfassen.py",
            label="Zu Patienten erfassen",
            icon=":material/person_add:",
        )


main()
