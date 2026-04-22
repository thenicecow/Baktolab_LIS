"""Hilfen fuer Pfade und Dateinamen der Patientenpersistenz."""

from __future__ import annotations

import posixpath

from persistenz.konfiguration import hole_patienten_dateiname, hole_switchdrive_data_dir


DATEIENDUNG_PATIENTENAKTE = ".json"


def baue_datenwurzel(fs_root_folder: str) -> str:
    """Baut die Datenwurzel fuer die Patientendaten im Dateisystem."""
    basisordner = fs_root_folder.strip().replace("\\", "/").strip("/")
    datenordner = hole_switchdrive_data_dir()

    if not basisordner:
        return datenordner

    return posixpath.join(basisordner, datenordner)


def patientendaten_dateiname() -> str:
    """Liefert den Dateinamen der zentralen Patienten-JSON-Datei."""
    return hole_patienten_dateiname()


def patientendaten_dateipfad() -> str:
    """Liefert den relativen Pfad der zentralen Patienten-JSON-Datei."""
    return patientendaten_dateiname()


def patientenakten_dateiname(patient_id: str) -> str:
    """Erzeugt den Legacy-Dateinamen fuer eine einzelne Patientenakte."""
    bereinigte_patient_id = _bereinige_patient_id(patient_id)
    return f"{bereinigte_patient_id}{DATEIENDUNG_PATIENTENAKTE}"


def patientenakten_dateipfad(patient_id: str) -> str:
    """Liefert den relativen Legacy-Pfad fuer eine einzelne Patientenakte."""
    return patientenakten_dateiname(patient_id)


def ist_patientenakten_datei(dateiname: str) -> bool:
    """Prueft, ob ein Dateiname auf eine alte Einzeldatei einer Patientenakte verweist."""
    bereinigt = dateiname.strip()
    if not bereinigt:
        return False

    return (
        bereinigt.lower().endswith(DATEIENDUNG_PATIENTENAKTE)
        and bereinigt.casefold() != patientendaten_dateiname().casefold()
    )


def _bereinige_patient_id(patient_id: str) -> str:
    """Validiert eine Patienten-ID fuer die Verwendung in Legacy-Dateinamen."""
    bereinigt = patient_id.strip()

    if not bereinigt:
        raise ValueError("Patienten-ID darf nicht leer sein.")

    if "/" in bereinigt or "\\" in bereinigt or bereinigt in {".", ".."}:
        raise ValueError("Patienten-ID enthaelt ungueltige Zeichen.")

    return bereinigt

