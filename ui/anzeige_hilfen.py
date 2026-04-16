from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import ANALYSEN_NACH_CODE, MATERIALTYPEN_NACH_CODE, Patient, normalisiere_materialtyp_code


def formatiere_datum(wert: date | None) -> str:
    if wert is None:
        return "-"

    return wert.strftime("%d.%m.%Y")


def formatiere_zeitpunkt(wert: datetime | None) -> str:
    if wert is None:
        return "-"

    return wert.strftime("%d.%m.%Y %H:%M")


def formatiere_text(wert: str | None) -> str:
    if wert is None:
        return "-"

    bereinigt = wert.strip()
    return bereinigt or "-"


def formatiere_patient_label(patient: Patient) -> str:
    return (
        f"{patient.nachname}, {patient.vorname} "
        f"({formatiere_datum(patient.geburtsdatum)})"
    )


def hole_aktuellen_user_id() -> str:
    user_id = st.session_state.get("username")

    if not isinstance(user_id, str):
        return ""

    return user_id.strip()


def baue_technische_fehlernachricht(aktion: str) -> str:
    return f"{aktion} Bitte pruefe die Datenablage und versuche es erneut."


def loese_materialtyp_label_auf(materialtyp_code: str | None) -> str:
    if materialtyp_code is None:
        return "-"

    bereinigt = materialtyp_code.strip()
    if not bereinigt:
        return "-"

    materialtyp_code_normalisiert = normalisiere_materialtyp_code(bereinigt)
    if materialtyp_code_normalisiert is None:
        return f"Ungueltiger Materialtyp ({bereinigt})"

    lookup_wert = MATERIALTYPEN_NACH_CODE.get(materialtyp_code_normalisiert)
    if lookup_wert is None:
        return f"Ungueltiger Materialtyp ({bereinigt})"

    return lookup_wert.label


def loese_analyse_label_auf(analyse_code: str | None) -> str:
    if analyse_code is None:
        return "-"

    bereinigt = analyse_code.strip()
    if not bereinigt:
        return "-"

    lookup_wert = ANALYSEN_NACH_CODE.get(bereinigt)
    if lookup_wert is None:
        return f"Ungueltige Analyse ({bereinigt})"

    return lookup_wert.label


def loese_klinische_frage_label_auf(klinische_frage_code: str | None) -> str:
    return loese_analyse_label_auf(klinische_frage_code)


