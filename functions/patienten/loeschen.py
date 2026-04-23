"""Fachliche Logik fuer das Loeschen bestehender Patienten."""

from __future__ import annotations

import streamlit as st

from functions.gemeinsam.anzeige_hilfen import baue_technische_fehlernachricht
from persistenz import PatientenRepository


LOESCHEN_BESTAETIGUNG_SCHLUESSEL = "patient_loeschen_bestaetigt"
LOESCHEN_KONTEXT_PATIENT_ID_SCHLUESSEL = "patient_loeschen_kontext_patient_id"
ERFOLGSMELDUNG_SCHLUESSEL = "patient_loeschen_erfolgsmeldung"


def initialisiere_loeschzustand(patient_id: str) -> None:
    """Initialisiert den Bestaetigungszustand fuer den aktuell geoeffneten Patienten."""
    aktueller_kontext = st.session_state.get(LOESCHEN_KONTEXT_PATIENT_ID_SCHLUESSEL)

    if aktueller_kontext != patient_id:
        st.session_state[LOESCHEN_KONTEXT_PATIENT_ID_SCHLUESSEL] = patient_id
        st.session_state[LOESCHEN_BESTAETIGUNG_SCHLUESSEL] = False
        return

    if LOESCHEN_BESTAETIGUNG_SCHLUESSEL not in st.session_state:
        st.session_state[LOESCHEN_BESTAETIGUNG_SCHLUESSEL] = False


def merke_erfolgreiche_loeschung(erfolgsmeldung: str) -> None:
    """Merkt sich eine Erfolgsmeldung fuer die Patientenuebersicht."""
    st.session_state[ERFOLGSMELDUNG_SCHLUESSEL] = erfolgsmeldung


def hole_und_entferne_erfolgsmeldung() -> str | None:
    """Liest eine zwischengespeicherte Erfolgsmeldung zur Patienteloeschung."""
    erfolgsmeldung = st.session_state.pop(ERFOLGSMELDUNG_SCHLUESSEL, None)

    if not isinstance(erfolgsmeldung, str):
        return None

    bereinigt = erfolgsmeldung.strip()
    return bereinigt or None


def bereinige_patientbezogenen_zustand_nach_loeschung() -> None:
    """Bereinigt patientenbezogenen Session-State nach einer erfolgreichen Loeschung."""
    schluessel_zum_entfernen = (
        "patientendetail_aktiv",
        "patientendetail_patient_id",
        "patientendetail_ausgewaehltes_material_id",
        "patientendetail_filter_materialtyp",
        "patientendetail_filter_analyse",
        "patient_bearbeiten_aktiv",
        "patient_bearbeiten_patient_id",
        "material_erfassen_patient_id",
        "patient_bearbeiten_formular_patient_id",
        "patient_bearbeiten_vorname",
        "patient_bearbeiten_nachname",
        "patient_bearbeiten_geburtsdatum",
        "patient_bearbeiten_geburtstag",
        "patient_bearbeiten_geburtsmonat",
        "patient_bearbeiten_geburtsjahr",
        "patient_bearbeiten_geschlecht",
        "patient_bearbeiten_erfolgsmeldung",
        LOESCHEN_BESTAETIGUNG_SCHLUESSEL,
        LOESCHEN_KONTEXT_PATIENT_ID_SCHLUESSEL,
    )

    for schluessel in schluessel_zum_entfernen:
        st.session_state.pop(schluessel, None)


def loesche_patient(patient_id: str) -> str | None:
    """Loescht einen Patienten mitsamt seiner Materialien und Kulturdaten."""
    repository = PatientenRepository()

    try:
        patient = repository.lade_patient_nach_id(patient_id)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der ausgewaehlte Patient konnte nicht geladen werden."
            )
        )
        return None

    if patient is None:
        st.error("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    try:
        geloeschter_patient = repository.loesche_patient_nach_id(patient_id)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der Patient konnte nicht geloescht werden."
            )
        )
        return None

    if geloeschter_patient is None:
        st.error("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    return (
        f"Patient {geloeschter_patient.vorname} "
        f"{geloeschter_patient.nachname} wurde erfolgreich geloescht."
    )
