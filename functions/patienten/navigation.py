"""Interne Routing-Helfer fuer die Patientendetailansicht."""

from __future__ import annotations

import streamlit as st


PATIENTENDETAIL_AKTIV_SCHLUESSEL = "patientendetail_aktiv"
PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL = (
    "patientendetail_ausgewaehltes_material_id"
)


def hole_patienten_id_fuer_detailansicht() -> str | None:
    """Liest die aktuell hinterlegte Patienten-ID fuer die Detailansicht."""
    patient_id = st.session_state.get(PATIENTENDETAIL_ID_SCHLUESSEL)

    if not isinstance(patient_id, str):
        return None

    bereinigt = patient_id.strip()
    return bereinigt or None


def aktiviere_patientendetailansicht(patient_id: str) -> bool:
    """Aktiviert die interne Patientendetailansicht fuer eine gueltige Patienten-ID."""
    bereinigt = patient_id.strip()

    if not bereinigt:
        return False

    st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = bereinigt
    st.session_state[PATIENTENDETAIL_AKTIV_SCHLUESSEL] = True
    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)
    return True


def deaktiviere_patientendetailansicht() -> None:
    """Beendet die interne Patientendetailansicht und bereinigt detailspezifischen Zustand."""
    st.session_state.pop(PATIENTENDETAIL_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENDETAIL_ID_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)


def ist_patientendetailansicht_aktiv() -> bool:
    """Prueft, ob die interne Patientendetailansicht aktuell aktiviert ist."""
    return bool(st.session_state.get(PATIENTENDETAIL_AKTIV_SCHLUESSEL, False))


def hat_gueltige_patientendetail_route() -> bool:
    """Prueft, ob die Detailansicht aktiv ist und eine gueltige Patienten-ID vorliegt."""
    return ist_patientendetailansicht_aktiv() and hole_patienten_id_fuer_detailansicht() is not None
