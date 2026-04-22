"""Fachliche Hilfsfunktionen fuer die Seite ``Kulturen ablesen``."""

from __future__ import annotations

from domaene import Kulturdaten, KulturKeim, Material, Patient
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


def baue_leere_kulturdaten() -> Kulturdaten:
    """Liefert einen sinnvollen leeren Standardzustand fuer Kulturdaten."""
    return Kulturdaten(
        wachstum=None,
        keime=[],
        beurteilung=None,
    )


def hole_kulturdaten_oder_standard(material: Material) -> Kulturdaten:
    """Liefert vorhandene Kulturdaten oder einen leeren Standardzustand."""
    kulturdaten = material.kulturdaten

    if not isinstance(kulturdaten, Kulturdaten):
        return baue_leere_kulturdaten()

    return Kulturdaten(
        wachstum=kulturdaten.wachstum,
        keime=[
            KulturKeim(
                keim_id=keim.keim_id,
                keimzahl_code=keim.keimzahl_code,
                rolle=keim.rolle,
                keimgruppe=keim.keimgruppe,
            )
            for keim in kulturdaten.keime
        ],
        beurteilung=kulturdaten.beurteilung,
    )


def baue_kulturdaten_aus_formularwerten(
    wachstum: bool,
    keime: list[dict[str, str]],
    beurteilung: str | None = None,
) -> Kulturdaten:
    """Erzeugt Kulturdaten aus den aktuellen Formularwerten."""
    if not wachstum:
        return Kulturdaten(
            wachstum=False,
            keime=[],
            beurteilung=beurteilung,
        )

    keimeintraege = [
        KulturKeim(
            keim_id=eintrag["keim_id"].strip(),
            keimzahl_code=eintrag["keimzahl_code"].strip(),
            rolle=eintrag["rolle"].strip(),
            keimgruppe=eintrag["keimgruppe"].strip(),
        )
        for eintrag in keime
        if eintrag["keim_id"].strip()
    ]

    return Kulturdaten(
        wachstum=True,
        keime=keimeintraege,
        beurteilung=beurteilung,
    )


def lade_materialkontext_fuer_kulturen_ablesen() -> tuple[Patient, Material] | None:
    """Laedt Patient und Material fuer die aktuell gesetzte Materialreferenz."""
    material_id = hole_material_id_fuer_kulturen_ablesen()
    if material_id is None:
        return None

    repository = PatientenRepository()
    materialkontext = repository.lade_materialkontext_nach_id(material_id)
    if materialkontext is None:
        return None

    patient, material, _materialien = materialkontext
    return patient, material


def speichere_kulturdaten_fuer_material(
    material_id: str,
    kulturdaten: Kulturdaten,
) -> tuple[Patient, Material] | None:
    """Speichert Kulturdaten fuer ein bestimmtes Material."""
    repository = PatientenRepository()
    return repository.speichere_kulturdaten_fuer_material(material_id, kulturdaten)
