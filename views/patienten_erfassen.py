"""Streamlit-Seite zur Erfassung neuer Patienten."""

from __future__ import annotations

import streamlit as st

from functions.patienten.erfassung import (
    GEBURTSTAG_SCHLUESSEL,
    GEBURTSJAHR_SCHLUESSEL,
    GEBURTSMONAT_SCHLUESSEL,
    GESCHLECHTER,
    GESCHLECHT_SCHLUESSEL,
    MONATE,
    NACHNAME_SCHLUESSEL,
    VORNAME_SCHLUESSEL,
    hole_geburtsjahre,
    hole_monatslabel,
    hole_und_entferne_erfolgsmeldung,
    initialisiere_formularzustand,
    merke_erfolgreiche_speicherung,
    speichere_patient,
)


def main() -> None:
    """Rendert die Patientenerfassung und ruft die Fachlogik auf."""
    initialisiere_formularzustand()

    st.title("Patient erfassen")
    st.write("Hier kannst du einen neuen Patienten erfassen.")
    st.info("Die Patienten-ID wird automatisch erzeugt.")

    erfolgsmeldung = hole_und_entferne_erfolgsmeldung()
    if erfolgsmeldung:
        st.success(erfolgsmeldung)

    with st.form("patient_erfassen_formular"):
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

            st.caption("Jahre bis einschliesslich 1900 sind auswählbar.")

        with rechte_spalte:
            st.text_input("Nachname", key=NACHNAME_SCHLUESSEL)
            st.selectbox("Geschlecht", GESCHLECHTER, key=GESCHLECHT_SCHLUESSEL)

        speichern = st.form_submit_button(
            "Patient speichern",
            type="primary",
            use_container_width=True,
        )

    if speichern:
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
