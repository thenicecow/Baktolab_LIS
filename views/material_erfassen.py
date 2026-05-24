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
from functions.kulturen.ablesen import (
    UNTERSTUETZTER_ANALYSE_CODE,
    UNTERSTUETZTER_MATERIALTYP_CODE,
    ist_material_fuer_kulturen_ablesen_unterstuetzt,
)
from ui.header import show_header
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


def ist_direkter_kulturworkflow(materialtyp_code: str, analyse_code: str) -> bool:
    """Prueft, ob nach dem Speichern direkt 'Kulturen ablesen' folgt."""
    return (
        materialtyp_code == UNTERSTUETZTER_MATERIALTYP_CODE
        and analyse_code == UNTERSTUETZTER_ANALYSE_CODE
    )


def zeige_design_css() -> None:
    """Ergänzt kleine lokale Styles für diese Seite."""
    st.markdown(
        """
        <style>
        .material-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
            min-height: 118px;
        }

        .material-card-title {
            font-size: 0.82rem;
            color: #475569;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .material-card-value {
            font-size: 1.9rem;
            color: #1d4ed8;
            font-weight: 800;
            line-height: 1.1;
        }

        .material-card-caption {
            font-size: 0.78rem;
            color: #64748b;
            margin-top: 0.35rem;
        }

        .workflow-box {
            border-radius: 16px;
            padding: 1rem 1.2rem;
            border: 1px solid #bfdbfe;
            background: #f8fbff;
            margin-top: 0.7rem;
            margin-bottom: 0.7rem;
        }

        .workflow-active {
            border-left: 7px solid #22c55e;
        }

        .workflow-inactive {
            border-left: 7px solid #f59e0b;
        }

        .workflow-label {
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .workflow-title {
            font-size: 1.15rem;
            color: #0f172a;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .workflow-text {
            font-size: 0.9rem;
            color: #475569;
        }

        .date-check {
            background: #f8fafc;
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-top: 0.5rem;
            margin-bottom: 0.8rem;
        }

        .date-check-good {
            border-left: 7px solid #22c55e;
        }

        .date-check-info {
            border-left: 7px solid #3b82f6;
        }

        .mini-section-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #1d4ed8;
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def zeige_info_karte(titel: str, wert: str | int, beschreibung: str) -> None:
    """Zeigt eine kleine optische Kennzahlenkarte."""
    st.markdown(
        f"""
        <div class="material-card">
            <div class="material-card-title">{titel}</div>
            <div class="material-card-value">{wert}</div>
            <div class="material-card-caption">{beschreibung}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_naechsten_schritt_hinweis(materialtyp_code: str, analyse_code: str) -> None:
    """Zeigt an, was nach dem Speichern als nächster Schritt passiert."""
    if ist_direkter_kulturworkflow(materialtyp_code, analyse_code):
        st.info(
            "Nach dem Speichern wird direkt der unterstützte Kulturworkflow "
            "mit Beurteilung und Befund für dieses Material geöffnet."
        )
        return

    st.caption(
        "Dieses Material wird in der App gespeichert und in den Patientendetails angezeigt. "
        "Ein Kulturworkflow mit Beurteilung und Befund ist aktuell nur für Urin mit der "
        "Analyse 'Allgemeine Bakteriologie' vorhanden."
    )


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


def zeige_kleine_uebersicht(patienten: list[Patient]) -> None:
    """Zeigt kleine Kennzahlen zur aktuellen Materialerfassung."""
    st.markdown('<div class="mini-section-title">Kurzübersicht</div>', unsafe_allow_html=True)

    patienten_spalte, materialtypen_spalte, analysen_spalte = st.columns(3)

    with patienten_spalte:
        zeige_info_karte(
            titel="Verfügbare Patienten",
            wert=len(patienten),
            beschreibung="Patienten, für die Material erfasst werden kann.",
        )

    with materialtypen_spalte:
        zeige_info_karte(
            titel="Materialtypen",
            wert=len(MATERIALTYPEN),
            beschreibung="Auswählbare Materialarten in dieser App.",
        )

    with analysen_spalte:
        zeige_info_karte(
            titel="Analysen",
            wert=len(ANALYSEN),
            beschreibung="Verfügbare Untersuchungen für neues Material.",
        )


def zeige_workflow_status(materialtyp_code: str, analyse_code: str) -> None:
    """Zeigt visuell an, ob der direkte Kulturworkflow aktiv ist."""
    direkter_workflow = ist_direkter_kulturworkflow(materialtyp_code, analyse_code)

    st.markdown('<div class="mini-section-title">Nächster Schritt</div>', unsafe_allow_html=True)

    if direkter_workflow:
        st.markdown(
            """
            <div class="workflow-box workflow-active">
                <div class="workflow-label">Workflow-Status</div>
                <div class="workflow-title">Direkter Kulturworkflow aktiv</div>
                <div class="workflow-text">
                    Nach dem Speichern wird automatisch die Seite
                    <b>Kulturen ablesen</b> geöffnet.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="workflow-box workflow-inactive">
                <div class="workflow-label">Workflow-Status</div>
                <div class="workflow-title">Nur Speicherung ohne direkte Kulturbeurteilung</div>
                <div class="workflow-text">
                    Nach dem Speichern wird das Material in der Patientenakte angezeigt.
                    Die App wechselt danach zurück zur <b>Patientenübersicht</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def zeige_datumskontrolle(abnahmedatum: date, eingangsdatum: date) -> None:
    """Zeigt eine kleine Kontrolle der Zeitspanne zwischen Abnahme und Eingang."""
    tage_bis_eingang = (eingangsdatum - abnahmedatum).days

    if tage_bis_eingang == 0:
        css_klasse = "date-check date-check-good"
        titel = "Materialeingang am gleichen Tag"
        text = "Zwischen Abnahme und Eingang liegt keine Verzögerung."
    elif tage_bis_eingang == 1:
        css_klasse = "date-check date-check-info"
        titel = "Zeit zwischen Abnahme und Eingang: 1 Tag"
        text = "Die Datumsangaben sind gültig."
    else:
        css_klasse = "date-check date-check-info"
        titel = f"Zeit zwischen Abnahme und Eingang: {tage_bis_eingang} Tage"
        text = "Die Datumsangaben sind gültig."

    st.markdown(
        f"""
        <div class="{css_klasse}">
            <div class="workflow-label">Datumskontrolle</div>
            <div class="workflow-title">{titel}</div>
            <div class="workflow-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Rendert die Materialerfassung und bindet die Fachlogik ein."""
    zeige_design_css()

    show_header("Material erfassen")
    st.write("Hier kannst du ein neues Material für einen bestehenden Patienten erfassen.")
    st.info(
        "Reihenfolge: zuerst Patient festlegen, danach Materialtyp und Analyse wählen "
        "und zum Schluss die Datumsangaben prüfen. "
        "Der durchgängige Kulturworkflow mit Beurteilung und Befund ist aktuell nur "
        "für Urin mit der Analyse 'Allgemeine Bakteriologie' vorgesehen."
    )

    repository = PatientenRepository()
    patienten = lade_patienten(repository)

    if patienten is None:
        return

    if not patienten:
        zeige_leermeldung()
        return

    zeige_kleine_uebersicht(patienten)

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

    st.markdown('<div class="mini-section-title">Materialdaten erfassen</div>', unsafe_allow_html=True)

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
                min_value=abnahmedatum,
                max_value=date.today(),
                format="DD.MM.YYYY",
            )

        zeige_datumskontrolle(abnahmedatum, eingangsdatum)
        zeige_workflow_status(materialtyp_code, analyse_code)
        zeige_naechsten_schritt_hinweis(materialtyp_code, analyse_code)

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