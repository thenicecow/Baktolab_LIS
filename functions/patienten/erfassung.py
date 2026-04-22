"""Fachliche Logik fuer die Erfassung neuer Patienten."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import streamlit as st

from domaene import Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    hole_aktuellen_user_id,
)
from persistenz import PatientenRepository


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
RESET_FORMULAR_SCHLUESSEL = "patient_erfassen_reset_formular"


def setze_geburtsdatum_im_formular(geburtsdatum: date) -> None:
    """Schreibt ein Geburtsdatum in die einzelnen Formularfelder."""
    st.session_state[GEBURTSDATUM_SCHLUESSEL] = geburtsdatum
    st.session_state[GEBURTSTAG_SCHLUESSEL] = geburtsdatum.day
    st.session_state[GEBURTSMONAT_SCHLUESSEL] = geburtsdatum.month
    st.session_state[GEBURTSJAHR_SCHLUESSEL] = geburtsdatum.year


def setze_formular_auf_standardwerte() -> None:
    """Setzt das Formular auf seine Standardwerte zurueck."""
    st.session_state[VORNAME_SCHLUESSEL] = ""
    st.session_state[NACHNAME_SCHLUESSEL] = ""
    setze_geburtsdatum_im_formular(date.today())
    st.session_state[GESCHLECHT_SCHLUESSEL] = GESCHLECHTER[0]


def initialisiere_formularzustand() -> None:
    """Initialisiert den benoetigten Session-State fuer das Formular."""
    if st.session_state.pop(RESET_FORMULAR_SCHLUESSEL, False):
        setze_formular_auf_standardwerte()
        return

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


def hole_geburtsjahre() -> list[int]:
    """Liefert die im Formular verfuegbaren Geburtsjahre."""
    return list(range(date.today().year, ERSTES_GEBURTSJAHR - 1, -1))


def hole_monatslabel(monat: int) -> str:
    """Liefert das Anzeige-Label fuer einen Monatswert."""
    for monatsnummer, label in MONATE:
        if monatsnummer == monat:
            return label

    return str(monat)


def hole_geburtsdatum_aus_formular() -> date | None:
    """Liest das Geburtsdatum aus den Session-State-Feldern."""
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
    """Erzeugt eine neue technische Patienten-ID."""
    return f"patient-{uuid4().hex}"


def hole_und_entferne_erfolgsmeldung() -> str | None:
    """Liest eine zwischengespeicherte Erfolgsmeldung aus dem Session State."""
    erfolgsmeldung = st.session_state.pop(ERFOLGSMELDUNG_SCHLUESSEL, None)

    if not isinstance(erfolgsmeldung, str):
        return None

    bereinigt = erfolgsmeldung.strip()
    return bereinigt or None


def merke_erfolgreiche_speicherung(erfolgsmeldung: str) -> None:
    """Merkt sich eine Erfolgsmeldung und markiert das Formular zum Reset."""
    st.session_state[ERFOLGSMELDUNG_SCHLUESSEL] = erfolgsmeldung
    st.session_state[RESET_FORMULAR_SCHLUESSEL] = True


def speichere_patient() -> str | None:
    """Validiert die Eingaben und speichert einen neuen Patienten."""
    vorname = str(st.session_state[VORNAME_SCHLUESSEL]).strip()
    nachname = str(st.session_state[NACHNAME_SCHLUESSEL]).strip()
    geburtsdatum = hole_geburtsdatum_aus_formular()
    geschlecht = str(st.session_state[GESCHLECHT_SCHLUESSEL]).strip()

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

    return (
        f"Patient {patient.vorname} {patient.nachname} wurde erfolgreich gespeichert. "
        f"ID: {patient.id}"
    )
