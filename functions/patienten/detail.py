"""Fachliche Logik fuer die Patientendetailansicht."""

from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import baue_technische_fehlernachricht
from functions.materialien.erfassung import baue_ansatzhinweis
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL = (
    "patientendetail_ausgewaehltes_material_id"
)
MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL = "material_erfassen_patient_id"
MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL = "material_erfassen_erfolgsmeldung"
MATERIAL_ERFASSEN_ANSATZHINWEIS_SCHLUESSEL = "material_erfassen_ansatzhinweis"
PATIENT_BEARBEITEN_ERFOLGSMELDUNG_SCHLUESSEL = "patient_bearbeiten_erfolgsmeldung"
ALLE_FILTER_OPTION = ""
MATERIALTYP_FILTER_SCHLUESSEL = "patientendetail_filter_materialtyp"
ANALYSE_FILTER_SCHLUESSEL = "patientendetail_filter_analyse"


def material_sortierschluessel(material: Material) -> tuple[int, int, int, float]:
    """Erzeugt den Sortierschluessel fuer Materialeintraege."""
    abnahmedatum = material.abnahmedatum if isinstance(material.abnahmedatum, date) else None
    erstellt_am = material.erstellt_am if isinstance(material.erstellt_am, datetime) else None

    return (
        1 if abnahmedatum is not None else 0,
        abnahmedatum.toordinal() if abnahmedatum is not None else -1,
        1 if erstellt_am is not None else 0,
        erstellt_am.timestamp() if erstellt_am is not None else float("-inf"),
    )


def sortiere_materialien(materialien: list[Material]) -> list[Material]:
    """Sortiert Materialien absteigend nach Datum und Erstellzeitpunkt."""
    return sorted(materialien, key=material_sortierschluessel, reverse=True)


def filtere_materialien(
    materialien: list[Material],
    materialtyp_code: str | None,
    analyse_code: str | None,
) -> list[Material]:
    """Filtert Materialien nach Materialtyp und Analyse."""
    gefilterte_materialien: list[Material] = []

    for material in materialien:
        if materialtyp_code and material.materialtyp_code != materialtyp_code:
            continue

        if analyse_code and material.klinische_frage_code != analyse_code:
            continue

        gefilterte_materialien.append(material)

    return gefilterte_materialien


def merke_patient_id_fuer_material_erfassen(patient_id: str) -> None:
    """Merkt sich den Patienten fuer die nachfolgende Materialerfassung."""
    st.session_state[MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL] = patient_id


def merke_material_fuer_ansatzhinweis(material_id: str) -> None:
    """Merkt sich ein Material fuer die erneute Anzeige des Ansatzhinweises."""
    bereinigt = material_id.strip()

    if not bereinigt:
        return

    st.session_state[PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL] = bereinigt


def lade_patientenakte() -> tuple[Patient, list[Material]] | None:
    """Laedt die aktuell ausgewaehlte Patientenakte."""
    patient_id = st.session_state.get(PATIENTENDETAIL_ID_SCHLUESSEL)

    if not isinstance(patient_id, str) or not patient_id.strip():
        st.info("Es wurde noch kein Patient ausgewaehlt.")
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
        st.warning("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    return patientenakte


def hole_und_entferne_erfolgsmeldung() -> str | None:
    """Liest eine Erfolgsmeldung zur Materialerfassung aus dem Session State."""
    erfolgsmeldung = st.session_state.pop(MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL, None)

    if not isinstance(erfolgsmeldung, str):
        return None

    bereinigt = erfolgsmeldung.strip()
    return bereinigt or None


def hole_und_entferne_bearbeitungserfolgsmeldung() -> str | None:
    """Liest eine Erfolgsmeldung zur Patientenbearbeitung aus dem Session State."""
    erfolgsmeldung = st.session_state.pop(PATIENT_BEARBEITEN_ERFOLGSMELDUNG_SCHLUESSEL, None)

    if not isinstance(erfolgsmeldung, str):
        return None

    bereinigt = erfolgsmeldung.strip()
    return bereinigt or None


def hole_und_entferne_ansatzhinweis() -> dict[str, object] | None:
    """Liest einen gespeicherten Ansatzhinweis aus dem Session State."""
    ansatzhinweis = st.session_state.pop(MATERIAL_ERFASSEN_ANSATZHINWEIS_SCHLUESSEL, None)

    if not isinstance(ansatzhinweis, dict):
        return None

    return ansatzhinweis


def hole_ausgewaehltes_material(materialien: list[Material]) -> Material | None:
    """Liefert das aktuell fuer den Ansatzhinweis ausgewaehlte Material."""
    material_id = st.session_state.get(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL)

    if not isinstance(material_id, str):
        return None

    bereinigt = material_id.strip()
    if not bereinigt:
        return None

    for material in materialien:
        if material.id == bereinigt:
            return material

    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)
    return None


def baue_ansatzhinweis_fuer_ausgewaehltes_material(
    materialien: list[Material],
) -> dict[str, object] | None:
    """Erzeugt den Ansatzhinweis fuer das aktuell ausgewaehlte Material."""
    material = hole_ausgewaehltes_material(materialien)

    if material is None:
        return None

    return baue_ansatzhinweis(material)


def initialisiere_filterzustand(
    materialtyp_optionen: list[str],
    analyse_optionen: list[str],
) -> None:
    """Initialisiert gueltige Filterwerte im Session State."""
    materialtyp_wert = st.session_state.get(MATERIALTYP_FILTER_SCHLUESSEL)
    if not isinstance(materialtyp_wert, str) or materialtyp_wert not in materialtyp_optionen:
        st.session_state[MATERIALTYP_FILTER_SCHLUESSEL] = ALLE_FILTER_OPTION

    analyse_wert = st.session_state.get(ANALYSE_FILTER_SCHLUESSEL)
    if not isinstance(analyse_wert, str) or analyse_wert not in analyse_optionen:
        st.session_state[ANALYSE_FILTER_SCHLUESSEL] = ALLE_FILTER_OPTION
