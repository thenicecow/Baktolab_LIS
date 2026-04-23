"""Streamlit-Seite zur Erfassung neuer Materialien."""

from __future__ import annotations

from datetime import date

import streamlit as st

from domaene import ANALYSEN, MATERIALTYPEN, Patient
from functions.gemeinsam.anzeige_hilfen import (
    formatiere_patient_label,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import ist_material_fuer_kulturen_ablesen_unterstuetzt
from functions.kulturen.navigation import (
    aktiviere_kulturen_ablesen,
    deaktiviere_kulturen_ablesen,
)
from functions.materialien.erfassung import (
    hole_vorbelegte_patient_id,
    lade_patienten,
    merke_erfolgreiche_materialspeicherung,
    speichere_material,
)
from functions.patienten.navigation import aktiviere_patientendetailansicht
from persistenz import PatientenRepository


def zeige_leermeldung() -> None:
    """Zeigt eine Leermeldung an, wenn noch keine Patienten vorhanden sind."""
    st.info("Es sind noch keine Patienten erfasst. Bitte erfasse zuerst einen Patienten.")

    linke_spalte, rechte_spalte = st.columns(2)

    with linke_spalte:
        st.page_link(
            "views/patienten_erfassen.py",
            label="Patient erfassen",
            icon=":material/person_add:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurück zum Dashboard",
            icon=":material/dashboard:",
        )


def main() -> None:
    """Rendert die Materialerfassung und bindet die Fachlogik ein."""
    st.title("Material erfassen")
    st.write("Hier kannst du ein neues Material für einen bestehenden Patienten erfassen.")

    repository = PatientenRepository()
    patienten = lade_patienten(repository)

    if patienten is None:
        return

    if not patienten:
        zeige_leermeldung()
        return

    patienten_nach_id = {patient.id: patient for patient in patienten}

    vorbelegte_patient_id = hole_vorbelegte_patient_id()
    vorbelegter_patient = None

    if vorbelegte_patient_id is not None:
        vorbelegter_patient = patienten_nach_id.get(vorbelegte_patient_id)

        if vorbelegter_patient is None:
            st.warning(
                "Der vorbelegte Patient wurde nicht gefunden. "
                "Bitte wähle einen Patienten aus."
            )

    if vorbelegter_patient is not None:
        st.info(
            f"Material wird für {vorbelegter_patient.vorname} "
            f"{vorbelegter_patient.nachname} erfasst."
        )
        st.caption(f"Patienten-ID: {vorbelegter_patient.id}")

    patient_ids = [patient.id for patient in patienten]
    materialtyp_codes = [eintrag.code for eintrag in MATERIALTYPEN]
    analyse_codes = [eintrag.code for eintrag in ANALYSEN]

    with st.form("material_erfassen_formular"):
        if vorbelegter_patient is None:
            ausgewaehlte_patient_id = st.selectbox(
                "Patient",
                options=patient_ids,
                index=None,
                placeholder="Patient auswählen",
                format_func=lambda patient_id: formatiere_patient_label(
                    patienten_nach_id[patient_id]
                ),
            )
        else:
            ausgewaehlte_patient_id = vorbelegter_patient.id
            st.text_input(
                "Patient",
                value=formatiere_patient_label(vorbelegter_patient),
                disabled=True,
            )

        materialtyp_code = st.selectbox(
            "Materialtyp",
            options=materialtyp_codes,
            format_func=loese_materialtyp_label_auf,
        )

        analyse_code = st.selectbox(
            "Analyse",
            options=analyse_codes,
            format_func=loese_analyse_label_auf,
        )

        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            abnahmedatum = st.date_input(
                "Abnahmedatum",
                value=date.today(),
                max_value=date.today(),
                format="DD.MM.YYYY",
            )

        with rechte_spalte:
            eingangsdatum = st.date_input(
                "Eingangsdatum",
                value=date.today(),
                max_value=date.today(),
                format="DD.MM.YYYY",
            )

        speichern = st.form_submit_button(
            "Material speichern",
            type="primary",
            use_container_width=True,
        )

    if speichern:
        if ausgewaehlte_patient_id is None:
            st.error("Bitte wähle einen Patienten aus.")
        elif not isinstance(abnahmedatum, date) or not isinstance(eingangsdatum, date):
            st.error("Bitte gib gültige Datumswerte ein.")
        else:
            ergebnis = speichere_material(
                repository=repository,
                patient_id=ausgewaehlte_patient_id,
                materialtyp_code=materialtyp_code,
                analyse_code=analyse_code,
                abnahmedatum=abnahmedatum,
                eingangsdatum=eingangsdatum,
            )

            if ergebnis is not None:
                patient, material = ergebnis
                merke_erfolgreiche_materialspeicherung(patient, material)

                if not aktiviere_patientendetailansicht(patient.id):
                    st.error("Die Patientendetailansicht konnte nicht geöffnet werden.")
                    return

                if ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
                    if not aktiviere_kulturen_ablesen(material.id):
                        st.error("Die Seite 'Kulturen ablesen' konnte nicht geöffnet werden.")
                        return

                    st.switch_page("views/kulturen_ablesen.py")
                else:
                    deaktiviere_kulturen_ablesen()
                    st.switch_page("views/patientenuebersicht.py")

    linke_spalte, rechte_spalte = st.columns(2)

    with linke_spalte:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurück zur Patientenübersicht",
            icon=":material/groups:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurück zum Dashboard",
            icon=":material/dashboard:",
        )


main()
