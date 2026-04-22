"""Streamlit-Seite fuer die vorbereitete Funktion ``Kulturen ablesen``."""

from __future__ import annotations

import streamlit as st

from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_patient_label,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import (
    ist_material_fuer_kulturen_ablesen_unterstuetzt,
    lade_materialkontext_fuer_kulturen_ablesen,
)
from functions.kulturen.navigation import (
    deaktiviere_kulturen_ablesen,
    hole_material_id_fuer_kulturen_ablesen,
)


def kehre_zur_patientendetailansicht_zurueck() -> None:
    """Beendet die Kulturseite und kehrt per Rerun zur vorherigen internen Ansicht zurueck."""
    deaktiviere_kulturen_ablesen()
    st.rerun()


def zeige_aktionsleiste() -> None:
    """Rendert die wichtigsten Ruecksprung- und Navigationsaktionen."""
    linke_spalte, mittlere_spalte, rechte_spalte = st.columns(3)

    with linke_spalte:
        if st.button(
            "Zurueck zur Patientendetailansicht",
            use_container_width=True,
        ):
            kehre_zur_patientendetailansicht_zurueck()

    with mittlere_spalte:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurueck zur Patientenuebersicht",
            icon=":material/groups:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )


def main() -> None:
    """Rendert die vorbereitete Seite ``Kulturen ablesen``."""
    st.title("Kulturen ablesen")
    st.info(
        "Diese Seite ist aktuell technisch vorbereitet und gilt vorerst nur fuer "
        "Urin mit der Analyse Allgemeine Bakteriologie."
    )

    zeige_aktionsleiste()

    materialreferenz = hole_material_id_fuer_kulturen_ablesen()

    if materialreferenz is None:
        st.info("Es ist aktuell kein Material fuer 'Kulturen ablesen' ausgewaehlt.")
        return

    st.caption(f"Aktuelle Materialreferenz: {materialreferenz}")

    try:
        materialkontext = lade_materialkontext_fuer_kulturen_ablesen()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Das ausgewaehlte Material konnte nicht geladen werden."
            )
        )
        return

    if materialkontext is None:
        st.warning(
            "Zur gesetzten Materialreferenz konnte kein vorhandenes Material gefunden werden."
        )
        return

    patient, material = materialkontext

    with st.container(border=True):
        st.markdown("**Aktuelles Material**")
        st.write(f"Patient: {formatiere_patient_label(patient)}")
        st.write(f"Material-ID: {material.id}")
        st.write(f"Materialtyp: {loese_materialtyp_label_auf(material.materialtyp_code)}")
        st.write(f"Analyse: {loese_analyse_label_auf(material.klinische_frage_code)}")
        st.write(f"Eingangsdatum: {formatiere_datum(material.eingangsdatum)}")

    if not ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
        st.warning(
            "Diese Beurteilung wird aktuell nur fuer Material 'Urin' "
            "mit der Analyse 'Allgemeine Bakteriologie' unterstuetzt."
        )
        return

    st.success(
        "Die Seite ist technisch erreichbar. Eingabemaske, Speicherung und "
        "Beurteilungslogik folgen in einem spaeteren Schritt."
    )


main()
