"""Streamlit-Seite fuer die Uebersicht aller Patienten."""

from __future__ import annotations

import streamlit as st

from domaene import Patient
from functions.gemeinsam.anzeige_hilfen import formatiere_datum, formatiere_zeitpunkt
from functions.patienten.uebersicht import (
    filtere_patienten,
    lade_patienten,
    merke_patient_fuer_detailansicht,
)


def oeffne_patientendetail(patient_id: str) -> None:
    """Merkt sich den Patienten und oeffnet die Detailansicht."""
    merke_patient_fuer_detailansicht(patient_id)
    st.switch_page("views/patientendetail.py")


def zeige_leermeldung() -> None:
    """Zeigt eine Leermeldung an, wenn noch keine Patienten vorhanden sind."""
    st.info("Es sind noch keine Patienten erfasst.")
    linke_spalte, rechte_spalte = st.columns(2)

    with linke_spalte:
        st.page_link(
            "views/patienten_erfassen.py",
            label="Patient erfassen",
            icon=":material/person_add:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )


def zeige_leermeldung_keine_treffer(suchtext: str) -> None:
    """Zeigt eine Meldung an, wenn die Suche keine Treffer liefert."""
    st.info(f"Es wurden keine Patienten zur Suche '{suchtext.strip()}' gefunden.")


def zeige_tabellenkopf() -> None:
    """Rendert den Tabellenkopf der Patientenliste."""
    spalten = st.columns((2.0, 2.0, 1.7, 1.5, 1.8, 1.2))
    ueberschriften = (
        "Vorname",
        "Nachname",
        "Geburtsdatum",
        "Geschlecht",
        "Erstellt am",
        "Aktion",
    )

    for spalte, ueberschrift in zip(spalten, ueberschriften):
        spalte.markdown(f"**{ueberschrift}**")


def zeige_patientenzeile(patient: Patient) -> None:
    """Rendert eine einzelne Zeile der Patientenliste."""
    with st.container(border=True):
        spalten = st.columns((2.0, 2.0, 1.7, 1.5, 1.8, 1.2))

        spalten[0].write(patient.vorname)
        spalten[1].write(patient.nachname)
        spalten[2].write(formatiere_datum(patient.geburtsdatum))
        spalten[3].write(patient.geschlecht)
        spalten[4].write(formatiere_zeitpunkt(patient.erstellt_am))

        if spalten[5].button(
            "Details",
            key=f"patient_detail_{patient.id}",
            use_container_width=True,
        ):
            oeffne_patientendetail(patient.id)


def main() -> None:
    """Rendert die Patientenuebersicht und bindet die Fachlogik ein."""
    st.title("Patientenuebersicht")
    st.write("Hier siehst du alle erfassten Patienten.")

    linke_spalte, rechte_spalte = st.columns(2)
    with linke_spalte:
        st.page_link(
            "views/patienten_erfassen.py",
            label="Patient erfassen",
            icon=":material/person_add:",
        )
    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )

    patienten = lade_patienten()
    if patienten is None:
        return

    if not patienten:
        zeige_leermeldung()
        return

    suchtext = st.text_input("Suche nach Vorname oder Nachname")

    gefilterte_patienten = filtere_patienten(patienten, suchtext)

    if suchtext.strip():
        st.caption(
            f"Treffer: {len(gefilterte_patienten)} von {len(patienten)} Patienten"
        )
    else:
        st.caption(f"Anzahl Patienten: {len(patienten)}")

    if not gefilterte_patienten:
        zeige_leermeldung_keine_treffer(suchtext)
        return

    zeige_tabellenkopf()
    st.divider()

    for patient in gefilterte_patienten:
        zeige_patientenzeile(patient)


main()
