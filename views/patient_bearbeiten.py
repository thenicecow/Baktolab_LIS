"""Streamlit-Seite zur Bearbeitung bestehender Patienten."""

from __future__ import annotations

import streamlit as st

from functions.patienten.bearbeitung import (
    GEBURTSTAG_SCHLUESSEL,
    GEBURTSJAHR_SCHLUESSEL,
    GEBURTSMONAT_SCHLUESSEL,
    GESCHLECHT_SCHLUESSEL,
    MONATE,
    NACHNAME_SCHLUESSEL,
    VORNAME_SCHLUESSEL,
    hole_geburtsjahre,
    hole_geschlechter_optionen,
    hole_monatslabel,
    initialisiere_formularzustand,
    lade_patientenakte_fuer_bearbeitung,
    merke_erfolgreiche_bearbeitung,
    speichere_patientaenderungen,
)
from functions.patienten.navigation import (
    aktiviere_patientendetailansicht,
    deaktiviere_patientenbearbeitung,
)


def kehre_zur_patientendetailansicht_zurueck(patient_id: str) -> None:
    """Wechselt nach der Bearbeitung zur Detailansicht des Patienten innerhalb der Uebersicht zurueck."""
    deaktiviere_patientenbearbeitung()

    if not aktiviere_patientendetailansicht(patient_id):
        st.error("Die Patientendetailansicht konnte nicht geoeffnet werden.")
        return

    st.switch_page("views/patientenuebersicht.py")


def kehre_zur_patientenuebersicht_zurueck() -> None:
    """Beendet die interne Bearbeitung und wechselt zur Patientenuebersicht zurueck."""
    deaktiviere_patientenbearbeitung()
    st.switch_page("views/patientenuebersicht.py")


def main() -> None:
    """Rendert die Bearbeitungsmaske fuer einen bestehenden Patienten."""
    st.title("Patient bearbeiten")
    st.write("Hier kannst du die Stammdaten eines bestehenden Patienten bearbeiten.")

    patientenakte = lade_patientenakte_fuer_bearbeitung()
    if patientenakte is None:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurueck zur Patientenuebersicht",
            icon=":material/groups:",
        )
        return

    patient, materialien = patientenakte
    geschlecht_optionen = hole_geschlechter_optionen(patient.geschlecht)
    initialisiere_formularzustand(patient, geschlecht_optionen)

    st.caption(f"Patienten-ID: {patient.id}")
    st.info("Bearbeitbar sind Vorname, Nachname, Geburtsdatum und Geschlecht.")

    with st.form("patient_bearbeiten_formular"):
        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            st.text_input("Vorname", key=VORNAME_SCHLUESSEL)
            st.markdown("**Geburtsdatum**")
            tag_spalte, monat_spalte, jahr_spalte = st.columns(3)

            with tag_spalte:
                st.selectbox(
                    "Tag",
                    options=list(range(1, 32)),
                    key=GEBURTSTAG_SCHLUESSEL,
                )

            with monat_spalte:
                st.selectbox(
                    "Monat",
                    options=[monatsnummer for monatsnummer, _ in MONATE],
                    key=GEBURTSMONAT_SCHLUESSEL,
                    format_func=hole_monatslabel,
                )

            with jahr_spalte:
                st.selectbox(
                    "Jahr",
                    options=hole_geburtsjahre(),
                    key=GEBURTSJAHR_SCHLUESSEL,
                )

            st.caption("Jahre bis einschliesslich 1900 sind auswaehlbar.")

        with rechte_spalte:
            st.text_input("Nachname", key=NACHNAME_SCHLUESSEL)
            st.selectbox(
                "Geschlecht",
                options=list(geschlecht_optionen),
                key=GESCHLECHT_SCHLUESSEL,
            )

            st.markdown("**Nicht bearbeitbare Felder**")
            st.text_input("Erstellt von", value=patient.erstellt_von_user_id or "-", disabled=True)
            st.text_input(
                "Erstellt am",
                value=patient.erstellt_am.strftime("%d.%m.%Y %H:%M")
                if patient.erstellt_am is not None
                else "-",
                disabled=True,
            )

        linke_button_spalte, rechte_button_spalte = st.columns(2)

        with linke_button_spalte:
            abbrechen = st.form_submit_button(
                "Abbrechen",
                use_container_width=True,
            )

        with rechte_button_spalte:
            speichern = st.form_submit_button(
                "Aenderungen speichern",
                type="primary",
                use_container_width=True,
            )

    if abbrechen:
        kehre_zur_patientendetailansicht_zurueck(patient.id)

    if speichern:
        erfolgsmeldung = speichere_patientaenderungen(patient, materialien)
        if erfolgsmeldung is not None:
            merke_erfolgreiche_bearbeitung(erfolgsmeldung)
            kehre_zur_patientendetailansicht_zurueck(patient.id)

    if st.button(
        "Zurueck zur Patientenuebersicht",
        use_container_width=True,
    ):
        kehre_zur_patientenuebersicht_zurueck()


main()
