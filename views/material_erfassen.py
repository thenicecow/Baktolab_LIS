from __future__ import annotations

import streamlit as st

from ui.platzhalter import zeige_platzhalterseite


def main() -> None:
    zeige_platzhalterseite(
        titel="Material erfassen",
        beschreibung=(
            "Hier entsteht die Eingabemaske zur Erfassung neuer Materialien "
            "und Proben."
        ),
        vorbereitete_punkte=[
            "Bereich für eine einfache Material- und Probenerfassung",
            "Vorbereitung für die spätere Verknüpfung mit Patienten",
            "Saubere Anschlussstelle für die dateibasierte Persistenz in Switchdrive",
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
            "views/patientenuebersicht.py",
            label="Weiter zur Patientenübersicht",
            icon=":material/groups:",
        )


main()
