from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"


def formatiere_geburtsdatum(geburtsdatum: date) -> str:
    return geburtsdatum.strftime("%d.%m.%Y")


def formatiere_erstellt_am(erstellt_am: datetime | None) -> str:
    if erstellt_am is None:
        return "-"

    return erstellt_am.strftime("%d.%m.%Y %H:%M")


def main() -> None:
    st.title("Patientendetail")

    patient_id = st.session_state.get(PATIENTENDETAIL_ID_SCHLUESSEL)
    if not isinstance(patient_id, str) or not patient_id.strip():
        st.info("Es wurde noch kein Patient ausgewaehlt.")
    else:
        repository = PatientenRepository()

        try:
            patient = repository.lade_patient_nach_id(patient_id)
        except Exception as exc:
            st.error(f"Der ausgewaehlte Patient konnte nicht geladen werden: {exc}")
            patient = None

        if patient is None:
            st.warning("Der ausgewaehlte Patient wurde nicht gefunden.")
        else:
            st.write("Die Detailansicht wird im naechsten Schritt ausgebaut.")

            st.markdown(f"**Vorname:** {patient.vorname}")
            st.markdown(f"**Nachname:** {patient.nachname}")
            st.markdown(f"**Geburtsdatum:** {formatiere_geburtsdatum(patient.geburtsdatum)}")
            st.markdown(f"**Geschlecht:** {patient.geschlecht}")
            st.markdown(f"**Erstellt am:** {formatiere_erstellt_am(patient.erstellt_am)}")

    linke_spalte, rechte_spalte = st.columns(2)

    with linke_spalte:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurueck zur Patientenuebersicht",
            icon=":material/groups:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )


main()
