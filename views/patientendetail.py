"""Streamlit-Seite fuer die Detailansicht eines Patienten."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from domaene import ANALYSEN, MATERIALTYPEN, Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    formatiere_datum,
    formatiere_text,
    formatiere_zeitpunkt,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import ist_material_fuer_kulturen_ablesen_unterstuetzt
from functions.kulturen.navigation import aktiviere_kulturen_ablesen
from functions.patienten.detail import (
    ALLE_FILTER_OPTION,
    ANALYSE_FILTER_SCHLUESSEL,
    MATERIALTYP_FILTER_SCHLUESSEL,
    baue_ansatzhinweis_fuer_ausgewaehltes_material,
    filtere_materialien,
    hole_und_entferne_ansatzhinweis,
    hole_und_entferne_bearbeitungserfolgsmeldung,
    hole_und_entferne_erfolgsmeldung,
    initialisiere_filterzustand,
    lade_patientenakte,
    merke_material_fuer_ansatzhinweis,
    merke_patient_id_fuer_material_erfassen,
    sortiere_materialien,
)
from functions.patienten.loeschen import (
    LOESCHEN_BESTAETIGUNG_SCHLUESSEL,
    bereinige_patientbezogenen_zustand_nach_loeschung,
    initialisiere_loeschzustand,
    loesche_patient,
    merke_erfolgreiche_loeschung,
)
from functions.patienten.navigation import (
    aktiviere_patientendetailansicht,
    deaktiviere_patientendetailansicht,
)


def zeige_erfolgsmeldungen() -> None:
    """Zeigt gespeicherte Erfolgsmeldungen an."""
    bearbeitungserfolg = hole_und_entferne_bearbeitungserfolgsmeldung()
    if bearbeitungserfolg:
        st.success(bearbeitungserfolg)

    erfolgsmeldung_material = hole_und_entferne_erfolgsmeldung()
    if erfolgsmeldung_material:
        st.success(erfolgsmeldung_material)


def zeige_ansatzhinweistabelle(
    ansatzhinweis: dict[str, object] | None,
    ueberschrift: str,
) -> None:
    """Zeigt einen Ansatzhinweis als Tabelle oder neutrale Info an."""
    if ansatzhinweis is None:
        return

    titel = ansatzhinweis.get("titel")
    zeilen = ansatzhinweis.get("zeilen")
    hinweistext = ansatzhinweis.get("hinweistext")

    with st.container(border=True):
        st.markdown(f"**{ueberschrift}**")

        if isinstance(titel, str) and titel.strip():
            st.caption(titel.strip())

        if isinstance(zeilen, list) and zeilen:
            st.table(pd.DataFrame(zeilen, columns=["Ansatz", "Inkubation"]))
            return

        if isinstance(hinweistext, str) and hinweistext.strip():
            st.info(hinweistext.strip())


def zeige_ansatzhinweis_nach_speicherung() -> None:
    """Zeigt den Hinweis fuer ein soeben erfolgreich gespeichertes Material an."""
    ansatzhinweis = hole_und_entferne_ansatzhinweis()
    zeige_ansatzhinweistabelle(
        ansatzhinweis,
        "Ansatzhinweis zum neu erfassten Material",
    )


def zeige_ansatzhinweis_zum_ausgewaehlten_material(materialien: list[Material]) -> None:
    """Zeigt den Hinweis fuer das in der Materialliste ausgewaehlte Material an."""
    ansatzhinweis = baue_ansatzhinweis_fuer_ausgewaehltes_material(materialien)
    zeige_ansatzhinweistabelle(
        ansatzhinweis,
        "Ansatzhinweis zum ausgewaehlten Material",
    )


def wechsle_zu_sichtbarer_seite(zielseite: str) -> None:
    """Beendet die interne Detailansicht und wechselt zu einer sichtbaren Seite."""
    deaktiviere_patientendetailansicht()
    st.switch_page(zielseite)


def oeffne_materialerfassung_aus_detail(patient_id: str) -> None:
    """Oeffnet die Materialerfassung fuer den aktuellen Patienten."""
    merke_patient_id_fuer_material_erfassen(patient_id)
    deaktiviere_patientendetailansicht()
    st.switch_page("views/material_erfassen.py")


def oeffne_patientbearbeitung_aus_detail(patient_id: str) -> None:
    """Oeffnet die Bearbeitungsseite fuer den aktuellen Patienten."""
    if not aktiviere_patientendetailansicht(patient_id):
        st.error("Die Patientenbearbeitung konnte nicht geoeffnet werden.")
        return

    st.switch_page("views/patient_bearbeiten.py")


def oeffne_kulturen_ablesen(material_id: str) -> None:
    """Aktiviert die Seite ``Kulturen ablesen`` fuer ein Material."""
    if not aktiviere_kulturen_ablesen(material_id):
        st.error("Die Seite 'Kulturen ablesen' konnte nicht geoeffnet werden.")
        return

    st.switch_page("views/kulturen_ablesen.py")


def zeige_aktionsleiste(patient: Patient | None) -> None:
    """Rendert die Aktionsleiste der Detailansicht."""
    erste_spalte, zweite_spalte, dritte_spalte, vierte_spalte = st.columns(4)

    with erste_spalte:
        if st.button(
            "Zurueck zur Patientenuebersicht",
            use_container_width=True,
        ):
            wechsle_zu_sichtbarer_seite("views/patientenuebersicht.py")

    with zweite_spalte:
        if st.button(
            "Zurueck zum Dashboard",
            use_container_width=True,
        ):
            wechsle_zu_sichtbarer_seite("views/dashboard.py")

    with dritte_spalte:
        if st.button(
            "Patient bearbeiten",
            use_container_width=True,
            disabled=patient is None,
        ) and patient is not None:
            oeffne_patientbearbeitung_aus_detail(patient.id)

    with vierte_spalte:
        if st.button(
            "Material fuer diesen Patienten erfassen",
            use_container_width=True,
            type="primary",
            disabled=patient is None,
        ) and patient is not None:
            oeffne_materialerfassung_aus_detail(patient.id)


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


def zeige_loeschsektion(patient: Patient) -> None:
    """Zeigt eine bewusst abgesicherte Loeschsektion fuer den aktuellen Patienten an."""
    initialisiere_loeschzustand(patient.id)

    with st.expander("Patient loeschen", expanded=False):
        st.warning(
            "Wenn du diesen Patienten loeschst, werden auch alle zugehoerigen "
            "Materialien und vorhandenen Kulturdaten dauerhaft entfernt."
        )
        st.checkbox(
            "Ich habe die Warnung gelesen und moechte diesen Patienten wirklich loeschen.",
            key=LOESCHEN_BESTAETIGUNG_SCHLUESSEL,
        )

        if st.button(
            "Patient endgueltig loeschen",
            use_container_width=True,
            disabled=not bool(st.session_state.get(LOESCHEN_BESTAETIGUNG_SCHLUESSEL, False)),
        ):
            erfolgsmeldung = loesche_patient(patient.id)

            if erfolgsmeldung is not None:
                bereinige_patientbezogenen_zustand_nach_loeschung()
                merke_erfolgreiche_loeschung(erfolgsmeldung)
                st.switch_page("views/patientenuebersicht.py")


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

    st.caption(
        "Mit 'Anzeigen' kannst du den passenden Ansatzhinweis erneut aufrufen. "
        "Mit 'Kulturen' gelangst du bei passenden Urinmaterialien zur neuen Seite."
    )

    if not sortierte_materialien:
        st.info("Fuer die gesetzten Filter wurden keine Materialien gefunden.")
        return

    spalten = st.columns((1.4, 1.8, 1.2, 1.2, 1.4, 1.2, 1.0, 1.1))
    ueberschriften = (
        "Materialtyp",
        "Analyse",
        "Abnahmedatum",
        "Eingangsdatum",
        "Erstellt am",
        "Erstellt von",
        "Hinweis",
        "Kulturen",
    )

    for spalte, ueberschrift in zip(spalten, ueberschriften):
        spalte.markdown(f"**{ueberschrift}**")

    st.divider()

    for material in sortierte_materialien:
        with st.container(border=True):
            zeilen_spalten = st.columns((1.4, 1.8, 1.2, 1.2, 1.4, 1.2, 1.0, 1.1))
            zeilen_spalten[0].write(loese_materialtyp_label_auf(material.materialtyp_code))
            zeilen_spalten[1].write(loese_analyse_label_auf(material.klinische_frage_code))
            zeilen_spalten[2].write(formatiere_datum(material.abnahmedatum))
            zeilen_spalten[3].write(formatiere_datum(material.eingangsdatum))
            zeilen_spalten[4].write(formatiere_zeitpunkt(material.erstellt_am))
            zeilen_spalten[5].write(formatiere_text(material.erstellt_von_user_id))

            if zeilen_spalten[6].button(
                "Anzeigen",
                key=f"material_hinweis_{material.id}",
                use_container_width=True,
            ):
                merke_material_fuer_ansatzhinweis(material.id)

            if ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
                if zeilen_spalten[7].button(
                    "Kulturen",
                    key=f"material_kulturen_{material.id}",
                    use_container_width=True,
                ):
                    oeffne_kulturen_ablesen(material.id)
            else:
                zeilen_spalten[7].write("-")


def main() -> None:
    """Rendert die Patientendetailansicht."""
    st.title("Patientendetail")
    zeige_erfolgsmeldungen()
    zeige_ansatzhinweis_nach_speicherung()

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
    zeige_loeschsektion(patient)
    st.divider()
    zeige_material_log(materialien)
    zeige_ansatzhinweis_zum_ausgewaehlten_material(materialien)


if __name__ == "__main__":
    main()
