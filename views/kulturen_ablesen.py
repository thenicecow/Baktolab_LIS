"""Streamlit-Seite fuer die Funktion ``Kulturen ablesen`` mit speicherbarer Eingabemaske."""

from __future__ import annotations

import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_patient_label,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import (
    hole_kulturdaten_oder_standard,
    ist_material_fuer_kulturen_ablesen_unterstuetzt,
    lade_materialkontext_fuer_kulturen_ablesen,
    speichere_kulturdaten_fuer_material,
)
from functions.kulturen.ansicht import (
    KEIN_WACHSTUM_OPTION,
    baue_formularschluessel,
    baue_kulturdaten_aus_formularvorschau,
    hat_verfuegbare_keimzahl_codes,
    hole_wachstum,
    hole_wachstumsoption_label,
    hole_wachstumsoptionen,
    initialisiere_formularzustand,
    zeige_beurteilung,
    zeige_keimeingabe,
    zeige_vorschau,
)
from functions.kulturen.beurteilung import (
    UrinBeurteilung,
    beurteile_urin_allgemeine_bakteriologie,
)
from functions.kulturen.navigation import (
    aktiviere_befund,
    aktiviere_kulturen_ablesen,
    deaktiviere_befund,
    deaktiviere_kulturen_ablesen,
    hat_gueltige_befund_route,
    ist_befund_aktiv,
)
from functions.patienten.navigation import aktiviere_patientendetailansicht
from persistenz import PatientenRepository
from ui.header import show_header
from views.befund import main as rendere_befundansicht


PATIENTENAUSWAHL_SCHLUESSEL = "kulturen_ablesen_patientenauswahl_patient_id"
PATIENTENAUSWAHL_MATERIALKONTEXT_SCHLUESSEL = (
    "kulturen_ablesen_patientenauswahl_material_id"
)


