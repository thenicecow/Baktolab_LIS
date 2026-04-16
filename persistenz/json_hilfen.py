from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any

from domaene import (
    Material,
    Patient,
    ist_gueltiger_analyse_code,
    normalisiere_materialtyp_code,
)
from utils.data_handler import DataHandler


logger = logging.getLogger(__name__)


def lade_json_objekt(
    data_handler: DataHandler,
    relativer_pfad: str,
) -> dict[str, Any] | None:
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
    data_handler.save(relativer_pfad, dict(daten))


def patient_als_dict(patient: Patient) -> dict[str, Any]:
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
        "klinische_frage_code": analyse_code,
        "abnahmedatum": material.abnahmedatum.isoformat(),
        "eingangsdatum": material.eingangsdatum.isoformat(),
        "erstellt_am": zeitpunkt_als_iso(material.erstellt_am),
        "erstellt_von_user_id": optionaler_text(material.erstellt_von_user_id),
    }


def material_aus_dict(daten: Mapping[str, Any]) -> Material:
    materialtyp_code_roh = lese_textpflichtfeld(daten, "materialtyp_code")
    materialtyp_code = normalisiere_materialtyp_code(materialtyp_code_roh)

    if materialtyp_code is None:
        materialtyp_code = materialtyp_code_roh.strip()

    return Material(
        id=lese_textpflichtfeld(daten, "id"),
        patient_id=lese_textpflichtfeld(daten, "patient_id"),
        materialtyp_code=materialtyp_code,
        klinische_frage_code=lese_textpflichtfeld(daten, "klinische_frage_code"),
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
    )


def patientenakte_als_dict(
    patient: Patient,
    materialien: Sequence[Material],
) -> dict[str, Any]:
    return {
        "patient": patient_als_dict(patient),
        "materialien": materialien_als_listendaten(materialien),
    }


def materialien_als_listendaten(materialien: Sequence[Material]) -> list[dict[str, Any]]:
    listendaten: list[dict[str, Any]] = []

    for index, material in enumerate(materialien, start=1):
        try:
            listendaten.append(material_als_dict(material))
        except ValueError as exc:
            raise ValueError(f"Materialeintrag {index} ist ungueltig: {exc}") from exc

    return listendaten


def patientenakte_aus_dict(
    daten: Mapping[str, Any],
) -> tuple[Patient, list[Material]]:
    patient_rohdaten = lese_dict(daten, "patient")
    materialien_rohdaten = daten.get("materialien", [])

    if materialien_rohdaten is None:
        materialien_rohdaten = []
    elif not isinstance(materialien_rohdaten, list):
        logger.warning("Feld 'materialien' ist ungueltig und wird als leer behandelt.")
        materialien_rohdaten = []

    patient = patient_aus_dict(patient_rohdaten)
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

    return patient, materialien


def lese_dict(daten: Mapping[str, Any], schluessel: str) -> Mapping[str, Any]:
    wert = daten.get(schluessel)

    if not isinstance(wert, Mapping):
        raise ValueError(f"Feld '{schluessel}' fehlt oder ist ungueltig.")

    return wert


def lese_textpflichtfeld(daten: Mapping[str, Any], schluessel: str) -> str:
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
    wert = daten.get(schluessel)

    if wert is None:
        return standardwert

    if not isinstance(wert, str):
        raise ValueError(f"Feld '{schluessel}' muss Text sein.")

    bereinigt = wert.strip()
    return bereinigt or standardwert


def lese_optional_textfeld(daten: Mapping[str, Any], schluessel: str) -> str | None:
    wert = daten.get(schluessel)

    if wert is None:
        return None

    if not isinstance(wert, str):
        raise ValueError(f"Feld '{schluessel}' muss Text oder null sein.")

    bereinigt = wert.strip()
    return bereinigt or None


def lese_datumpflichtfeld(daten: Mapping[str, Any], schluessel: str) -> date:
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
    textwert = lese_optional_textfeld(daten, schluessel)

    if textwert is None:
        return None

    try:
        return datetime.fromisoformat(textwert)
    except ValueError as exc:
        raise ValueError(f"Feld '{schluessel}' hat keinen gueltigen Zeitstempel.") from exc


def zeitpunkt_als_iso(zeitpunkt: datetime | None) -> str | None:
    if zeitpunkt is None:
        return None

    return zeitpunkt.isoformat()


def optionaler_text(wert: str | None) -> str | None:
    if wert is None:
        return None

    bereinigt = wert.strip()
    return bereinigt or None

