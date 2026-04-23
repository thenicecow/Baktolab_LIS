"""Interne Routing-Helfer fuer Patientendetail und Patientenbearbeitung."""

from __future__ import annotations

import streamlit as st


PATIENTENDETAIL_AKTIV_SCHLUESSEL = "patientendetail_aktiv"
PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL = (
    "patientendetail_ausgewaehltes_material_id"
)
PATIENTENBEARBEITUNG_AKTIV_SCHLUESSEL = "patient_bearbeiten_aktiv"
PATIENTENBEARBEITUNG_ID_SCHLUESSEL = "patient_bearbeiten_patient_id"


def hole_patienten_id_fuer_detailansicht() -> str | None:
    """Liest die aktuell hinterlegte Patienten-ID fuer die Detailansicht."""
    patient_id = st.session_state.get(PATIENTENDETAIL_ID_SCHLUESSEL)

    if not isinstance(patient_id, str):
        return None

    bereinigt = patient_id.strip()
    return bereinigt or None


def hole_patienten_id_fuer_bearbeitung() -> str | None:
    """Liest die aktuell hinterlegte Patienten-ID fuer die interne Bearbeitung."""
    patient_id = st.session_state.get(PATIENTENBEARBEITUNG_ID_SCHLUESSEL)

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
    deaktiviere_patientenbearbeitung()
    return True


def aktiviere_patientenbearbeitung(patient_id: str) -> bool:
    """Aktiviert die interne Patientenbearbeitung fuer eine gueltige Patienten-ID."""
    bereinigt = patient_id.strip()

    if not bereinigt:
        return False

    st.session_state[PATIENTENBEARBEITUNG_ID_SCHLUESSEL] = bereinigt
    st.session_state[PATIENTENBEARBEITUNG_AKTIV_SCHLUESSEL] = True
    st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = bereinigt
    st.session_state.pop(PATIENTENDETAIL_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)
    return True


def deaktiviere_patientendetailansicht() -> None:
    """Beendet die interne Patientendetailansicht und bereinigt detailspezifischen Zustand."""
    st.session_state.pop(PATIENTENDETAIL_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENDETAIL_ID_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENDETAIL_AUSGEWAEHLTES_MATERIAL_ID_SCHLUESSEL, None)


def deaktiviere_patientenbearbeitung() -> None:
    """Beendet die interne Patientenbearbeitung und bereinigt bearbeitungsspezifischen Zustand."""
    st.session_state.pop(PATIENTENBEARBEITUNG_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(PATIENTENBEARBEITUNG_ID_SCHLUESSEL, None)


def ist_patientendetailansicht_aktiv() -> bool:
    """Prueft, ob die interne Patientendetailansicht aktuell aktiviert ist."""
    return bool(st.session_state.get(PATIENTENDETAIL_AKTIV_SCHLUESSEL, False))


def ist_patientenbearbeitung_aktiv() -> bool:
    """Prueft, ob die interne Patientenbearbeitung aktuell aktiviert ist."""
    return bool(st.session_state.get(PATIENTENBEARBEITUNG_AKTIV_SCHLUESSEL, False))


def hat_gueltige_patientendetail_route() -> bool:
    """Prueft, ob die Detailansicht aktiv ist und eine gueltige Patienten-ID vorliegt."""
    return ist_patientendetailansicht_aktiv() and hole_patienten_id_fuer_detailansicht() is not None


def hat_gueltige_patientenbearbeiten_route() -> bool:
    """Prueft, ob die Bearbeitung aktiv ist und eine gueltige Patienten-ID vorliegt."""
    return ist_patientenbearbeitung_aktiv() and hole_patienten_id_fuer_bearbeitung() is not None
