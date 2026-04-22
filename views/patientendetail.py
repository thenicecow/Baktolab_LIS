"""Streamlit-Seite fuer die Detailansicht eines Patienten."""

from __future__ import annotations

import streamlit as st

from domaene import ANALYSEN, MATERIALTYPEN, Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    formatiere_datum,
    formatiere_text,
    formatiere_zeitpunkt,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.patienten.detail import (
    ALLE_FILTER_OPTION,
    ANALYSE_FILTER_SCHLUESSEL,
    MATERIALTYP_FILTER_SCHLUESSEL,
    filtere_materialien,
    hole_und_entferne_erfolgsmeldung,
    initialisiere_filterzustand,
    lade_patientenakte,
    merke_patient_id_fuer_material_erfassen,
    sortiere_materialien,
)


def zeige_erfolgsmeldung() -> None:
    """Zeigt eine gespeicherte Erfolgsmeldung an."""
    erfolgsmeldung = hole_und_entferne_erfolgsmeldung()

    if erfolgsmeldung:
        st.success(erfolgsmeldung)


def zeige_aktionsleiste(patient: Patient | None) -> None:
    """Rendert die Aktionsleiste der Detailansicht."""
    linke_spalte, mittlere_spalte, rechte_spalte = st.columns(3)

    with linke_spalte:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurueck zur Patientenuebersicht",
            icon=":material/groups:",
        )

    with mittlere_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )

    with rechte_spalte:
        if st.button(
            "Material fuer diesen Patienten erfassen",
            use_container_width=True,
            type="primary",
            disabled=patient is None,
        ) and patient is not None:
            merke_patient_id_fuer_material_erfassen(patient.id)
            st.switch_page("views/material_erfassen.py")


def zeige_stammdaten(patient: Patient) -> None:
    """Zeigt die Stammdaten des Patienten an."""
    st.subheader("Stammdaten")

    with st.container(border=True):
        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            st.markdown(f"**Vorname:** {patient.vorname}")
            st.markdown(f"**Nachname:** {patient.nachname}")
            st.markdown(f"**Geburtsdatum:** {formatiere_datum(patient.geburtsdatum)}")

        with rechte_spalte:
            st.markdown(f"**Geschlecht:** {patient.geschlecht}")
            st.markdown(f"**Erstellt am:** {formatiere_zeitpunkt(patient.erstellt_am)}")
            st.markdown(f"**Erstellt von:** {formatiere_text(patient.erstellt_von_user_id)}")


def zeige_filterleiste() -> tuple[str | None, str | None]:
    """Rendert die Filter fuer Materialtyp und Analyse."""
    materialtyp_optionen = [ALLE_FILTER_OPTION] + [eintrag.code for eintrag in MATERIALTYPEN]
    analyse_optionen = [ALLE_FILTER_OPTION] + [eintrag.code for eintrag in ANALYSEN]

    initialisiere_filterzustand(materialtyp_optionen, analyse_optionen)

    with st.container(border=True):
        st.markdown("**Filter**")

        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            materialtyp_code = st.selectbox(
                "Materialtyp",
                options=materialtyp_optionen,
                key=MATERIALTYP_FILTER_SCHLUESSEL,
                format_func=lambda code: (
                    "Alle Materialtypen"
                    if code == ALLE_FILTER_OPTION
                    else loese_materialtyp_label_auf(code)
                ),
            )

        with rechte_spalte:
            analyse_code = st.selectbox(
                "Analyse",
                options=analyse_optionen,
                key=ANALYSE_FILTER_SCHLUESSEL,
                format_func=lambda code: (
                    "Alle Analysen"
                    if code == ALLE_FILTER_OPTION
                    else loese_analyse_label_auf(code)
                ),
            )

    return materialtyp_code or None, analyse_code or None


def zeige_material_log(materialien: list[Material]) -> None:
    """Zeigt das Material-Log des Patienten an."""
    st.subheader("Material-Log")

    if not materialien:
        st.info("Fuer diesen Patienten sind noch keine Materialien erfasst.")
        return

    materialtyp_filter, analyse_filter = zeige_filterleiste()

    gefilterte_materialien = filtere_materialien(
        materialien,
        materialtyp_code=materialtyp_filter,
        analyse_code=analyse_filter,
    )

    sortierte_materialien = sortiere_materialien(gefilterte_materialien)

    if materialtyp_filter or analyse_filter:
        st.caption(
            f"Gefilterte Materialeintraege: {len(sortierte_materialien)} von {len(materialien)}"
        )
    else:
        st.caption(f"Anzahl Materialeintraege: {len(sortierte_materialien)}")

    if not sortierte_materialien:
        st.info("Fuer die gesetzten Filter wurden keine Materialien gefunden.")
        return

    spalten = st.columns((1.6, 2.0, 1.3, 1.3, 1.6, 1.4))
    ueberschriften = (
        "Materialtyp",
        "Analyse",
        "Abnahmedatum",
        "Eingangsdatum",
        "Erstellt am",
        "Erstellt von",
    )

    for spalte, ueberschrift in zip(spalten, ueberschriften):
        spalte.markdown(f"**{ueberschrift}**")

    st.divider()

    for material in sortierte_materialien:
        with st.container(border=True):
            zeilen_spalten = st.columns((1.6, 2.0, 1.3, 1.3, 1.6, 1.4))
            zeilen_spalten[0].write(loese_materialtyp_label_auf(material.materialtyp_code))
            zeilen_spalten[1].write(loese_analyse_label_auf(material.klinische_frage_code))
            zeilen_spalten[2].write(formatiere_datum(material.abnahmedatum))
            zeilen_spalten[3].write(formatiere_datum(material.eingangsdatum))
            zeilen_spalten[4].write(formatiere_zeitpunkt(material.erstellt_am))
            zeilen_spalten[5].write(formatiere_text(material.erstellt_von_user_id))


def main() -> None:
    """Rendert die Patientendetailansicht."""
    st.title("Patientendetail")
    zeige_erfolgsmeldung()

    patientenakte = lade_patientenakte()
    patient = None
    materialien: list[Material] = []

    if patientenakte is not None:
        patient, materialien = patientenakte

    zeige_aktionsleiste(patient)

    if patient is None:
        return

    zeige_stammdaten(patient)
    st.divider()
    zeige_material_log(materialien)


main()


