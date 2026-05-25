"""Streamlit-Seite zur Erfassung neuer Patienten."""

from __future__ import annotations

from datetime import date

import streamlit as st

from functions.patienten.erfassung import (
    GEBURTSTAG_SCHLUESSEL,
    GEBURTSJAHR_SCHLUESSEL,
    GEBURTSMONAT_SCHLUESSEL,
    GESCHLECHTER,
    GESCHLECHT_SCHLUESSEL,
    NACHNAME_SCHLUESSEL,
    VORNAME_SCHLUESSEL,
    hole_und_entferne_erfolgsmeldung,
    initialisiere_formularzustand,
    merke_erfolgreiche_speicherung,
    speichere_patient,
)
from ui.header import show_header


GEBURTSDATUM_KALENDER_SCHLUESSEL = "geburtsdatum_kalender"


def hole_vorausgewaehltes_geburtsdatum() -> date:
    """Erzeugt ein Datum aus dem bestehenden Formularzustand."""
    tag = st.session_state.get(GEBURTSTAG_SCHLUESSEL, 1)
    monat = st.session_state.get(GEBURTSMONAT_SCHLUESSEL, 1)
    jahr = st.session_state.get(GEBURTSJAHR_SCHLUESSEL, 2000)

    try:
        return date(int(jahr), int(monat), int(tag))
    except ValueError:
        return date(2000, 1, 1)


def uebertrage_kalenderdatum_in_formularzustand(geburtsdatum: date) -> None:
    """Speichert das Kalenderdatum in den bisherigen Tag-, Monat- und Jahr-Schlüsseln."""
    st.session_state[GEBURTSTAG_SCHLUESSEL] = geburtsdatum.day
    st.session_state[GEBURTSMONAT_SCHLUESSEL] = geburtsdatum.month
    st.session_state[GEBURTSJAHR_SCHLUESSEL] = geburtsdatum.year


def main() -> None:
    """Rendert die Patientenerfassung und ruft die Fachlogik auf."""
    initialisiere_formularzustand()

    show_header("Patient erfassen")
    st.write("Hier kannst du einen neuen Patienten erfassen.")
    st.info("Die Patienten-ID wird automatisch erzeugt.")

    erfolgsmeldung = hole_und_entferne_erfolgsmeldung()
    if erfolgsmeldung:
        st.success(erfolgsmeldung)

    with st.form("patient_erfassen_formular"):
        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            st.text_input("Vorname", key=VORNAME_SCHLUESSEL)

            geburtsdatum = st.date_input(
                "Geburtsdatum",
                value=hole_vorausgewaehltes_geburtsdatum(),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                format="DD.MM.YYYY",
                key=GEBURTSDATUM_KALENDER_SCHLUESSEL,
            )

            st.caption("Das Geburtsdatum kann direkt im Kalender ausgewählt werden.")

        with rechte_spalte:
            st.text_input("Nachname", key=NACHNAME_SCHLUESSEL)
            st.selectbox("Geschlecht", GESCHLECHTER, key=GESCHLECHT_SCHLUESSEL)

        speichern = st.form_submit_button(
            "Patient speichern",
            type="primary",
            use_container_width=True,
        )

    if speichern:
        uebertrage_kalenderdatum_in_formularzustand(geburtsdatum)

        neue_erfolgsmeldung = speichere_patient()
        if neue_erfolgsmeldung is not None:
            merke_erfolgreiche_speicherung(neue_erfolgsmeldung)
            st.rerun()

    st.page_link(
        "views/dashboard.py",
        label="Zurück zum Dashboard",
        icon=":material/dashboard:",
    )


main()