from __future__ import annotations

import posixpath

from persistenz.konfiguration import hole_switchdrive_data_dir


DATEIENDUNG_PATIENTENAKTE = ".json"


def baue_datenwurzel(fs_root_folder: str) -> str:
    basisordner = fs_root_folder.strip().replace("\\", "/").strip("/")
    datenordner = hole_switchdrive_data_dir()

    if not basisordner:
        return datenordner

    return posixpath.join(basisordner, datenordner)


def patientenakten_dateiname(patient_id: str) -> str:
    bereinigte_patient_id = _bereinige_patient_id(patient_id)
    return f"{bereinigte_patient_id}{DATEIENDUNG_PATIENTENAKTE}"


def patientenakten_dateipfad(patient_id: str) -> str:
    return patientenakten_dateiname(patient_id)


def ist_patientenakten_datei(dateiname: str) -> bool:
    return dateiname.lower().endswith(DATEIENDUNG_PATIENTENAKTE)


def _bereinige_patient_id(patient_id: str) -> str:
    bereinigt = patient_id.strip()

    if not bereinigt:
        raise ValueError("Patienten-ID darf nicht leer sein.")

    if "/" in bereinigt or "\\" in bereinigt or bereinigt in {".", ".."}:
        raise ValueError("Patienten-ID enthaelt ungueltige Zeichen.")

    return bereinigt
