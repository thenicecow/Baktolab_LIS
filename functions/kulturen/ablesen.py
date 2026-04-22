"""Fachliche Hilfsfunktionen fuer die Seite ``Kulturen ablesen``."""

from __future__ import annotations

from domaene import Material, Patient
from functions.kulturen.navigation import hole_material_id_fuer_kulturen_ablesen
from persistenz import PatientenRepository


UNTERSTUETZTER_MATERIALTYP_CODE = "urin"
UNTERSTUETZTER_ANALYSE_CODE = "allgemeine_bakteriologie"


def ist_material_fuer_kulturen_ablesen_unterstuetzt(material: Material) -> bool:
    """Prueft, ob ein Material aktuell fuer ``Kulturen ablesen`` unterstuetzt wird."""
    return (
        material.materialtyp_code == UNTERSTUETZTER_MATERIALTYP_CODE
        and material.klinische_frage_code == UNTERSTUETZTER_ANALYSE_CODE
    )


def lade_materialkontext_fuer_kulturen_ablesen() -> tuple[Patient, Material] | None:
    """Laedt Patient und Material fuer die aktuell gesetzte Materialreferenz."""
    material_id = hole_material_id_fuer_kulturen_ablesen()
    if material_id is None:
        return None

    repository = PatientenRepository()
    patienten = repository.lade_alle_patienten()

    for patient in patienten:
        patientenakte = repository.lade_patientenakte_nach_id(patient.id)
        if patientenakte is None:
            continue

        patient_aus_akte, materialien = patientenakte

        for material in materialien:
            if material.id == material_id:
                return patient_aus_akte, material

    return None