def zeige_seitenstil() -> None:
    """Fuegt kleine visuelle Verbesserungen fuer Karten und Ablaufgrafik hinzu."""
    st.markdown(
        """
<style>
.kultur-karte {
    border: 1px solid rgba(49, 51, 63, 0.18);
    border-radius: 14px;
    padding: 1rem;
    min-height: 145px;
    background: rgba(250, 250, 250, 0.65);
}

.kultur-icon {
    font-size: 2rem;
    line-height: 1;
    margin-bottom: 0.35rem;
}

.kultur-karten-titel {
    font-weight: 700;
    font-size: 1rem;
    margin-bottom: 0.25rem;
}

.kultur-karten-text {
    font-size: 0.95rem;
    margin-bottom: 0.25rem;
}

.kultur-karten-caption {
    color: rgba(49, 51, 63, 0.65);
    font-size: 0.82rem;
}

.workflow-box {
    border: 1px solid rgba(49, 51, 63, 0.16);
    border-radius: 16px;
    padding: 1rem 0.75rem;
    text-align: center;
    background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,247,250,0.95));
    min-height: 155px;
}

.workflow-icon {
    font-size: 2rem;
    margin-bottom: 0.3rem;
}

.workflow-number {
    display: inline-block;
    border-radius: 999px;
    border: 1px solid rgba(49, 51, 63, 0.2);
    padding: 0.12rem 0.55rem;
    font-size: 0.78rem;
    margin-bottom: 0.45rem;
}

.workflow-title {
    font-weight: 700;
    margin-bottom: 0.25rem;
}

.workflow-text {
    color: rgba(49, 51, 63, 0.7);
    font-size: 0.85rem;
}

.status-chip {
    display: inline-block;
    border: 1px solid rgba(49, 51, 63, 0.18);
    border-radius: 999px;
    padding: 0.25rem 0.7rem;
    margin-right: 0.35rem;
    margin-bottom: 0.35rem;
    background: rgba(250,250,250,0.75);
    font-size: 0.88rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def zeige_workflow_grafik() -> None:
    """Zeigt eine kleine grafische Ablaufuebersicht ohne externe Bilddateien."""
    st.subheader("Arbeitsablauf")

    schritt_1, schritt_2, schritt_3, schritt_4 = st.columns(4)

    with schritt_1:
        st.markdown(
            """
<div class="workflow-box">
    <div class="workflow-icon">🧫</div>
    <div class="workflow-number">Schritt 1</div>
    <div class="workflow-title">Wachstum</div>
    <div class="workflow-text">Festlegen, ob Bakterienwachstum vorhanden ist.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with schritt_2:
        st.markdown(
            """
<div class="workflow-box">
    <div class="workflow-icon">🔬</div>
    <div class="workflow-number">Schritt 2</div>
    <div class="workflow-title">Keime</div>
    <div class="workflow-text">Nur bei Wachstum die nachgewiesenen Keime erfassen.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with schritt_3:
        st.markdown(
            """
<div class="workflow-box">
    <div class="workflow-icon">🧪</div>
    <div class="workflow-number">Schritt 3</div>
    <div class="workflow-title">Beurteilung</div>
    <div class="workflow-text">Eingaben validieren und fachlich beurteilen.</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with schritt_4:
        st.markdown(
            """
<div class="workflow-box">
    <div class="workflow-icon">📄</div>
    <div class="workflow-number">Schritt 4</div>
    <div class="workflow-title">Befund</div>
    <div class="workflow-text">Nach gueltiger Beurteilung den Befund oeffnen.</div>
</div>
""",
            unsafe_allow_html=True,
        )


def hole_ausgewaehlte_patienten_id_auswahl() -> str | None:
    """Liest die aktuell im Dropdown gewaehlte Patienten-ID aus dem Session State."""
    patient_id = st.session_state.get(PATIENTENAUSWAHL_SCHLUESSEL)

    if not isinstance(patient_id, str):
        return None

    bereinigt = patient_id.strip()
    return bereinigt or None


def kehre_zur_patientendetailansicht_zurueck() -> None:
    """Kehrt moeglichst in die Detailansicht des aktuell bearbeiteten Patienten zurueck."""
    patient_id = hole_ausgewaehlte_patienten_id_auswahl()

    if patient_id is None:
        try:
            materialkontext = lade_materialkontext_fuer_kulturen_ablesen()
        except Exception:
            materialkontext = None

        if materialkontext is not None:
            patient, _material = materialkontext
            patient_id = patient.id

    deaktiviere_befund()
    deaktiviere_kulturen_ablesen()

    if patient_id is not None and aktiviere_patientendetailansicht(patient_id):
        st.switch_page("views/patientenuebersicht.py")
        return

    st.switch_page("views/patientenuebersicht.py")


def zeige_aktionsleiste() -> None:
    """Rendert die wichtigsten Ruecksprung- und Navigationsaktionen."""
    with st.container(border=True):
        st.markdown("### Navigation")

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


def zeige_kurzanleitung() -> None:
    """Zeigt eine kurze, gut sichtbare Anleitung fuer die Arbeitsschritte."""
    zeige_workflow_grafik()

    with st.expander("Ausfuehrliche Kurzanleitung anzeigen", expanded=False):
        st.markdown(
            """
1. Lege zuerst fest, ob Bakterienwachstum vorliegt oder ob ausdruecklich kein Wachstum vorhanden ist.
2. Erfasse nur dann Keime, wenn Bakterienwachstum vorhanden ist, und bestaetige jede Keimzahl anhand des Referenzbilds.
3. Speichere die Eingabe oder berechne die Beurteilung, sobald alle Angaben vollstaendig sind.
4. Mit 'Validieren und Befund oeffnen' wird der Befund nur nach einer gueltigen Beurteilung geoeffnet.
"""
        )


def zeige_befund_innerhalb_kulturen_ablesen() -> None:
    """Rendert die interne Befundansicht innerhalb der sichtbaren Kulturseite."""
    rendere_befundansicht()


def lade_verfuegbare_patienten() -> list[Patient] | None:
    """Laedt alle bereits erfassten Patienten fuer die Auswahl auf der Seite."""
    repository = PatientenRepository()

    try:
        return repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None


def baue_material_sortierschluessel(material: Material) -> tuple[int, int, float, str]:
    """Erzeugt einen stabilen Sortierschluessel fuer die Auswahl des bevorzugten Materials."""
    return (
        material.eingangsdatum.toordinal(),
        material.abnahmedatum.toordinal(),
        material.erstellt_am.timestamp() if material.erstellt_am is not None else float("-inf"),
        material.id,
    )


def waehle_bevorzugtes_material_fuer_patient(materialien: list[Material]) -> Material | None:
    """Waehlt fuer einen Patienten das zuletzt passende Material fuer Kulturen ablesen aus."""
    unterstuetzte_materialien = [
        material
        for material in materialien
        if ist_material_fuer_kulturen_ablesen_unterstuetzt(material)
    ]

    if not unterstuetzte_materialien:
        return None

    return max(unterstuetzte_materialien, key=baue_material_sortierschluessel)


def initialisiere_patientenauswahl(
    patienten_ids: list[str],
    aktuelle_patient_id: str | None,
    aktuelle_material_id: str | None,
) -> None:
    """Synchronisiert die Dropdown-Auswahl mit einem bestehenden Materialkontext."""
    gespeicherte_materialreferenz = st.session_state.get(
        PATIENTENAUSWAHL_MATERIALKONTEXT_SCHLUESSEL
    )

    if aktuelle_material_id is not None and gespeicherte_materialreferenz != aktuelle_material_id:
        if aktuelle_patient_id is not None and aktuelle_patient_id in patienten_ids:
            st.session_state[PATIENTENAUSWAHL_SCHLUESSEL] = aktuelle_patient_id
        else:
            st.session_state.pop(PATIENTENAUSWAHL_SCHLUESSEL, None)

        st.session_state[PATIENTENAUSWAHL_MATERIALKONTEXT_SCHLUESSEL] = aktuelle_material_id
        return

    ausgewaehlte_patient_id = st.session_state.get(PATIENTENAUSWAHL_SCHLUESSEL)
    if not isinstance(ausgewaehlte_patient_id, str) or ausgewaehlte_patient_id not in patienten_ids:
        if aktuelle_patient_id is not None and aktuelle_patient_id in patienten_ids:
            st.session_state[PATIENTENAUSWAHL_SCHLUESSEL] = aktuelle_patient_id
        else:
            st.session_state.pop(PATIENTENAUSWAHL_SCHLUESSEL, None)

    if aktuelle_material_id is None:
        st.session_state.pop(PATIENTENAUSWAHL_MATERIALKONTEXT_SCHLUESSEL, None)


def zeige_patientenauswahl(
    patienten: list[Patient],
    aktuelle_patient_id: str | None,
    aktuelle_material_id: str | None,
) -> str | None:
    """Rendert das Dropdown fuer alle vorhandenen Patienten und liefert die gewaehlte ID."""
    patienten_nach_id = {patient.id: patient for patient in patienten}
    patienten_ids = list(patienten_nach_id.keys())

    initialisiere_patientenauswahl(
        patienten_ids=patienten_ids,
        aktuelle_patient_id=aktuelle_patient_id,
        aktuelle_material_id=aktuelle_material_id,
    )

    with st.container(border=True):
        st.markdown("### Patient auswaehlen")
        st.caption("Waehle den Patienten, dessen Kulturdaten du ablesen moechtest.")

        st.selectbox(
            "Patient",
            options=patienten_ids,
            index=None,
            key=PATIENTENAUSWAHL_SCHLUESSEL,
            placeholder="Patient auswaehlen",
            format_func=lambda patient_id: formatiere_patient_label(patienten_nach_id[patient_id]),
        )

    return hole_ausgewaehlte_patienten_id_auswahl()


def ermittle_materialkontext_fuer_patientenauswahl(
    patient_id: str,
    aktueller_patient: Patient | None,
    aktuelles_material: Material | None,
) -> tuple[Patient, Material] | None:
    """Laedt zum gewaehlten Patienten den kompatiblen Materialkontext fuer die Seite."""
    if (
        aktueller_patient is not None
        and aktuelles_material is not None
        and patient_id == aktueller_patient.id
    ):
        return aktueller_patient, aktuelles_material

    repository = PatientenRepository()

    try:
        patientenakte = repository.lade_patientenakte_nach_id(patient_id)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der ausgewaehlte Patient konnte nicht geladen werden."
            )
        )
        return None

    if patientenakte is None:
        st.warning("Der ausgewaehlte Patient wurde nicht gefunden.")
        return None

    patient, materialien = patientenakte
    material = waehle_bevorzugtes_material_fuer_patient(materialien)

    if material is None:
        st.info(
            f"Fuer {formatiere_patient_label(patient)} ist noch kein passendes Material "
            "fuer 'Kulturen ablesen' erfasst."
        )
        return None

    if aktuelles_material is None or aktuelles_material.id != material.id:
        if not aktiviere_kulturen_ablesen(material.id):
            st.error("Das passende Material konnte nicht fuer 'Kulturen ablesen' aktiviert werden.")
            return None

        st.rerun()

    return patient, material


