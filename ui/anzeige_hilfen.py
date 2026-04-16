from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import KLINISCHE_FRAGESTELLUNGEN_NACH_CODE, MATERIALTYPEN_NACH_CODE, Patient


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

    lookup_wert = MATERIALTYPEN_NACH_CODE.get(bereinigt)
    if lookup_wert is None:
        return f"Ungueltiger Materialtyp ({bereinigt})"

    return lookup_wert.label


def loese_klinische_frage_label_auf(klinische_frage_code: str | None) -> str:
    if klinische_frage_code is None:
        return "-"

    lookup_wert = KLINISCHE_FRAGESTELLUNGEN_NACH_CODE.get(klinische_frage_code)
    if lookup_wert is None:
        return formatiere_text(klinische_frage_code)

    return lookup_wert.label

