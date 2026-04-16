from __future__ import annotations

from datetime import date
from uuid import uuid4

import streamlit as st

from domaene import Patient
from persistenz import PatientenRepository
from ui.anzeige_hilfen import baue_technische_fehlernachricht, hole_aktuellen_user_id


GESCHLECHTER: tuple[str, ...] = (
    "weiblich",
    "maennlich",
    "divers",
    "unbekannt",
)

MONATE: tuple[tuple[int, str], ...] = (
    (1, "Januar"),
    (2, "Februar"),
    (3, "Maerz"),
    (4, "April"),
    (5, "Mai"),
    (6, "Juni"),
    (7, "Juli"),
    (8, "August"),
    (9, "September"),
    (10, "Oktober"),
    (11, "November"),
    (12, "Dezember"),
)

ERSTES_GEBURTSJAHR = 1900

VORNAME_SCHLUESSEL = "patient_erfassen_vorname"
NACHNAME_SCHLUESSEL = "patient_erfassen_nachname"
GEBURTSDATUM_SCHLUESSEL = "patient_erfassen_geburtsdatum"
GEBURTSTAG_SCHLUESSEL = "patient_erfassen_geburtstag"
GEBURTSMONAT_SCHLUESSEL = "patient_erfassen_geburtsmonat"
GEBURTSJAHR_SCHLUESSEL = "patient_erfassen_geburtsjahr"
GESCHLECHT_SCHLUESSEL = "patient_erfassen_geschlecht"
ERFOLGSMELDUNG_SCHLUESSEL = "patient_erfassen_erfolgsmeldung"


def setze_geburtsdatum_im_formular(geburtsdatum: date) -> None:
    st.session_state[GEBURTSDATUM_SCHLUESSEL] = geburtsdatum
    st.session_state[GEBURTSTAG_SCHLUESSEL] = geburtsdatum.day
    st.session_state[GEBURTSMONAT_SCHLUESSEL] = geburtsdatum.month
    st.session_state[GEBURTSJAHR_SCHLUESSEL] = geburtsdatum.year


def initialisiere_formularzustand() -> None:
    if VORNAME_SCHLUESSEL not in st.session_state:
        st.session_state[VORNAME_SCHLUESSEL] = ""

    if NACHNAME_SCHLUESSEL not in st.session_state:
        st.session_state[NACHNAME_SCHLUESSEL] = ""

    geburtsdatum = st.session_state.get(GEBURTSDATUM_SCHLUESSEL)
    if not isinstance(geburtsdatum, date):
        geburtsdatum = date.today()

    if (
        GEBURTSTAG_SCHLUESSEL not in st.session_state
        or GEBURTSMONAT_SCHLUESSEL not in st.session_state
        or GEBURTSJAHR_SCHLUESSEL not in st.session_state
    ):
        setze_geburtsdatum_im_formular(geburtsdatum)

    if GESCHLECHT_SCHLUESSEL not in st.session_state:
        st.session_state[GESCHLECHT_SCHLUESSEL] = GESCHLECHTER[0]


def leere_formularzustand() -> None:
    st.session_state[VORNAME_SCHLUESSEL] = ""
    st.session_state[NACHNAME_SCHLUESSEL] = ""
    setze_geburtsdatum_im_formular(date.today())
    st.session_state[GESCHLECHT_SCHLUESSEL] = GESCHLECHTER[0]


def hole_geburtsjahre() -> list[int]:
    return list(range(date.today().year, ERSTES_GEBURTSJAHR - 1, -1))


def hole_monatslabel(monat: int) -> str:
    for monatsnummer, label in MONATE:
        if monatsnummer == monat:
            return label

    return str(monat)


def hole_geburtsdatum_aus_formular() -> date | None:
    tag = st.session_state.get(GEBURTSTAG_SCHLUESSEL)
    monat = st.session_state.get(GEBURTSMONAT_SCHLUESSEL)
    jahr = st.session_state.get(GEBURTSJAHR_SCHLUESSEL)

    if not isinstance(tag, int) or not isinstance(monat, int) or not isinstance(jahr, int):
        return None

    try:
        geburtsdatum = date(jahr, monat, tag)
    except ValueError:
        return None

    st.session_state[GEBURTSDATUM_SCHLUESSEL] = geburtsdatum
    return geburtsdatum


def erzeuge_patient_id() -> str:
    return f"patient-{uuid4().hex}"


def speichere_patient() -> str | None:
    vorname = str(st.session_state[VORNAME_SCHLUESSEL]).strip()
    nachname = str(st.session_state[NACHNAME_SCHLUESSEL]).strip()
    geburtsdatum = hole_geburtsdatum_aus_formular()
    geschlecht = str(st.session_state[GESCHECHT_SCHLUESSEL]).strip() if "GESCHECHT_SCHLUESSEL" in globals() else str(st.session_state[GESCHLECHT_SCHLUESSEL]).strip()

    if not vorname or not nachname:
        st.error("Vorname und Nachname muessen ausgefuellt werden.")
        return None

    if geburtsdatum is None:
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
    except Exception:
        st.error(baue_technische_fehlernachricht("Der Patient konnte nicht gespeichert werden."))
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