def zeige_materialkontext(patient: Patient, material: Material) -> None:
    """Zeigt den aktuell verwendeten Patienten- und Materialkontext uebersichtlich an."""
    st.subheader("Aktueller Fall")

    patient_spalte, material_spalte, analyse_spalte = st.columns(3)

    with patient_spalte:
        st.markdown(
            f"""
<div class="kultur-karte">
    <div class="kultur-icon">👤</div>
    <div class="kultur-karten-titel">Patient</div>
    <div class="kultur-karten-text">{formatiere_patient_label(patient)}</div>
    <div class="kultur-karten-caption">Patienten-ID: {patient.id}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with material_spalte:
        st.markdown(
            f"""
<div class="kultur-karte">
    <div class="kultur-icon">🧫</div>
    <div class="kultur-karten-titel">Material</div>
    <div class="kultur-karten-text">{loese_materialtyp_label_auf(material.materialtyp_code)}</div>
    <div class="kultur-karten-caption">Material-ID: {material.id}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with analyse_spalte:
        st.markdown(
            f"""
<div class="kultur-karte">
    <div class="kultur-icon">🔬</div>
    <div class="kultur-karten-titel">Analyse</div>
    <div class="kultur-karten-text">{loese_analyse_label_auf(material.klinische_frage_code)}</div>
    <div class="kultur-karten-caption">Eingang: {formatiere_datum(material.eingangsdatum)}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    st.caption("Alle Eingaben auf dieser Seite werden direkt bei diesem Material gespeichert.")


def pruefe_kulturworkflow_voraussetzungen(material: Material) -> bool:
    """Prueft die Mindestvoraussetzungen fuer den Kulturworkflow des Materials."""
    if not ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
        st.warning(
            "Fuer dieses Material ist 'Kulturen ablesen' aktuell nicht freigeschaltet. "
            "Unterstuetzt wird nur Material vom Typ 'Urin' mit der Analyse "
            "'Allgemeine Bakteriologie'. Kehre zur Patientendetailansicht zurueck, "
            "um ein anderes Material auszuwaehlen oder den Fall dort weiterzubearbeiten."
        )
        return False

    if not hat_verfuegbare_keimzahl_codes():
        st.error(
            "Es sind aktuell keine gueltigen Keimzahl-Codes fuer 'Kulturen ablesen' hinterlegt."
        )
        return False

    return True


def lade_und_validiere_materialkontext() -> tuple[Patient, Material] | None:
    """Laedt Patientenliste, Auswahl und den dazu passenden Materialkontext der Seite."""
    patienten = lade_verfuegbare_patienten()
    if patienten is None:
        return None

    if not patienten:
        st.info("Es sind noch keine Patienten erfasst. Bitte erfasse zuerst einen Patienten.")
        return None

    try:
        aktueller_materialkontext = lade_materialkontext_fuer_kulturen_ablesen()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der aktuelle Materialkontext konnte nicht geladen werden."
            )
        )
        return None

    aktueller_patient: Patient | None = None
    aktuelles_material: Material | None = None

    if aktueller_materialkontext is not None:
        aktueller_patient, aktuelles_material = aktueller_materialkontext

    ausgewaehlte_patient_id = zeige_patientenauswahl(
        patienten=patienten,
        aktuelle_patient_id=aktueller_patient.id if aktueller_patient is not None else None,
        aktuelle_material_id=aktuelles_material.id if aktuelles_material is not None else None,
    )

    if ausgewaehlte_patient_id is None:
        st.info("Bitte waehle einen Patienten aus, um mit 'Kulturen ablesen' zu arbeiten.")
        return None

    materialkontext = ermittle_materialkontext_fuer_patientenauswahl(
        patient_id=ausgewaehlte_patient_id,
        aktueller_patient=aktueller_patient,
        aktuelles_material=aktuelles_material,
    )
    if materialkontext is None:
        return None

    patient, material = materialkontext
    zeige_materialkontext(patient, material)

    if not pruefe_kulturworkflow_voraussetzungen(material):
        return None

    return patient, material


def hole_gespeicherte_beurteilung(material: Material) -> UrinBeurteilung | None:
    """Liefert eine vorhandene, gespeicherte Beurteilung fuer das Material."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if not kulturdaten.beurteilung:
        return None

    beurteilung = beurteile_urin_allgemeine_bakteriologie(kulturdaten)

    if beurteilung.ist_gueltig and beurteilung.gesamtbeurteilung:
        return beurteilung

    return UrinBeurteilung(
        gesamtbeurteilung=kulturdaten.beurteilung,
        ist_gueltig=True,
        keimbeurteilungen=[],
        hinweise=["Die gespeicherte Gesamtbeurteilung konnte nur vereinfacht angezeigt werden."],
    )


def speichere_kulturdaten(material: Material) -> bool:
    """Speichert die aktuell erfassten Kulturdaten ohne berechnete Beurteilung."""
    kulturdaten = baue_kulturdaten_aus_formularvorschau(
        material=material,
        beurteilung=None,
    )
    if kulturdaten is None:
        return False

    try:
        speicherergebnis = speichere_kulturdaten_fuer_material(material.id, kulturdaten)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Die Kulturdaten konnten nicht gespeichert werden."
            )
        )
        return False

    if speicherergebnis is None:
        st.error("Die Kulturdaten konnten keinem vorhandenen Material zugeordnet werden.")
        return False

    material.kulturdaten = kulturdaten
    st.success(
        "Die Kulturdaten wurden erfolgreich gespeichert. "
        "Die Beurteilung muss bei geaenderten Eingaben neu berechnet werden."
    )
    return True


