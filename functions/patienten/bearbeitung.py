"""Fachliche Logik fuer die Bearbeitung bestehender Patienten."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import baue_technische_fehlernachricht
from functions.patienten.navigation import hole_patienten_id_fuer_bearbeitung
from persistenz import PatientenRepository


STANDARD_GESCHLECHTER: tuple[str, ...] = (
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

FORMULAR_PATIENT_ID_SCHLUESSEL = "patient_bearbeiten_formular_patient_id"
VORNAME_SCHLUESSEL = "patient_bearbeiten_vorname"
NACHNAME_SCHLUESSEL = "patient_bearbeiten_nachname"
GEBURTSDATUM_SCHLUESSEL = "patient_bearbeiten_geburtsdatum"
GEBURTSTAG_SCHLUESSEL = "patient_bearbeiten_geburtstag"
GEBURTSMONAT_SCHLUESSEL = "patient_bearbeiten_geburtsmonat"
GEBURTSJAHR_SCHLUESSEL = "patient_bearbeiten_geburtsjahr"
GESCHLECHT_SCHLUESSEL = "patient_bearbeiten_geschlecht"
ERFOLGSMELDUNG_SCHLUESSEL = "patient_bearbeiten_erfolgsmeldung"


def hole_geschlechter_optionen(aktuelles_geschlecht: str | None) -> tuple[str, ...]:
    """Liefert die verfuegbaren Geschlechteroptionen fuer das Formular."""
    if not isinstance(aktuelles_geschlecht, str):
        return STANDARD_GESCHLECHTER

    bereinigt = aktuelles_geschlecht.strip()
    if not bereinigt or bereinigt in STANDARD_GESCHLECHTER:
        return STANDARD_GESCHLECHTER

    return (bereinigt, *STANDARD_GESCHLECHTER)


def setze_geburtsdatum_im_formular(geburtsdatum: date) -> None:
    """Schreibt ein Geburtsdatum in die einzelnen Formularfelder."""
    st.session_state[GEBURTSDATUM_SCHLUESSEL] = geburtsdatum
    st.session_state[GEBURTSTAG_SCHLUESSEL] = geburtsdatum.day
    st.session_state[GEBURTSMONAT_SCHLUESSEL] = geburtsdatum.month
    st.session_state[GEBURTSJAHR_SCHLUESSEL] = geburtsdatum.year


def setze_formular_aus_patient(
    patient: Patient,
    geschlecht_optionen: Sequence[str],
) -> None:
    """Befuellt das Bearbeitungsformular mit den Daten des Patienten."""
    st.session_state[FORMULAR_PATIENT_ID_SCHLUESSEL] = patient.id
    st.session_state[VORNAME_SCHLUESSEL] = patient.vorname
    st.session_state[NACHNAME_SCHLUESSEL] = patient.nachname
    setze_geburtsdatum_im_formular(patient.geburtsdatum)

    if patient.geschlecht in geschlecht_optionen:
        st.session_state[GESCHLECHT_SCHLUESSEL] = patient.geschlecht
    else:
        st.session_state[GESCHLECHT_SCHLUESSEL] = geschlecht_optionen[0]


def initialisiere_formularzustand(
    patient: Patient,
    geschlecht_optionen: Sequence[str],
) -> None:
    """Initialisiert den Session State fuer das Bearbeitungsformular."""
    formular_patient_id = st.session_state.get(FORMULAR_PATIENT_ID_SCHLUESSEL)

    if formular_patient_id != patient.id:
        setze_formular_aus_patient(patient, geschlecht_optionen)
        return

    if VORNAME_SCHLUESSEL not in st.session_state:
        st.session_state[VORNAME_SCHLUESSEL] = patient.vorname

    if NACHNAME_SCHLUESSEL not in st.session_state:
        st.session_state[NACHNAME_SCHLUESSEL] = patient.nachname

    geburtsdatum = st.session_state.get(GEBURTSDATUM_SCHLUESSEL)
    if not isinstance(geburtsdatum, date):
        geburtsdatum = patient.geburtsdatum

    if (
        GEBURTSTAG_SCHLUESSEL not in st.session_state
        or GEBURTSMONAT_SCHLUESSEL not in st.session_state
        or GEBURTSJAHR_SCHLUESSEL not in st.session_state
    ):
        setze_geburtsdatum_im_formular(geburtsdatum)

    geschlecht = st.session_state.get(GESCHLECHT_SCHLUESSEL)
    if not isinstance(geschlecht, str) or geschlecht not in geschlecht_optionen:
        st.session_state[GESCHLECHT_SCHLUESSEL] = (
            patient.geschlecht
            if patient.geschlecht in geschlecht_optionen
            else geschlecht_optionen[0]
        )


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


def lade_patientenakte_fuer_bearbeitung() -> tuple[Patient, list[Material]] | None:
    """Laedt die aktuell ausgewaehlte Patientenakte fuer die Bearbeitung."""
    patient_id = hole_patienten_id_fuer_bearbeitung()

    if patient_id is None:
        st.error("Es wurde kein Patient fuer die Bearbeitung ausgewaehlt.")
        return None

    repository = PatientenRepository()

    try:
        patientenakte = repository.lade_patientenakte_nach_id(patient_id)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der ausgewaehlte Patient konnte nicht geladen werden."
            )
        )
        return None

    if patientenakte is None:
        st.error("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    return patientenakte


def merke_erfolgreiche_bearbeitung(erfolgsmeldung: str) -> None:
    """Merkt sich eine Erfolgsmeldung fuer die Rueckkehr zur Detailansicht."""
    st.session_state[ERFOLGSMELDUNG_SCHLUESSEL] = erfolgsmeldung


def speichere_patientaenderungen(
    patient: Patient,
    materialien: Sequence[Material],
) -> str | None:
    """Validiert und speichert geaenderte Stammdaten eines Patienten."""
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

    if not geschlecht:
        st.error("Bitte ein Geschlecht auswaehlen.")
        return None

    aktualisierter_patient = Patient(
        id=patient.id,
        vorname=vorname,
        nachname=nachname,
        geburtsdatum=geburtsdatum,
        geschlecht=geschlecht,
        erstellt_am=patient.erstellt_am,
        erstellt_von_user_id=patient.erstellt_von_user_id,
    )

    repository = PatientenRepository()

    try:
        repository.speichere_patient_mit_materialien(aktualisierter_patient, materialien)
    except ValueError as exc:
        st.error(str(exc))
        return None
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Die Aenderungen am Patienten konnten nicht gespeichert werden."
            )
        )
        return None

    return (
        f"Patient {aktualisierter_patient.vorname} "
        f"{aktualisierter_patient.nachname} wurde erfolgreich aktualisiert."
    )
