from __future__ import annotations

from datetime import date, datetime

import streamlit as st

from domaene import ANALYSEN, MATERIALTYPEN, Material, Patient
from persistenz import PatientenRepository
from ui.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_text,
    formatiere_zeitpunkt,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)


PATIENTENDETAIL_ID_SCHLUESSEL = "patientendetail_patient_id"
MATERIAL_ERFASSEN_PATIENT_ID_SCHLUESSEL = "material_erfassen_patient_id"
MATERIAL_ERFASSEN_ERFOLGSMELDUNG_SCHLUESSEL = "material_erfassen_erfolgsmeldung"
ALLE_FILTER_OPTION = ""
MATERIALTYP_FILTER_SCHLUESSEL = "patientendetail_filter_materialtyp"
ANALYSE_FILTER_SCHLUESSEL = "patientendetail_filter_analyse"


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


def filtere_materialien(
    materialien: list[Material],
    materialtyp_code: str | None,
    analyse_code: str | None,
) -> list[Material]:
    gefilterte_materialien: list[Material] = []

    for material in materialien:
        if materialtyp_code and material.materialtyp_code != materialtyp_code:
            continue

        if analyse_code and material.klinische_frage_code != analyse_code:
            continue

        gefilterte_materialien.append(material)

    return gefilterte_materialien


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
    except Exception:
        st.error(baue_technische_fehlernachricht("Der ausgewaehlte Patient konnte nicht geladen werden."))
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


def initialisiere_filterzustand(
    materialtyp_optionen: list[str],
    analyse_optionen: list[str],
) -> None:
    materialtyp_wert = st.session_state.get(MATERIALTYP_FILTER_SCHLUESSEL)
    if not isinstance(materialtyp_wert, str) or materialtyp_wert not in materialtyp_optionen:
        st.session_state[MATERIALTYP_FILTER_SCHLUESSEL] = ALLE_FILTER_OPTION

    analyse_wert = st.session_state.get(ANALYSE_FILTER_SCHLUESSEL)
    if not isinstance(analyse_wert, str) or analyse_wert not in analyse_optionen:
        st.session_state[ANALYSE_FILTER_SCHLUESSEL] = ALLE_FILTER_OPTION


def zeige_filterleiste() -> tuple[str | None, str | None]:
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