def berechne_und_speichere_beurteilung(material: Material) -> UrinBeurteilung | None:
    """Berechnet die Beurteilung, zeigt Eingabefehler an und speichert das Ergebnis."""
    kulturdaten = baue_kulturdaten_aus_formularvorschau(
        material=material,
        beurteilung=None,
    )
    if kulturdaten is None:
        return None

    beurteilung = beurteile_urin_allgemeine_bakteriologie(kulturdaten)

    if not beurteilung.ist_gueltig or not beurteilung.gesamtbeurteilung:
        st.error("Die Beurteilung konnte nicht berechnet werden.")
        for hinweis in beurteilung.hinweise:
            st.warning(hinweis)
        return None

    kulturdaten.beurteilung = beurteilung.gesamtbeurteilung

    try:
        speicherergebnis = speichere_kulturdaten_fuer_material(material.id, kulturdaten)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Die Beurteilung konnte nicht gespeichert werden."
            )
        )
        return None

    if speicherergebnis is None:
        st.error("Die Beurteilung konnte keinem vorhandenen Material zugeordnet werden.")
        return None

    material.kulturdaten = kulturdaten
    st.success("Die Beurteilung wurde erfolgreich berechnet und beim Material gespeichert.")
    return beurteilung


def validiere_und_oeffne_befund(material: Material) -> UrinBeurteilung | None:
    """Berechnet die Beurteilung und oeffnet anschliessend die interne Befundansicht."""
    beurteilung = berechne_und_speichere_beurteilung(material)
    if beurteilung is None:
        return None

    if not aktiviere_befund(material.id):
        st.error("Die Befundansicht konnte nicht geoeffnet werden.")
        return beurteilung

    st.rerun()
    return beurteilung


