"""Hilfen fuer JSON-Serialisierung und defensives Laden von Patientendaten."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from domaene import (
    Kulturdaten,
    KulturKeim,
    Material,
    Patient,
    ist_gueltiger_analyse_code,
    ist_gueltiger_keimzahl_code,
    normalisiere_materialtyp_code,
)
from utils.data_handler import DataHandler


logger = logging.getLogger(__name__)


def lade_json_objekt(
    data_handler: DataHandler,
    relativer_pfad: str,
) -> dict[str, Any] | None:
    """Laedt ein JSON-Objekt und gibt bei Problemen ``None`` zurueck."""
    try:
        if not data_handler.exists(relativer_pfad):
            return None

        daten = data_handler.load(relativer_pfad)
    except (FileNotFoundError, OSError, TypeError, ValueError) as exc:
        logger.warning("JSON-Datei konnte nicht geladen werden (%s): %s", relativer_pfad, exc)
        return None

    if daten is None:
        logger.warning("JSON-Datei ist leer (%s).", relativer_pfad)
        return None

    if not isinstance(daten, dict):
        logger.warning("JSON-Datei enthaelt kein gueltiges Objekt (%s).", relativer_pfad)
        return None

    return daten


def speichere_json_objekt(
    data_handler: DataHandler,
    relativer_pfad: str,
    daten: Mapping[str, Any],
) -> None:
    """Speichert ein Mapping als JSON-Objekt."""
    data_handler.save(relativer_pfad, dict(daten))


def patient_als_dict(patient: Patient) -> dict[str, Any]:
    """Serialisiert einen Patienten in JSON-taugliche Daten."""
    return {
        "id": patient.id.strip(),
        "vorname": patient.vorname.strip(),
        "nachname": patient.nachname.strip(),
        "geburtsdatum": patient.geburtsdatum.isoformat(),
        "geschlecht": patient.geschlecht.strip(),
        "erstellt_am": zeitpunkt_als_iso(patient.erstellt_am),
        "erstellt_von_user_id": optionaler_text(patient.erstellt_von_user_id),
    }


def patient_aus_dict(daten: Mapping[str, Any]) -> Patient:
    """Deserialisiert einen Patienten aus Mapping-Daten."""
    return Patient(
        id=lese_textpflichtfeld(daten, "id"),
        vorname=lese_textpflichtfeld(daten, "vorname"),
        nachname=lese_textpflichtfeld(daten, "nachname"),
        geburtsdatum=lese_datumpflichtfeld(daten, "geburtsdatum"),
        geschlecht=lese_textfeld_mit_standard(daten, "geschlecht", "unbekannt"),
        erstellt_am=lese_optional_zeitpunkt(daten, "erstellt_am"),
        erstellt_von_user_id=lese_optional_textfeld(daten, "erstellt_von_user_id"),
    )


def material_als_dict(material: Material) -> dict[str, Any]:
    """Serialisiert ein Material in JSON-taugliche Daten."""
    materialtyp_code_roh = material.materialtyp_code.strip()
    materialtyp_code = normalisiere_materialtyp_code(materialtyp_code_roh)

    if materialtyp_code is None:
        materialtyp_code = materialtyp_code_roh

    analyse_code = material.klinische_frage_code.strip()

    if not ist_gueltiger_analyse_code(analyse_code):
        raise ValueError(
            "Feld 'klinische_frage_code' enthaelt eine unzulaessige Analyse. "
            "Erlaubt sind nur: allgemeine_bakteriologie, hefen, gardnerella_vaginalis."
        )

    return {
        "id": material.id.strip(),
        "patient_id": material.patient_id.strip(),
        "materialtyp_code": materialtyp_code,
        "analyse_code": analyse_code,
        "abnahmedatum": material.abnahmedatum.isoformat(),
        "eingangsdatum": material.eingangsdatum.isoformat(),
        "erstellt_am": zeitpunkt_als_iso(material.erstellt_am),
        "erstellt_von_user_id": optionaler_text(material.erstellt_von_user_id),
        "kulturdaten": kulturdaten_als_dict(material.kulturdaten),
    }


def material_aus_dict(daten: Mapping[str, Any]) -> Material:
    """Deserialisiert ein Material aus Mapping-Daten."""
    materialtyp_code_roh = lese_textpflichtfeld(daten, "materialtyp_code")
    materialtyp_code = normalisiere_materialtyp_code(materialtyp_code_roh)

    if materialtyp_code is None:
        materialtyp_code = materialtyp_code_roh.strip()

    analyse_code_roh = daten.get("analyse_code")
    if analyse_code_roh is None:
        analyse_code_roh = daten.get("klinische_frage_code")

    if not isinstance(analyse_code_roh, str):
        raise ValueError(
            "Feld 'analyse_code' oder 'klinische_frage_code' fehlt oder ist kein Text."
        )

    analyse_code = analyse_code_roh.strip()
    if not analyse_code:
        raise ValueError("Feld 'analyse_code' oder 'klinische_frage_code' darf nicht leer sein.")

    return Material(
        id=lese_textpflichtfeld(daten, "id"),
        patient_id=lese_textpflichtfeld(daten, "patient_id"),
        materialtyp_code=materialtyp_code,
        klinische_frage_code=analyse_code,
        abnahmedatum=lese_datumpflichtfeld_mit_fallback(
            daten,
            schluessel="abnahmedatum",
            fallback_schluessel="eingangsdatum",
        ),
        eingangsdatum=lese_datumpflichtfeld_mit_fallback(
            daten,
            schluessel="eingangsdatum",
            fallback_schluessel="abnahmedatum",
        ),
        erstellt_am=lese_optional_zeitpunkt(daten, "erstellt_am"),
        erstellt_von_user_id=lese_optional_textfeld(daten, "erstellt_von_user_id"),
        kulturdaten=kulturdaten_aus_dict(daten.get("kulturdaten")),
    )


def kulturdaten_als_dict(kulturdaten: Kulturdaten) -> dict[str, Any]:
    """Serialisiert vorbereitete Kulturdaten in JSON-taugliche Daten."""
    return {
        "wachstum": kulturdaten.wachstum,
        "keime": [kulturkeim_als_dict(keim) for keim in kulturdaten.keime],
        "beurteilung": optionaler_text(kulturdaten.beurteilung),
    }


def kulturdaten_aus_dict(daten: object) -> Kulturdaten:
    """Deserialisiert Kulturdaten defensiv und nutzt einen leeren Standardzustand."""
    if daten is None:
        return Kulturdaten()

    if not isinstance(daten, Mapping):
        logger.warning("Feld 'kulturdaten' ist ungueltig und wird leer initialisiert.")
        return Kulturdaten()

    keime_rohdaten = daten.get("keime")

    if keime_rohdaten is None:
        keime_rohdaten = []
    elif not isinstance(keime_rohdaten, list):
        logger.warning("Feld 'kulturdaten.keime' ist ungueltig und wird leer behandelt.")
        keime_rohdaten = []

    keime: list[KulturKeim] = []

    for index, eintrag in enumerate(keime_rohdaten, start=1):
        if not isinstance(eintrag, Mapping):
            logger.warning(
                "Kulturdaten-Eintrag %s ist ungueltig und wird uebersprungen.",
                index,
            )
            continue

        try:
            keime.append(kulturkeim_aus_dict(eintrag))
        except ValueError as exc:
            logger.warning("Kulturdaten-Eintrag %s wird uebersprungen: %s", index, exc)

    return Kulturdaten(
        wachstum=lese_optional_boolfeld(daten, "wachstum"),
        keime=keime,
        beurteilung=lese_optional_textfeld(daten, "beurteilung"),
    )


def kulturkeim_als_dict(kulturkeim: KulturKeim) -> dict[str, Any]:
    """Serialisiert einen einzelnen Keimeintrag in JSON-taugliche Daten."""
    keimzahl_code = kulturkeim.keimzahl_code.strip()

    if not ist_gueltiger_keimzahl_code(keimzahl_code):
        raise ValueError(
            "Feld 'keimzahl_code' enthaelt einen unzulaessigen Wert. "
            "Erlaubt sind nur: k4, p4, p5, g5."
        )

    return {
        "keim_id": kulturkeim.keim_id.strip(),
        "keimzahl_code": keimzahl_code,
        "rolle": kulturkeim.rolle.strip(),
        "keimgruppe": kulturkeim.keimgruppe.strip(),
    }


def kulturkeim_aus_dict(daten: Mapping[str, Any]) -> KulturKeim:
    """Deserialisiert einen einzelnen Keimeintrag aus Mapping-Daten."""
    keimzahl_code = lese_textpflichtfeld(daten, "keimzahl_code")

    if not ist_gueltiger_keimzahl_code(keimzahl_code):
        raise ValueError(
            "Feld 'keimzahl_code' enthaelt einen unzulaessigen Wert. "
            "Erlaubt sind nur: k4, p4, p5, g5."
        )

    return KulturKeim(
        keim_id=lese_textpflichtfeld(daten, "keim_id"),
        keimzahl_code=keimzahl_code,
        rolle=lese_textpflichtfeld(daten, "rolle"),
        keimgruppe=lese_textpflichtfeld(daten, "keimgruppe"),
    )


def patient_mit_materialien_als_dict(
    patient: Patient,
    materialien: Sequence[Material],
) -> dict[str, Any]:
    """Serialisiert einen Patienten mit seiner Materialliste fuer die Zieldatei."""
    patientendaten = patient_als_dict(patient)
    patientendaten["materialien"] = materialien_als_listendaten(materialien)
    return patientendaten


def patientendaten_als_dict(
    patientenakten: Sequence[tuple[Patient, Sequence[Material]]],
) -> dict[str, Any]:
    """Serialisiert alle Patientenakten in das zentrale JSON-Format."""
    return {
        "patienten": [
            patient_mit_materialien_als_dict(patient, materialien)
            for patient, materialien in patientenakten
        ]
    }


def patientenakte_als_dict(
    patient: Patient,
    materialien: Sequence[Material],
) -> dict[str, Any]:
    """Serialisiert eine einzelne Patientenakte im bisherigen Dateiformat."""
    return {
        "patient": patient_als_dict(patient),
        "materialien": materialien_als_listendaten(materialien),
    }


def materialien_als_listendaten(materialien: Sequence[Material]) -> list[dict[str, Any]]:
    """Serialisiert mehrere Materialien in eine JSON-Liste."""
    listendaten: list[dict[str, Any]] = []

    for index, material in enumerate(materialien, start=1):
        try:
            listendaten.append(material_als_dict(material))
        except ValueError as exc:
            raise ValueError(f"Materialeintrag {index} ist ungueltig: {exc}") from exc

    return listendaten


def patient_mit_materialien_aus_dict(
    daten: Mapping[str, Any],
) -> tuple[Patient, list[Material]]:
    """Liest einen Patienten mit Materialliste aus einem Eintrag der Zieldatei."""
    patient = patient_aus_dict(daten)
    materialien = _lese_materialien_aus_rohdaten(patient, daten.get("materialien", []))
    return patient, materialien


def patientendaten_aus_dict(
    daten: Mapping[str, Any],
) -> list[tuple[Patient, list[Material]]]:
    """Liest alle Patientenakten aus dem zentralen JSON-Format."""
    if "patienten" not in daten:
        raise ValueError("Feld 'patienten' fehlt.")

    patienten_rohdaten = daten.get("patienten")

    if patienten_rohdaten is None:
        patienten_rohdaten = []
    elif not isinstance(patienten_rohdaten, list):
        raise ValueError("Feld 'patienten' ist ungueltig.")

    patientenakten: list[tuple[Patient, list[Material]]] = []

    for index, eintrag in enumerate(patienten_rohdaten, start=1):
        if not isinstance(eintrag, Mapping):
            logger.warning("Patienteneintrag %s ist ungueltig und wird uebersprungen.", index)
            continue

        try:
            patientenakten.append(patient_mit_materialien_aus_dict(eintrag))
        except ValueError as exc:
            logger.warning("Patienteneintrag %s wird uebersprungen: %s", index, exc)

    return patientenakten


def patientenakte_aus_dict(
    daten: Mapping[str, Any],
) -> tuple[Patient, list[Material]]:
    """Liest eine einzelne Patientenakte aus dem bisherigen Dateiformat."""
    patient_rohdaten = lese_dict(daten, "patient")
    patient = patient_aus_dict(patient_rohdaten)
    materialien = _lese_materialien_aus_rohdaten(patient, daten.get("materialien", []))
    return patient, materialien


def _lese_materialien_aus_rohdaten(
    patient: Patient,
    materialien_rohdaten: object,
) -> list[Material]:
    """Liest Materialrohdaten defensiv fuer einen bestimmten Patienten."""
    if materialien_rohdaten is None:
        materialien_rohdaten = []
    elif not isinstance(materialien_rohdaten, list):
        logger.warning("Feld 'materialien' ist ungueltig und wird als leer behandelt.")
        materialien_rohdaten = []

    materialien: list[Material] = []

    for index, eintrag in enumerate(materialien_rohdaten, start=1):
        if not isinstance(eintrag, Mapping):
            logger.warning("Materialeintrag %s ist ungueltig und wird uebersprungen.", index)
            continue

        try:
            material = material_aus_dict(eintrag)
        except ValueError as exc:
            logger.warning("Materialeintrag %s wird uebersprungen: %s", index, exc)
            continue

        if material.patient_id != patient.id:
            logger.warning(
                "Materialeintrag %s verweist auf eine andere Patienten-ID und wird uebersprungen.",
                index,
            )
            continue

        materialien.append(material)

    return materialien


def lese_dict(daten: Mapping[str, Any], schluessel: str) -> Mapping[str, Any]:
    """Liest ein Pflichtfeld als Mapping."""
    wert = daten.get(schluessel)

    if not isinstance(wert, Mapping):
        raise ValueError(f"Feld '{schluessel}' fehlt oder ist ungueltig.")

    return wert


def lese_textpflichtfeld(daten: Mapping[str, Any], schluessel: str) -> str:
    """Liest ein Pflichtfeld als nichtleeren Text."""
    wert = daten.get(schluessel)

    if not isinstance(wert, str):
        raise ValueError(f"Feld '{schluessel}' fehlt oder ist kein Text.")

    bereinigt = wert.strip()
    if not bereinigt:
        raise ValueError(f"Feld '{schluessel}' darf nicht leer sein.")

    return bereinigt


def lese_textfeld_mit_standard(
    daten: Mapping[str, Any],
    schluessel: str,
    standardwert: str,
) -> str:
    """Liest ein Textfeld und nutzt bei fehlendem Wert einen Standard."""
    wert = daten.get(schluessel)

    if wert is None:
        return standardwert

    if not isinstance(wert, str):
        raise ValueError(f"Feld '{schluessel}' muss Text sein.")

    bereinigt = wert.strip()
    return bereinigt or standardwert


def lese_optional_textfeld(daten: Mapping[str, Any], schluessel: str) -> str | None:
    """Liest ein optionales Textfeld und normalisiert Leerwerte zu ``None``."""
    wert = daten.get(schluessel)

    if wert is None:
        return None

    if not isinstance(wert, str):
        raise ValueError(f"Feld '{schluessel}' muss Text oder null sein.")

    bereinigt = wert.strip()
    return bereinigt or None


def lese_optional_boolfeld(daten: Mapping[str, Any], schluessel: str) -> bool | None:
    """Liest ein optionales Bool-Feld und laesst fehlende Werte leer."""
    wert = daten.get(schluessel)

    if wert is None:
        return None

    if isinstance(wert, bool):
        return wert

    raise ValueError(f"Feld '{schluessel}' muss bool oder null sein.")


def lese_datumpflichtfeld(daten: Mapping[str, Any], schluessel: str) -> date:
    """Liest ein Pflichtfeld als ISO-Datum."""
    textwert = lese_textpflichtfeld(daten, schluessel)

    try:
        return date.fromisoformat(textwert)
    except ValueError as exc:
        raise ValueError(f"Feld '{schluessel}' hat kein gueltiges Datum.") from exc


def lese_datumpflichtfeld_mit_fallback(
    daten: Mapping[str, Any],
    schluessel: str,
    fallback_schluessel: str,
) -> date:
    """Liest ein Pflichtdatum und faellt bei Bedarf auf einen Alternativschluessel zurueck."""
    try:
        return lese_datumpflichtfeld(daten, schluessel)
    except ValueError:
        try:
            return lese_datumpflichtfeld(daten, fallback_schluessel)
        except ValueError as exc:
            raise ValueError(
                f"Feld '{schluessel}' oder '{fallback_schluessel}' "
                f"muss ein gueltiges Datum enthalten."
            ) from exc


def lese_optional_zeitpunkt(daten: Mapping[str, Any], schluessel: str) -> datetime | None:
    """Liest ein optionales Feld als ISO-Zeitpunkt."""
    textwert = lese_optional_textfeld(daten, schluessel)

    if textwert is None:
        return None

    try:
        return datetime.fromisoformat(textwert)
    except ValueError as exc:
        raise ValueError(f"Feld '{schluessel}' hat keinen gueltigen Zeitstempel.") from exc


def zeitpunkt_als_iso(zeitpunkt: datetime | None) -> str | None:
    """Wandelt einen optionalen Zeitpunkt in ISO-Text um."""
    if zeitpunkt is None:
        return None

    return zeitpunkt.isoformat()


def optionaler_text(wert: str | None) -> str | None:
    """Bereinigt optionalen Text und gibt Leerwerte als ``None`` zurueck."""
    if wert is None:
        return None

    bereinigt = wert.strip()
    return bereinigt or None



