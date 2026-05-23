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
    baue_formularschluessel,
    baue_kulturdaten_aus_formularvorschau,
    hat_verfuegbare_keimzahl_codes,
    hole_wachstum,
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


def hole_ausgewaehlte_patienten_id_auswahl() -> str | None:
    """Liest die aktuell im Dropdown gewählte Patienten-ID aus dem Session State."""
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
    with st.expander("Kurzanleitung fuer diese Seite", expanded=True):
        st.markdown(
            """
1. Lege zuerst fest, ob Wachstum vorliegt.
2. Erfasse nur die vorhandenen Keime und bestaetige jede Keimzahl anhand des Referenzbilds.
3. Speichere die Eingabe oder berechne die Beurteilung, sobald alle Angaben vollstaendig sind.
4. Mit 'Validieren und Befund oeffnen' wird der Befund nur nach einer gueltigen Beurteilung geoeffnet.
"""
        )


def zeige_befund_innerhalb_kulturen_ablesen() -> None:
    """Rendert die interne Befundansicht innerhalb der sichtbaren Kulturseite."""
    rendere_befundansicht()


def lade_verfuegbare_patienten() -> list[Patient] | None:
    """Lädt alle bereits erfassten Patienten für die Auswahl auf der Seite."""
    repository = PatientenRepository()

    try:
        return repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None


def baue_material_sortierschluessel(material: Material) -> tuple[int, int, float, str]:
    """Erzeugt einen stabilen Sortierschlüssel für die Auswahl des bevorzugten Materials."""
    return (
        material.eingangsdatum.toordinal(),
        material.abnahmedatum.toordinal(),
        material.erstellt_am.timestamp() if material.erstellt_am is not None else float("-inf"),
        material.id,
    )


def waehle_bevorzugtes_material_fuer_patient(materialien: list[Material]) -> Material | None:
    """Wählt für einen Patienten das zuletzt passende Material für Kulturen ablesen aus."""
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
    """Rendert das Dropdown für alle vorhandenen Patienten und liefert die gewählte ID."""
    patienten_nach_id = {patient.id: patient for patient in patienten}
    patienten_ids = list(patienten_nach_id.keys())

    initialisiere_patientenauswahl(
        patienten_ids=patienten_ids,
        aktuelle_patient_id=aktuelle_patient_id,
        aktuelle_material_id=aktuelle_material_id,
    )

    with st.container(border=True):
        st.markdown("**Patientenauswahl**")
        st.selectbox(
            "Patient",
            options=patienten_ids,
            index=None,
            key=PATIENTENAUSWAHL_SCHLUESSEL,
            placeholder="Patient auswählen",
            format_func=lambda patient_id: formatiere_patient_label(patienten_nach_id[patient_id]),
        )

    return hole_ausgewaehlte_patienten_id_auswahl()


def ermittle_materialkontext_fuer_patientenauswahl(
    patient_id: str,
    aktueller_patient: Patient | None,
    aktuelles_material: Material | None,
) -> tuple[Patient, Material] | None:
    """Lädt zum gewählten Patienten den kompatiblen Materialkontext für die Seite."""
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
                "Der ausgewählte Patient konnte nicht geladen werden."
            )
        )
        return None

    if patientenakte is None:
        st.warning("Der ausgewählte Patient wurde nicht gefunden.")
        return None

    patient, materialien = patientenakte
    material = waehle_bevorzugtes_material_fuer_patient(materialien)

    if material is None:
        st.info(
            f"Für {formatiere_patient_label(patient)} ist noch kein passendes Material "
            "für 'Kulturen ablesen' erfasst."
        )
        return None

    if aktuelles_material is None or aktuelles_material.id != material.id:
        if not aktiviere_kulturen_ablesen(material.id):
            st.error("Das passende Material konnte nicht für 'Kulturen ablesen' aktiviert werden.")
            return None

        st.rerun()

    return patient, material


def zeige_materialkontext(patient: Patient, material: Material) -> None:
    """Zeigt den aktuell verwendeten Patienten- und Materialkontext an."""
    st.caption(f"Aktuelle Materialreferenz: {material.id}")

    with st.container(border=True):
        st.markdown("**Aktuelles Material**")
        st.write(f"Patient: {formatiere_patient_label(patient)}")
        st.write(f"Material-ID: {material.id}")
        st.write(f"Materialtyp: {loese_materialtyp_label_auf(material.materialtyp_code)}")
        st.write(f"Analyse: {loese_analyse_label_auf(material.klinische_frage_code)}")
        st.write(f"Eingangsdatum: {formatiere_datum(material.eingangsdatum)}")
        st.caption(
            "Alle Eingaben auf dieser Seite werden direkt bei diesem Material gespeichert."
        )


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
    """Lädt Patientenliste, Auswahl und den dazu passenden Materialkontext der Seite."""
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
        st.info("Bitte wähle einen Patienten aus, um mit 'Kulturen ablesen' zu arbeiten.")
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
        "Die Beurteilung muss bei geänderten Eingaben neu berechnet werden."
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


def zeige_kulturdatenformular(material: Material) -> None:
    """Rendert den Eingabebereich fuer Wachstum und Keime."""
    st.subheader("Kulturdaten")
    st.radio(
        "Wachstum",
        options=("ja", "nein"),
        key=baue_formularschluessel(material.id, "wachstum"),
        horizontal=True,
    )

    if hole_wachstum(material.id):
        st.caption(
            "Erfasse nur die vorhandenen Keime. Jede ausgewaehlte Keimzahl muss vor "
            "dem Speichern oder Beurteilen anhand des Referenzbilds bestaetigt werden."
        )
        zeige_keimeingabe(material.id)
    else:
        st.caption(
            "Bei 'nein' werden keine Keime erfasst. Die Beurteilung fuehrt dann zu "
            "'Kein Wachstum'."
        )


def verarbeite_aktionsbuttons(
    material: Material,
    aktuelle_beurteilung: UrinBeurteilung | None,
) -> UrinBeurteilung | None:
    """Verarbeitet Speichern, Beurteilung und Befundoeffnung fuer das aktuelle Material."""
    aktualisierte_beurteilung = aktuelle_beurteilung
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


def main() -> None:
    """Rendert die Seite ``Kulturen ablesen`` mit speicherbarer Eingabemaske."""
    if hat_gueltige_befund_route():
        zeige_befund_innerhalb_kulturen_ablesen()
        return

    show_header("Kulturen ablesen")
    st.info(
        "Diese Seite ist aktuell nur für Urin mit der Analyse "
        "'Allgemeine Bakteriologie' freigeschaltet. Kulturdaten, Beurteilung "
        "und Befund werden nur innerhalb dieses begrenzten Demo-Workflows "
        "unterstützt. Andere Materialien oder Analysen werden in der App "
        "dokumentiert, aber nicht über diese Seite weiterverarbeitet."
    )

    if ist_befund_aktiv():
        deaktiviere_befund()
        st.warning(
            "Die Befundansicht konnte nicht geoeffnet werden, "
            "weil kein gueltiger Materialkontext vorhanden ist."
        )

    zeige_aktionsleiste()

    materialkontext = lade_und_validiere_materialkontext()
    if materialkontext is None:
        return

    zeige_kurzanleitung()

    _patient, material = materialkontext
    initialisiere_formularzustand(material)

    aktuelle_beurteilung = hole_gespeicherte_beurteilung(material)

    zeige_kulturdatenformular(material)
    aktuelle_beurteilung = verarbeite_aktionsbuttons(material, aktuelle_beurteilung)
    zeige_vorschau(material.id)
    zeige_beurteilung(aktuelle_beurteilung)


main()