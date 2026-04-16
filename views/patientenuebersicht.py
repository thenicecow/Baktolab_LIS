from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import Patient
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"


def formatiere_geburtsdatum(geburtsdatum: date) -> str:
    return geburtsdatum.strftime("%d.%m.%Y")


def formatiere_erstellt_am(erstellt_am: datetime | None) -> str:
    if erstellt_am is None:
        return "-"

    return erstellt_am.strftime("%d.%m.%Y %H:%M")


def sortiere_patienten(patienten: list[Patient]) -> list[Patient]:
    return sorted(
        patienten,
        key=lambda patient: (
            patient.erstellt_am is not None,
            patient.erstellt_am.timestamp() if patient.erstellt_am is not None else float("-inf"),
        ),
        reverse=True,
    )


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
        spalten[2].write(formatiere_geburtsdatum(patient.geburtsdatum))
        spalten[3].write(patient.geschlecht)
        spalten[4].write(formatiere_erstellt_am(patient.erstellt_am))

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
    except Exception as exc:
        st.error(f"Die Patienten konnten nicht geladen werden: {exc}")
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

    st.caption(f"Anzahl Patienten: {len(patienten)}")

    zeige_tabellenkopf()
    st.divider()

    for patient in patienten:
        zeige_patientenzeile(patient)


main()
