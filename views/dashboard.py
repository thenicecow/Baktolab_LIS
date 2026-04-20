from __future__ import annotations

from typing import Literal

import streamlit as st


def zeige_aktionskarte(
    *,
    titel: str,
    beschreibung: str,
    button_text: str,
    seitenpfad: str,
    button_typ: Literal["primary", "secondary"] = "secondary",
) -> None:
    with st.container(border=True):
        st.subheader(titel)
        st.write(beschreibung)

        if st.button(button_text, use_container_width=True, type=button_typ):
            st.switch_page(seitenpfad)


def main() -> None:
    anzeige_name = st.session_state.get("name") or st.session_state.get("username") or "Benutzer"

    from ui.header import show_header
    show_header(title="Baktolab - Biomedizinische Labordiagnostik")
    
    st.title("Dashboard")
    st.caption(
        "Zentrale Startseite für das Laborinformationssystem im Modul "
        "Biomedizinische Labordiagnostik."
    )
    st.write(f"Willkommen, **{anzeige_name}**.")
    st.info(
        "Empfohlener Ablauf: zuerst Patient erfassen, danach Material erfassen "
        "und anschliessend in der Patientenübersicht weiterarbeiten."
    )

    spalte_patient, spalte_material, spalte_uebersicht = st.columns(3)

    with spalte_patient:
        zeige_aktionskarte(
            titel="Patienten erfassen",
            beschreibung=(
                "Neue Patienten anlegen. Die eigentliche Eingabemaske wird in einem "
                "späteren Schritt ergänzt."
            ),
            button_text="Patienten erfassen öffnen",
            seitenpfad="views/patienten_erfassen.py",
            button_typ="primary",
        )

    with spalte_material:
        zeige_aktionskarte(
            titel="Material erfassen",
            beschreibung=(
                "Neue Materialien und Proben erfassen. Die fachliche Erfassung "
                "folgt in einem späteren Schritt."
            ),
            button_text="Material erfassen öffnen",
            seitenpfad="views/material_erfassen.py",
        )

    with spalte_uebersicht:
        zeige_aktionskarte(
            titel="Patientenübersicht",
            beschreibung=(
                "Zukünftige Übersicht über alle Patienten. Dieser Bereich ist so "
                "vorbereitet, dass später alle Benutzer denselben Bestand sehen."
            ),
            button_text="Patientenübersicht öffnen",
            seitenpfad="views/patientenuebersicht.py",
        )

    st.markdown("### Aktueller Stand")
    st.markdown("- Dashboard und Kernnavigation sind vorbereitet.")
    st.markdown("- Die Bereiche Patienten, Material und Übersicht sind bewusst als Platzhalter angelegt.")
    st.markdown("- Domänenmodell und Persistenz sind strukturell vorbereitet, aber noch ohne Fachlogik.")


main()
