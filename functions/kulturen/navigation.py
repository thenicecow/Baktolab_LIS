"""Interne Routing-Helfer fuer die Seite ``Kulturen ablesen``."""

from __future__ import annotations

import streamlit as st


KULTUREN_ABLESEN_AKTIV_SCHLUESSEL = "kulturen_ablesen_aktiv"
KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL = "kulturen_ablesen_material_id"


def hole_material_id_fuer_kulturen_ablesen() -> str | None:
    """Liest die aktuell hinterlegte Material-ID fuer ``Kulturen ablesen``."""
    material_id = st.session_state.get(KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL)

    if not isinstance(material_id, str):
        return None

    bereinigt = material_id.strip()
    return bereinigt or None


def aktiviere_kulturen_ablesen(material_id: str) -> bool:
    """Aktiviert die interne Seite ``Kulturen ablesen`` fuer eine gueltige Material-ID."""
    bereinigt = material_id.strip()

    if not bereinigt:
        return False

    st.session_state[KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL] = bereinigt
    st.session_state[KULTUREN_ABLESEN_AKTIV_SCHLUESSEL] = True
    return True


def deaktiviere_kulturen_ablesen() -> None:
    """Beendet die interne Seite ``Kulturen ablesen`` und bereinigt ihren Zustand."""
    st.session_state.pop(KULTUREN_ABLESEN_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL, None)


def ist_kulturen_ablesen_aktiv() -> bool:
    """Prueft, ob die interne Seite ``Kulturen ablesen`` aktuell aktiviert ist."""
    return bool(st.session_state.get(KULTUREN_ABLESEN_AKTIV_SCHLUESSEL, False))


def hat_gueltige_kulturen_ablesen_route() -> bool:
    """Prueft, ob ``Kulturen ablesen`` aktiv ist und eine gueltige Material-ID vorliegt."""
    return ist_kulturen_ablesen_aktiv() and hole_material_id_fuer_kulturen_ablesen() is not None
