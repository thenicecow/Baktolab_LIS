"""Konfigurationshilfen fuer die zentrale Patientenpersistenz."""

from __future__ import annotations

import os


STANDARD_SWITCHDRIVE_DATA_DIR = "patientenakten"
STANDARD_PATIENTEN_DATEINAME = "patienten.json"


def hole_switchdrive_data_dir() -> str:
    """Liest das konfigurierte SwitchDrive-Unterverzeichnis fuer Patientendaten."""
    datenpfad = os.getenv("SWITCHDRIVE_DATA_DIR", STANDARD_SWITCHDRIVE_DATA_DIR)
    bereinigt = datenpfad.strip().replace("\\", "/").strip("/")
    return bereinigt or STANDARD_SWITCHDRIVE_DATA_DIR


def hole_patienten_dateiname() -> str:
    """Liefert den Dateinamen der zentralen Patienten-JSON-Datei."""
    return STANDARD_PATIENTEN_DATEINAME
