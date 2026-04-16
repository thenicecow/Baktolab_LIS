from __future__ import annotations

import streamlit as st

from domaene import Patient
from persistenz import PatientenRepository
from ui.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_zeitpunkt,
)


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"


def sortiere_patienten(patienten: list[Patient]) -> list[Patient]:
    return sorted(
        patienten,
        key=lambda patient: (
            patient.erstellt_am is not None,
            patient.erstellt_am.timestamp() if patient.erstellt_am is not None else float("-inf"),
        ),
        reverse=True,
    )


def filtere_patienten(patienten: list[Patient], suchtext: str) -> list[Patient]:
    suchtext_bereinigt = suchtext.strip().casefold()

    if not suchtext_bereinigt:
        return patienten

    return [
        patient
        for patient in patienten
        if suchtext_bereinigt in patient.vorname.casefold()
        or suchtext_bereinigt in patient.nachname.casefold()
    ]


def oeffne_patientendetail(patient_id: str) -> None:
    st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = patient_id
    st.switch_page("views/patientendetail.py")


def zeige_leermeldung() -> None:
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
    st.info(f"Es wurden keine Patienten zur Suche '{suchtext.strip()}' gefunden.")


def zeige_tabellenkopf() -> None:
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


def lade_patienten() -> list[Patient] | None:
    repository = PatientenRepository()

    try:
        patienten = repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None

    return sortiere_patienten(patienten)


def main() -> None:
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

