"""Fachliche Logik fuer die Patientenuebersicht."""

from __future__ import annotations

import streamlit as st

from domaene import Patient
from functions.gemeinsam.anzeige_hilfen import baue_technische_fehlernachricht
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"


def sortiere_patienten(patienten: list[Patient]) -> list[Patient]:
    """Sortiert Patienten absteigend nach Erstellzeitpunkt."""
    return sorted(
        patienten,
        key=lambda patient: (
            patient.erstellt_am is not None,
            patient.erstellt_am.timestamp() if patient.erstellt_am is not None else float("-inf"),
        ),
        reverse=True,
    )


def filtere_patienten(patienten: list[Patient], suchtext: str) -> list[Patient]:
    """Filtert Patienten nach Vor- oder Nachname."""
    suchtext_bereinigt = suchtext.strip().casefold()

    if not suchtext_bereinigt:
        return patienten

    return [
        patient
        for patient in patienten
        if suchtext_bereinigt in patient.vorname.casefold()
        or suchtext_bereinigt in patient.nachname.casefold()
    ]


def merke_patient_fuer_detailansicht(patient_id: str) -> None:
    """Merkt sich die ausgewaehlte Patienten-ID fuer die Detailansicht."""
    st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = patient_id


def lade_patienten() -> list[Patient] | None:
    """Laedt alle Patienten aus dem Repository."""
    repository = PatientenRepository()

    try:
        patienten = repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None

    return sortiere_patienten(patienten)
