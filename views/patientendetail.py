from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import KLINISCHE_FRAGESTELLUNGEN_NACH_CODE, MATERIALTYPEN_NACH_CODE, Material, Patient
from persistenz import PatientenRepository


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL = "material_erfassen_patient_id"
MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL = "material_erfassen_erfolgsmeldung"


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


def loese_materialtyp_label_auf(materialtyp_code: str) -> str:
    lookup_wert = MATERIALTYPEN_NACH_CODE.get(materialtyp_code)
    if lookup_wert is None:
        return formatiere_text(materialtyp_code)

    return lookup_wert.label


def loese_klinische_frage_label_auf(klinische_frage_code: str) -> str:
    lookup_wert = KLINISCHE_FRAGESTELLUNGEN_NACH_CODE.get(klinische_frage_code)
    if lookup_wert is None:
        return formatiere_text(klinische_frage_code)

    return lookup_wert.label


def material_sortierschluessel(material: Material) -> tuple[int, int, int, float]:
    abnahmedatum = material.abnahmedatum if isinstance(material.abnahmedatum, date) else None
    erstellt_am = material.erstellt_am if isinstance(material.erstellt_am, datetime) else None

    return (
        1 if abnahmedatum is not None else 0,
        abnahmedatum.toordinal() if abnahmedatum is not None else -1,
        1 if erstellt_am is not None else 0,
        erstellt_am.timestamp() if erstellt_am is not None else float("-inf"),
    )


def sortiere_materialien(materialien: list[Material]) -> list[Material]:
    return sorted(materialien, key=material_sortierschluessel, reverse=True)


def starte_material_erfassen(patient_id: str) -> None:
    st.session_state[MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL] = patient_id
    st.switch_page("views/material_erfassen.py")


def lade_patientenakte() -> tuple[Patient, list[Material]] | None:
    patient_id = st.session_state.get(PATIENTENDETAIL_ID_SCHLUESSEL)

    if not isinstance(patient_id, str) or not patient_id.strip():
        st.info("Es wurde noch kein Patient ausgewaehlt.")
        return None

    repository = PatientenRepository()

    try:
        patientenakte = repository.lade_patientenakte_nach_id(patient_id)
    except Exception as exc:
        st.error(f"Der ausgewaehlte Patient konnte nicht geladen werden: {exc}")
        return None

    if patientenakte is None:
        st.warning("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    return patientenakte


def zeige_erfolgsmeldung() -> None:
    erfolgsmeldung = st.session_state.pop(MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL, None)

    if erfolgsmeldung:
        st.success(erfolgsmeldung)


def zeige_aktionsleiste(patient: Patient | None) -> None:
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
            starte_material_erfassen(patient.id)


def zeige_stammdaten(patient: Patient) -> None:
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


def zeige_material_log(materialien: list[Material]) -> None:
    st.subheader("Material-Log")

    if not materialien:
        st.info("Fuer diesen Patienten sind noch keine Materialien erfasst.")
        return

    st.caption(f"Anzahl Materialeintraege: {len(materialien)}")

    spalten = st.columns((1.6, 2.0, 1.3, 1.3, 1.6, 1.4))
    ueberschriften = (
        "Materialtyp",
        "Klinische Fragestellung",
        "Abnahmedatum",
        "Eingangsdatum",
        "Erstellt am",
        "Erstellt von",
    )

    for spalte, ueberschrift in zip(spalten, ueberschriften):
        spalte.markdown(f"**{ueberschrift}**")

    st.divider()

    for material in sortiere_materialien(materialien):
        with st.container(border=True):
            zeilen_spalten = st.columns((1.6, 2.0, 1.3, 1.3, 1.6, 1.4))
            zeilen_spalten[0].write(loese_materialtyp_label_auf(material.materialtyp_code))
            zeilen_spalten[1].write(
                loese_klinische_frage_label_auf(material.klinische_frage_code)
            )
            zeilen_spalten[2].write(formatiere_datum(material.abnahmedatum))
            zeilen_spalten[3].write(formatiere_datum(material.eingangsdatum))
            zeilen_spalten[4].write(formatiere_zeitpunkt(material.erstellt_am))
            zeilen_spalten[5].write(formatiere_text(material.erstellt_von_user_id))


def main() -> None:
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

