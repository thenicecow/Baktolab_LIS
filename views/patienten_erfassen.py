from __future__ import annotations

from datetime import date
from uuid import uuid4

import streamlit as st

from domaene import Patient
from persistenz import PatientenRepository


GESCHLECHTER: tuple[str, ...] = (
    "weiblich",
    "maennlich",
    "divers",
    "unbekannt",
)

VORNAME_SCHLUESSEL = "patient_erfassen_vorname"
NACHNAME_SCHLUESSEL = "patient_erfassen_nachname"
GEBURTSDATUM_SCHLUESSEL = "patient_erfassen_geburtsdatum"
GESCHLECHT_SCHLUESSEL = "patient_erfassen_geschlecht"
ERFOLGSMELDUNG_SCHLUESSEL = "patient_erfassen_erfolgsmeldung"


def initialisiere_formularzustand() -> None:
    if VORNAME_SCHLUESSEL not in st.session_state:
        st.session_state[VORNAME_SCHLUESSEL] = ""

    if NACHNAME_SCHLUESSEL not in st.session_state:
        st.session_state[NACHNAME_SCHLUESSEL] = ""

    if GEBURTSDATUM_SCHLUESSEL not in st.session_state:
        st.session_state[GEBURTSDATUM_SCHLUESSEL] = date.today()

    if GESCHLECHT_SCHLUESSEL not in st.session_state:
        st.session_state[GESCHLECHT_SCHLUESSEL] = GESCHLECHTER[0]


def leere_formularzustand() -> None:
    st.session_state[VORNAME_SCHLUESSEL] = ""
    st.session_state[NACHNAME_SCHLUESSEL] = ""
    st.session_state[GEBURTSDATUM_SCHLUESSEL] = date.today()
    st.session_state[GESCHLECHT_SCHLUESSEL] = GESCHLECHTER[0]


def hole_aktuellen_user_id() -> str:
    user_id = st.session_state.get("username")

    if not isinstance(user_id, str):
        return ""

    return user_id.strip()


def erzeuge_patient_id() -> str:
    return f"patient-{uuid4().hex}"


def speichere_patient() -> str | None:
    vorname = str(st.session_state[VORNAME_SCHLUESSEL]).strip()
    nachname = str(st.session_state[NACHNAME_SCHLUESSEL]).strip()
    geburtsdatum = st.session_state[GEBURTSDATUM_SCHLUESSEL]
    geschlecht = str(st.session_state[GESCHLECHT_SCHLUESSEL]).strip()

    if not vorname or not nachname:
        st.error("Vorname und Nachname muessen ausgefuellt werden.")
        return None

    if not isinstance(geburtsdatum, date):
        st.error("Bitte ein gueltiges Geburtsdatum erfassen.")
        return None

    user_id = hole_aktuellen_user_id()
    if not user_id:
        st.error("Es konnte kein angemeldeter Benutzer ermittelt werden.")
        return None

    patient = Patient(
        id=erzeuge_patient_id(),
        vorname=vorname,
        nachname=nachname,
        geburtsdatum=geburtsdatum,
        geschlecht=geschlecht,
        erstellt_von_user_id=user_id,
    )

    repository = PatientenRepository()

    try:
        repository.speichere_neuen_patienten(patient)
    except ValueError as exc:
        st.error(str(exc))
        return None
    except Exception as exc:
        st.error(f"Der Patient konnte nicht gespeichert werden: {exc}")
        return None

    leere_formularzustand()

    return (
        f"Patient {patient.vorname} {patient.nachname} wurde erfolgreich gespeichert. "
        f"ID: {patient.id}"
    )


def zeige_erfolgsmeldung() -> None:
    erfolgsmeldung = st.session_state.pop(ERFOLGSMELDUNG_SCHLUESSEL, None)

    if erfolgsmeldung:
        st.success(erfolgsmeldung)


def main() -> None:
    initialisiere_formularzustand()

    st.title("Patient erfassen")
    st.write("Hier kannst du einen neuen Patienten erfassen.")
    st.info("Die Patienten-ID wird automatisch erzeugt.")

    zeige_erfolgsmeldung()

    with st.form("patient_erfassen_formular"):
        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            st.text_input("Vorname", key=VORNAME_SCHLUESSEL)
            st.date_input(
                "Geburtsdatum",
                key=GEBURTSDATUM_SCHLUESSEL,
                max_value=date.today(),
                format="DD.MM.YYYY",
            )

        with rechte_spalte:
            st.text_input("Nachname", key=NACHNAME_SCHLUESSEL)
            st.selectbox("Geschlecht", GESCHLECHTER, key=GESCHLECHT_SCHLUESSEL)

        speichern = st.form_submit_button(
            "Patient speichern",
            type="primary",
            use_container_width=True,
        )

    if speichern:
        erfolgsmeldung = speichere_patient()
        if erfolgsmeldung is not None:
            st.session_state[ERFOLGSMELDUNG_SCHLUESSEL] = erfolgsmeldung
            st.rerun()

    st.page_link(
        "views/dashboard.py",
        label="Zurueck zum Dashboard",
        icon=":material/dashboard:",
    )


main()
