"""Konfigurationshilfen fuer die zentrale dateibasierte App-Persistenz auf SwitchDrive."""

from __future__ import annotations

import os


STANDARD_SWITCHDRIVE_DATA_DIR = "patientenakten"
STANDARD_PATIENTEN_DATEINAME = "patienten.json"
STANDARD_RESISTENZMONITORING_ORDNERNAME = "resistenzmonitoring"
STANDARD_RESISTENZMONITORING_DATEINAME = "resistenzmonitoring.json"


def hole_switchdrive_data_dir() -> str:
    """Liest das konfigurierte SwitchDrive-Unterverzeichnis fuer die App-Daten."""
    datenpfad = os.getenv("SWITCHDRIVE_DATA_DIR", STANDARD_SWITCHDRIVE_DATA_DIR)
    bereinigt = datenpfad.strip().replace("\\", "/").strip("/")
    return bereinigt or STANDARD_SWITCHDRIVE_DATA_DIR


def hole_patienten_dateiname() -> str:
    """Liefert den Dateinamen der zentralen Patienten-JSON-Datei."""
    return STANDARD_PATIENTEN_DATEINAME


def hole_resistenzmonitoring_ordnername() -> str:
    """Liefert den Namen des separaten Unterordners fuer das Resistenzmonitoring."""
    return STANDARD_RESISTENZMONITORING_ORDNERNAME


def hole_resistenzmonitoring_dateiname() -> str:
    """Liefert den Dateinamen der zentralen JSON-Datei fuer das Resistenzmonitoring."""
    return STANDARD_RESISTENZMONITORING_DATEINAME