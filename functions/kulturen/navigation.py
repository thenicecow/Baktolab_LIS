"""Interne Routing-Helfer fuer die Seiten ``Kulturen ablesen`` und ``Befund``."""

from __future__ import annotations

import streamlit as st

from ui.navigation import SICHTBARE_NAVIGATION_URL_SCHLUESSEL


KULTUREN_ABLESEN_AKTIV_SCHLUESSEL = "kulturen_ablesen_aktiv"
KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL = "kulturen_ablesen_material_id"
KULTUREN_ABLESEN_URSPRUNG_URL_SCHLUESSEL = "kulturen_ablesen_ursprung_url"
KULTUREN_ABLESEN_BEFUND_AKTIV_SCHLUESSEL = "kulturen_ablesen_befund_aktiv"
KULTUREN_ABLESEN_BEFUND_MATERIAL_ID_SCHLUESSEL = "kulturen_ablesen_befund_material_id"
KULTUREN_ABLESEN_FORMULAR_PREFIX = "kulturen_ablesen_"


def hole_material_id_fuer_kulturen_ablesen() -> str | None:
    """Liest die aktuell hinterlegte Material-ID fuer ``Kulturen ablesen``."""
    material_id = st.session_state.get(KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL)

    if not isinstance(material_id, str):
        return None

    bereinigt = material_id.strip()
    return bereinigt or None


def hole_material_id_fuer_befund() -> str | None:
    """Liest die aktuell hinterlegte Material-ID fuer die interne Befundansicht."""
    material_id = st.session_state.get(KULTUREN_ABLESEN_BEFUND_MATERIAL_ID_SCHLUESSEL)

    if not isinstance(material_id, str):
        return None

    bereinigt = material_id.strip()
    return bereinigt or None


def hole_ursprungsseite_fuer_kulturen_ablesen() -> str | None:
    """Liest die sichtbare Ursprungsseite der aktuellen Kulturansicht."""
    ursprungsseite_url = st.session_state.get(KULTUREN_ABLESEN_URSPRUNG_URL_SCHLUESSEL)

    if not isinstance(ursprungsseite_url, str):
        return None

    bereinigt = ursprungsseite_url.strip()
    return bereinigt or None


def aktiviere_kulturen_ablesen(material_id: str) -> bool:
    """Aktiviert die interne Seite ``Kulturen ablesen`` fuer eine gueltige Material-ID."""
    bereinigt = material_id.strip()

    if not bereinigt:
        return False

    st.session_state[KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL] = bereinigt
    st.session_state[KULTUREN_ABLESEN_AKTIV_SCHLUESSEL] = True
    deaktiviere_befund()

    ursprungsseite_url = st.session_state.get(SICHTBARE_NAVIGATION_URL_SCHLUESSEL)
    if isinstance(ursprungsseite_url, str) and ursprungsseite_url.strip():
        st.session_state[KULTUREN_ABLESEN_URSPRUNG_URL_SCHLUESSEL] = (
            ursprungsseite_url.strip()
        )
    else:
        st.session_state.pop(KULTUREN_ABLESEN_URSPRUNG_URL_SCHLUESSEL, None)

    return True


def aktiviere_befund(material_id: str) -> bool:
    """Aktiviert die interne Befundansicht fuer ein bereits gewaehltetes Material."""
    bereinigt = material_id.strip()

    if not bereinigt:
        return False

    st.session_state[KULTUREN_ABLESEN_MATERIAL_ID_SCHLUESSEL] = bereinigt
    st.session_state[KULTUREN_ABLESEN_AKTIV_SCHLUESSEL] = True
    st.session_state[KULTUREN_ABLESEN_BEFUND_MATERIAL_ID_SCHLUESSEL] = bereinigt
    st.session_state[KULTUREN_ABLESEN_BEFUND_AKTIV_SCHLUESSEL] = True
    return True


def deaktiviere_befund() -> None:
    """Beendet die interne Befundansicht und bereinigt ihren Zustand."""
    st.session_state.pop(KULTUREN_ABLESEN_BEFUND_AKTIV_SCHLUESSEL, None)
    st.session_state.pop(KULTUREN_ABLESEN_BEFUND_MATERIAL_ID_SCHLUESSEL, None)


def deaktiviere_kulturen_ablesen() -> None:
    """Beendet die interne Seite ``Kulturen ablesen`` und bereinigt ihren Zustand."""
    for schluessel in list(st.session_state.keys()):
        if schluessel.startswith(KULTUREN_ABLESEN_FORMULAR_PREFIX):
            st.session_state.pop(schluessel, None)


def ist_kulturen_ablesen_aktiv() -> bool:
    """Prueft, ob die interne Seite ``Kulturen ablesen`` aktuell aktiviert ist."""
    return bool(st.session_state.get(KULTUREN_ABLESEN_AKTIV_SCHLUESSEL, False))


def ist_befund_aktiv() -> bool:
    """Prueft, ob die interne Befundansicht aktuell aktiviert ist."""
    return bool(st.session_state.get(KULTUREN_ABLESEN_BEFUND_AKTIV_SCHLUESSEL, False))


def hat_gueltige_kulturen_ablesen_route() -> bool:
    """Prueft, ob ``Kulturen ablesen`` aktiv ist und eine gueltige Material-ID vorliegt."""
    return ist_kulturen_ablesen_aktiv() and hole_material_id_fuer_kulturen_ablesen() is not None


def hat_gueltige_befund_route() -> bool:
    """Prueft, ob die interne Befundansicht aktiv ist und zum aktuellen Material passt."""
    material_id = hole_material_id_fuer_kulturen_ablesen()
    befund_material_id = hole_material_id_fuer_befund()

    if not ist_befund_aktiv():
        return False

    if material_id is None or befund_material_id is None:
        return False

    return material_id == befund_material_id


def darf_kulturen_ablesen_gerendert_werden(
    aktuelle_sichtbare_navigation_url: str | None,
) -> bool:
    """Prueft, ob die interne Kulturansicht die sichtbare Navigation ueberlagern darf."""
    if not hat_gueltige_kulturen_ablesen_route():
        return False

    ursprungsseite_url = hole_ursprungsseite_fuer_kulturen_ablesen()
    if ursprungsseite_url is None or aktuelle_sichtbare_navigation_url is None:
        return True

    return aktuelle_sichtbare_navigation_url == ursprungsseite_url
