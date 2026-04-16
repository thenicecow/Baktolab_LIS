from __future__ import annotations

import os


STANDARD_SWITCHDRIVE_DATA_DIR = "patientenakten"


def hole_switchdrive_data_dir() -> str:
    datenpfad = os.getenv("SWITCHDRIVE_DATA_DIR", STANDARD_SWITCHDRIVE_DATA_DIR)
    bereinigt = datenpfad.strip().replace("\\", "/").strip("/")
    return bereinigt or STANDARD_SWITCHDRIVE_DATA_DIR