def zeige_wachstumsstatus(material: Material) -> None:
    """Zeigt eine kleine grafische Statusanzeige zum aktuellen Wachstumsstatus."""
    wachstum_vorhanden = hole_wachstum(material.id)

    if wachstum_vorhanden:
        st.markdown(
            """
<div>
    <span class="status-chip">🧫 Wachstum vorhanden</span>
    <span class="status-chip">🔬 Keime erfassen</span>
    <span class="status-chip">✅ Keimzahl bestaetigen</span>
</div>
""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
<div>
    <span class="status-chip">✅ Kein Wachstum</span>
    <span class="status-chip">🧫 Keine Keime erforderlich</span>
    <span class="status-chip">📄 Direkt beurteilbar</span>
</div>
""",
            unsafe_allow_html=True,
        )


def zeige_kulturdatenformular(material: Material) -> None:
    """Rendert den Eingabebereich fuer Wachstum und Keime."""
    st.subheader("Kulturdaten erfassen")

    with st.container(border=True):
        st.markdown("### 🧫 Bakterienwachstum")
        st.caption("Waehle zuerst aus, ob Bakterienwachstum vorhanden ist.")

        st.radio(
            "Bakterienwachstum",
            options=hole_wachstumsoptionen(),
            key=baue_formularschluessel(material.id, "wachstum"),
            format_func=hole_wachstumsoption_label,
            horizontal=True,
        )

        zeige_wachstumsstatus(material)

        if hole_wachstum(material.id):
            st.info(
                "Bakterienwachstum ist vorhanden. Erfasse nun die nachgewiesenen Keime "
                "und bestaetige die Keimzahl anhand des Referenzbilds."
            )
            zeige_keimeingabe(material.id)
        else:
            st.success(
                "Es ist ausdruecklich 'Kein Wachstum' ausgewaehlt. "
                "Fuer dieses Material muessen keine Keime erfasst werden."
            )
            st.caption(
                "Beim Speichern, Beurteilen und im Befund wird dieser Fall als "
                "'keine Bakterien gewachsen' weitergefuehrt."
            )


