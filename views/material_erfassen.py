from __future__ import annotations

from datetime import date
from uuid import uuid4

import streamlit as st

from domaene import (
    KLINISCHE_FRAGESTELLUNGEN,
    KLINISCHE_FRAGESTELLUNGEN_NACH_CODE,
    MATERIALTYPEN,
    MATERIALTYPEN_NACH_CODE,
    Material,
    Patient,
)
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL = "material_erfassen_patient_id"
MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL = "material_erfassen_erfolgsmeldung"


def formatiere_datum(wert: date) -> str:
    return wert.strftime("%d.%m.%Y")


def formatiere_patient_label(patient: Patient) -> str:
    return (
        f"{patient.nachname}, {patient.vorname} "
        f"({formatiere_datum(patient.geburtsdatum)})"
    )


def loese_materialtyp_label_auf(materialtyp_code: str) -> str:
    lookup_wert = MATERIALTYPEN_NACH_CODE.get(materialtyp_code)
    if lookup_wert is None:
        return materialtyp_code

    return lookup_wert.label


def loese_klinische_frage_label_auf(klinische_frage_code: str) -> str:
    lookup_wert = KLINISCHE_FRAGESTELLUNGEN_NACH_CODE.get(klinische_frage_code)
    if lookup_wert is None:
        return klinische_frage_code

    return lookup_wert.label


def hole_aktuellen_user_id() -> str:
    user_id = st.session_state.get("username")

    if not isinstance(user_id, str):
        return ""

    return user_id.strip()


def hole_vorbelegte_patient_id() -> str | None:
    patient_id = st.session_state.get(MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL)

    if not isinstance(patient_id, str):
        return None

    bereinigt = patient_id.strip()
    return bereinigt or None


def erzeuge_material_id() -> str:
    return f"material-{uuid4().hex}"


def lade_patienten(repository: PatientenRepository) -> list[Patient] | None:
    try:
        return repository.lade_alle_patienten()
    except Exception as exc:
        st.error(f"Die Patienten konnten nicht geladen werden: {exc}")
        return None


def zeige_leermeldung() -> None:
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
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )


def speichere_material(
    repository: PatientenRepository,
    patient_id: str,
    materialtyp_code: str,
    klinische_frage_code: str,
    abnahmedatum: date,
    eingangsdatum: date,
) -> tuple[Patient, Material] | None:
    user_id = hole_aktuellen_user_id()
    if not user_id:
        st.error("Es konnte kein angemeldeter Benutzer ermittelt werden.")
        return None

    try:
        patientenakte = repository.lade_patientenakte_nach_id(patient_id)
    except Exception as exc:
        st.error(f"Der ausgewaehlte Patient konnte nicht geladen werden: {exc}")
        return None

    if patientenakte is None:
        st.error("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    patient, materialien = patientenakte

    neues_material = Material(
        id=erzeuge_material_id(),
        patient_id=patient.id,
        materialtyp_code=materialtyp_code,
        klinische_frage_code=klinische_frage_code,
        abnahmedatum=abnahmedatum,
        eingangsdatum=eingangsdatum,
        erstellt_von_user_id=user_id,
    )

    neue_materialien = list(materialien)
    neue_materialien.append(neues_material)

    try:
        repository.speichere_patient_mit_materialien(patient, neue_materialien)
    except ValueError as exc:
        st.error(str(exc))
        return None
    except Exception as exc:
        st.error(f"Das Material konnte nicht gespeichert werden: {exc}")
        return None

    return patient, neues_material


def main() -> None:
    st.title("Material erfassen")
    st.write("Hier kannst du ein neues Material fuer einen bestehenden Patienten erfassen.")

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
                "Bitte waehle einen Patienten aus."
            )

    if vorbelegter_patient is not None:
        st.info(
            f"Material wird fuer {vorbelegter_patient.vorname} "
            f"{vorbelegter_patient.nachname} erfasst."
        )
        st.caption(f"Patienten-ID: {vorbelegter_patient.id}")

    patient_ids = [patient.id for patient in patienten]
    materialtyp_codes = [eintrag.code for eintrag in MATERIALTYPEN]
    klinische_frage_codes = [eintrag.code for eintrag in KLINISCHE_FRAGESTELLUNGEN]

    with st.form("material_erfassen_formular"):
        if vorbelegter_patient is None:
            ausgewaehlte_patient_id = st.selectbox(
                "Patient",
                options=patient_ids,
                index=None,
                placeholder="Patient auswaehlen",
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

        klinische_frage_code = st.selectbox(
            "Klinische Fragestellung",
            options=klinische_frage_codes,
            format_func=loese_klinische_frage_label_auf,
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
            st.error("Bitte waehle einen Patienten aus.")
        elif not isinstance(abnahmedatum, date) or not isinstance(eingangsdatum, date):
            st.error("Bitte gib gueltige Datumswerte ein.")
        else:
            ergebnis = speichere_material(
                repository=repository,
                patient_id=ausgewaehlte_patient_id,
                materialtyp_code=materialtyp_code,
                klinische_frage_code=klinische_frage_code,
                abnahmedatum=abnahmedatum,
                eingangsdatum=eingangsdatum,
            )

            if ergebnis is not None:
                patient, material = ergebnis

                st.session_state[PATIENTENDETAIL_ID_SCHLUESSEL] = patient.id
                st.session_state[MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL] = (
                    f"Material {loese_materialtyp_label_auf(material.materialtyp_code)} "
                    f"wurde erfolgreich gespeichert."
                )
                st.session_state.pop(MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL, None)

                st.switch_page("views/patientendetail.py")

    linke_spalte, rechte_spalte = st.columns(2)

    with linke_spalte:
        if vorbelegter_patient is not None:
            st.page_link(
                "views/patientendetail.py",
                label="Zurueck zur Patientendetailansicht",
                icon=":material/badge:",
            )
        else:
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


main()
