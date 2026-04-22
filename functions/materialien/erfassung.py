"""Fachliche Logik fuer die Erfassung neuer Materialien."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import streamlit as st

from domaene import (
    Material,
    Patient,
    ist_gueltiger_analyse_code,
    ist_gueltiger_materialtyp_code,
)
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    hole_aktuellen_user_id,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL = (
    "patientendetail_ausgewaehltes_material_id"
)
MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL = "material_erfassen_patient_id"
MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL = "material_erfassen_erfolgsmeldung"
MATERIAL_ERFASSEN_ANSATZHINWEIS_SCHLUESSEL = "material_erfassen_ansatzhinweis"

ANSATZHINWEISE_NACH_KOMBINATION: dict[tuple[str, str], tuple[tuple[str, str], ...]] = {
    ("urin", "allgemeine_bakteriologie"): (
        ("SBA", "37 Grad C mit CO2"),
        ("CNA", "37 Grad C mit CO2"),
        ("CPS", "35 Grad C Luft"),
    ),
    ("blutkultur", "allgemeine_bakteriologie"): (
        ("BACTEC", "Inkubation im BACTEC"),
    ),
    ("vaginalabstrich", "allgemeine_bakteriologie"): (
        ("SBA", "37 Grad C mit CO2"),
        ("CNA", "37 Grad C mit CO2"),
        ("CAND", "35 Grad C Luft"),
        ("GARD", "37 Grad C anaerob"),
    ),
    ("vaginalabstrich", "gardnerella_vaginalis"): (
        ("SBA", "37 Grad C mit CO2"),
        ("GARD", "37 Grad C anaerob"),
    ),
    ("vaginalabstrich", "hefen"): (
        ("SBA", "37 Grad C mit CO2"),
        ("CAND", "35 Grad C Luft"),
    ),
}


def hole_vorbelegte_patient_id() -> str | None:
    """Liest eine vorbelegte Patienten-ID aus dem Session State."""
    patient_id = st.session_state.get(MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL)

    if not isinstance(patient_id, str):
        return None

    bereinigt = patient_id.strip()
    return bereinigt or None


def erzeuge_material_id() -> str:
    """Erzeugt eine neue technische Material-ID."""
    return f"material-{uuid4().hex}"


def lade_patienten(repository: PatientenRepository) -> list[Patient] | None:
    """Laedt alle Patienten fuer die Materialerfassung."""
    try:
        return repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None


def speichere_material(
    repository: PatientenRepository,
    patient_id: str,
    materialtyp_code: str,
    analyse_code: str,
    abnahmedatum: date,
    eingangsdatum: date,
) -> tuple[Patient, Material] | None:
    """Validiert und speichert ein neues Material fuer einen Patienten."""
    user_id = hole_aktuellen_user_id()
    if not user_id:
        st.error("Es konnte kein angemeldeter Benutzer ermittelt werden.")
        return None

    materialtyp_code_bereinigt = materialtyp_code.strip()
    if not ist_gueltiger_materialtyp_code(materialtyp_code_bereinigt):
        st.error("Bitte waehle einen gueltigen Materialtyp aus.")
        return None

    analyse_code_bereinigt = analyse_code.strip()
    if not ist_gueltiger_analyse_code(analyse_code_bereinigt):
        st.error("Bitte waehle eine gueltige Analyse aus.")
        return None

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

    patient, materialien = patientenakte

    neues_material = Material(
        id=erzeuge_material_id(),
        patient_id=patient.id,
        materialtyp_code=materialtyp_code_bereinigt,
        klinische_frage_code=analyse_code_bereinigt,
        abnahmedatum=abnahmedatum,
        eingangsdatum=eingangsdatum,
        erstellt_von_user_id=user_id,
    )

    neue_materialien = list(materialien)
    neue_materialien.append(neues_material)

    try:
        repository.speichere_patient_mit_materialien(patient, neue_materialien)
    except ValueError as exc:
        st.error(str(exc))
        return None
    except Exception:
        st.error(baue_technische_fehlernachricht("Das Material konnte nicht gespeichert werden."))
        return None

    return patient, neues_material


def hole_ansatzhinweis_zeilen(
    materialtyp_code: str,
    analyse_code: str,
) -> list[dict[str, str]]:
    """Liefert die Tabellenzeilen fuer den material- und analyseabhaengigen Hinweis."""
    kombination = (materialtyp_code.strip(), analyse_code.strip())
    rohdaten = ANSATZHINWEISE_NACH_KOMBINATION.get(kombination, ())

    return [
        {"Ansatz": ansatz, "Inkubation": inkubation}
        for ansatz, inkubation in rohdaten
    ]


def baue_ansatzhinweis(material: Material) -> dict[str, object]:
    """Erzeugt die Anzeigedaten fuer den Ansatzhinweis eines Materials."""
    material_label = loese_materialtyp_label_auf(material.materialtyp_code)
    analyse_label = loese_analyse_label_auf(material.klinische_frage_code)
    zeilen = hole_ansatzhinweis_zeilen(
        material.materialtyp_code,
        material.klinische_frage_code,
    )

    ansatzhinweis: dict[str, object] = {
        "titel": f"Ansatzhinweis fuer {material_label} und {analyse_label}",
        "zeilen": zeilen,
    }

    if not zeilen:
        ansatzhinweis["hinweistext"] = "Fuer diese Kombination ist kein Ansatzhinweis definiert."

    return ansatzhinweis


def merke_erfolgreiche_materialspeicherung(patient: Patient, material: Material) -> None:
    """Merkt sich Zielnavigation, Erfolgsmeldung und Ansatzhinweis nach dem Speichern."""
    st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = patient.id
    st.session_state[MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL] = (
        f"Material {loese_materialtyp_label_auf(material.materialtyp_code)} "
        f"wurde erfolgreich gespeichert."
    )
    st.session_state[MATERIAL_ERFASSEN_ANSATZHINWEIS_SCHLUESSEL] = (
        baue_ansatzhinweis(material)
    )
    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)
    st.session_state.pop(MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL, None)