def verarbeite_aktionsbuttons(
    material: Material,
    aktuelle_beurteilung: UrinBeurteilung | None,
) -> UrinBeurteilung | None:
    """Verarbeitet Speichern, Beurteilung und Befundoeffnung fuer das aktuelle Material."""
    aktualisierte_beurteilung = aktuelle_beurteilung

    st.subheader("Aktionen")

    with st.container(border=True):
        st.markdown(
            """
<div>
    <span class="status-chip">💾 Speichern</span>
    <span class="status-chip">🧪 Beurteilung berechnen</span>
    <span class="status-chip">📄 Befund oeffnen</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.caption(
            "Speichere zuerst die Kulturdaten oder berechne direkt die Beurteilung. "
            "Der Befund wird erst nach erfolgreicher Validierung geoeffnet."
        )

        button_spalte_links, button_spalte_mitte, button_spalte_rechts = st.columns(3)

        with button_spalte_links:
            if st.button(
                "Kulturdaten speichern",
                type="secondary",
                use_container_width=True,
            ):
                if speichere_kulturdaten(material):
                    aktualisierte_beurteilung = None

        with button_spalte_mitte:
            if st.button(
                "Beurteilung berechnen",
                type="secondary",
                use_container_width=True,
            ):
                berechnete_beurteilung = berechne_und_speichere_beurteilung(material)
                if berechnete_beurteilung is not None:
                    aktualisierte_beurteilung = berechnete_beurteilung

        with button_spalte_rechts:
            if st.button(
                "Validieren und Befund oeffnen",
                type="primary",
                use_container_width=True,
            ):
                berechnete_beurteilung = validiere_und_oeffne_befund(material)
                if berechnete_beurteilung is not None:
                    aktualisierte_beurteilung = berechnete_beurteilung

    return aktualisierte_beurteilung


def zeige_ergebnisbereich(
    material: Material,
    aktuelle_beurteilung: UrinBeurteilung | None,
) -> None:
    """Zeigt Vorschau und Beurteilung uebersichtlich in Tabs."""
    st.subheader("Ergebnis und Kontrolle")

    tab_vorschau, tab_beurteilung = st.tabs(["📋 Vorschau", "🧪 Beurteilung"])

    with tab_vorschau:
        st.caption("Kontrolliere hier die aktuell erfassten Kulturdaten.")
        zeige_vorschau(material.id)

    with tab_beurteilung:
        st.caption("Hier erscheint die berechnete oder gespeicherte Beurteilung.")
        zeige_beurteilung(aktuelle_beurteilung)


def main() -> None:
    """Rendert die Seite ``Kulturen ablesen`` mit speicherbarer Eingabemaske."""
    zeige_seitenstil()

    if hat_gueltige_befund_route():
        zeige_befund_innerhalb_kulturen_ablesen()
        return

    show_header("Kulturen ablesen")

    st.info(
        "Diese Seite ist aktuell nur fuer Urin mit der Analyse "
        "'Allgemeine Bakteriologie' freigeschaltet. Kulturdaten, Beurteilung "
        "und Befund werden nur innerhalb dieses begrenzten Demo-Workflows "
        "unterstuetzt. Andere Materialien oder Analysen werden in der App "
        "dokumentiert, aber nicht ueber diese Seite weiterverarbeitet."
    )

    if ist_befund_aktiv():
        deaktiviere_befund()
        st.warning(
            "Die Befundansicht konnte nicht geoeffnet werden, "
            "weil kein gueltiger Materialkontext vorhanden ist."
        )

    zeige_aktionsleiste()
    st.divider()

    materialkontext = lade_und_validiere_materialkontext()
    if materialkontext is None:
        return

    st.divider()
    zeige_kurzanleitung()

    _patient, material = materialkontext
    initialisiere_formularzustand(material)

    aktuelle_beurteilung = hole_gespeicherte_beurteilung(material)

    st.divider()
    zeige_kulturdatenformular(material)

    aktuelle_beurteilung = verarbeite_aktionsbuttons(material, aktuelle_beurteilung)

    st.divider()
    zeige_ergebnisbereich(material, aktuelle_beurteilung)


main()