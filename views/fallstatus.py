"""Streamlit-Seite für den aktuellen Bearbeitungsstand aller Patientenfaelle."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_patient_label,
    formatiere_zeitpunkt,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import ist_material_fuer_kulturen_ablesen_unterstuetzt
from functions.kulturen.navigation import aktiviere_kulturen_ablesen
from functions.patienten.detail import merke_patient_id_fuer_material_erfassen
from functions.patienten.navigation import aktiviere_patientendetailansicht
from persistenz import PatientenRepository
from ui.header import show_header


FILTER_ALLE = "Alle Fälle"
FILTER_OFFEN = "Offene Fälle"
FILTER_OHNE_MATERIAL = "Ohne Material"
FILTER_KULTUR_OFFEN = "Kultur offen"
FILTER_BEFUND_BEREIT = "Befund bereit"
FILTER_ABGESCHLOSSEN = "Abgeschlossen"

FALLSTATUS_FILTER_SCHLUESSEL = "fallstatus_filter"
FALLSTATUS_SUCHE_SCHLUESSEL = "fallstatus_suche"


@dataclass(frozen=True)
class Fallstatus:
    """Beschreibt den aktuellen Workflow-Stand eines Patientenfalls."""

    patient: Patient
    materialien: list[Material]
    material_erfasst: bool
    kultur_bearbeitet: bool
    befund_bereit: bool
    unterstuetztes_material_vorhanden: bool
    bevorzugtes_material: Material | None
    naechster_schritt: str
    statusgruppe: str


def zeige_seitenstil() -> None:
    """Fuegt lokale Styles fuer die Fallstatus-Seite hinzu."""
    st.markdown(
        """
        <style>
        .status-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            min-height: 125px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
        }

        .status-card-title {
            color: #1d4ed8;
            font-size: 0.95rem;
            font-weight: 850;
            margin-bottom: 0.25rem;
        }

        .status-card-value {
            color: #0f172a;
            font-size: 1.75rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 0.25rem;
        }

        .status-card-text {
            color: #475569;
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .fall-card {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
        }

        .fall-name {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.15rem;
        }

        .fall-subtitle {
            color: #64748b;
            font-size: 0.84rem;
            margin-bottom: 0.5rem;
        }

        .status-chip {
            display: inline-block;
            border-radius: 999px;
            padding: 0.28rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 800;
            margin: 0.14rem 0.2rem 0.14rem 0;
            white-space: nowrap;
        }

        .chip-patient {
            background: #ede9fe;
            color: #5b21b6;
            border: 1px solid #c4b5fd;
        }

        .chip-material {
            background: #ccfbf1;
            color: #115e59;
            border: 1px solid #5eead4;
        }

        .chip-kultur {
            background: #ecfccb;
            color: #3f6212;
            border: 1px solid #bef264;
        }

        .chip-befund {
            background: #dcfce7;
            color: #14532d;
            border: 1px solid #86efac;
        }

        .chip-offen {
            background: #f8fafc;
            color: #64748b;
            border: 1px solid #cbd5e1;
        }

        .next-step-box {
            background: #f8fbff;
            border: 1px solid #dbeafe;
            border-left: 6px solid #2563eb;
            border-radius: 14px;
            padding: 0.75rem 0.85rem;
            color: #334155;
            font-size: 0.88rem;
            line-height: 1.4;
        }

        .legend-box {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def lade_alle_patientenakten() -> list[tuple[Patient, list[Material]]] | None:
    """Laedt alle Patienten mit vollstaendigen Materiallisten."""
    repository = PatientenRepository()

    try:
        patienten = repository.lade_alle_patienten()
    except Exception:
        st.error(baue_technische_fehlernachricht("Die Patienten konnten nicht geladen werden."))
        return None

    patientenakten: list[tuple[Patient, list[Material]]] = []

    for patient in patienten:
        try:
            patientenakte = repository.lade_patientenakte_nach_id(patient.id)
        except Exception:
            st.warning(
                f"Die Patientenakte von {patient.vorname} {patient.nachname} "
                "konnte nicht vollständig geladen werden."
            )
            patientenakten.append((patient, []))
            continue

        if patientenakte is None:
            patientenakten.append((patient, []))
            continue

        patient_aus_akte, materialien = patientenakte
        patientenakten.append((patient_aus_akte, materialien))

    return patientenakten


def hat_kulturdaten(material: Material) -> bool:
    """Prueft, ob bei einem Material bereits Kulturdaten vorhanden sind."""
    kulturdaten = material.kulturdaten

    if kulturdaten.wachstum is not None:
        return True

    if kulturdaten.keime:
        return True

    if kulturdaten.beurteilung:
        return True

    return False


def hat_befund_bereit(material: Material) -> bool:
    """Prueft, ob ein Material eine gespeicherte Beurteilung besitzt."""
    return bool(material.kulturdaten.beurteilung)


def waehle_bevorzugtes_material(materialien: list[Material]) -> Material | None:
    """Waehlt ein sinnvolles Material fuer direkte Aktionen aus."""
    if not materialien:
        return None

    befund_materialien = [
        material for material in materialien if hat_befund_bereit(material)
    ]
    if befund_materialien:
        return sortiere_materialien_nach_datum(befund_materialien)[0]

    kultur_materialien = [
        material for material in materialien if hat_kulturdaten(material)
    ]
    if kultur_materialien:
        return sortiere_materialien_nach_datum(kultur_materialien)[0]

    unterstuetzte_materialien = [
        material
        for material in materialien
        if ist_material_fuer_kulturen_ablesen_unterstuetzt(material)
    ]
    if unterstuetzte_materialien:
        return sortiere_materialien_nach_datum(unterstuetzte_materialien)[0]

    return sortiere_materialien_nach_datum(materialien)[0]


def sortiere_materialien_nach_datum(materialien: list[Material]) -> list[Material]:
    """Sortiert Materialien absteigend nach Eingangsdatum, Abnahmedatum und Erstellzeit."""
    return sorted(
        materialien,
        key=lambda material: (
            material.eingangsdatum.toordinal(),
            material.abnahmedatum.toordinal(),
            material.erstellt_am.timestamp() if material.erstellt_am is not None else float("-inf"),
            material.id,
        ),
        reverse=True,
    )


def ermittle_naechsten_schritt(
    materialien: list[Material],
    befund_bereit: bool,
    kultur_bearbeitet: bool,
    unterstuetztes_material_vorhanden: bool,
) -> tuple[str, str]:
    """Ermittelt den naechsten sinnvollen Schritt und die Statusgruppe."""
    if not materialien:
        return "Material erfassen", FILTER_OHNE_MATERIAL

    if befund_bereit:
        return "Befund prüfen / Fall abgeschlossen", FILTER_ABGESCHLOSSEN

    if unterstuetztes_material_vorhanden and not befund_bereit:
        if kultur_bearbeitet:
            return "Beurteilung prüfen und Befund öffnen", FILTER_KULTUR_OFFEN

        return "Kulturen ablesen", FILTER_KULTUR_OFFEN

    return "In Patientendetails prüfen", FILTER_OFFEN


def baue_fallstatus(patient: Patient, materialien: list[Material]) -> Fallstatus:
    """Baut den Workflowstatus fuer einen Patienten."""
    material_erfasst = len(materialien) > 0
    kultur_bearbeitet = any(hat_kulturdaten(material) for material in materialien)
    befund_bereit = any(hat_befund_bereit(material) for material in materialien)
    unterstuetztes_material_vorhanden = any(
        ist_material_fuer_kulturen_ablesen_unterstuetzt(material)
        for material in materialien
    )
    bevorzugtes_material = waehle_bevorzugtes_material(materialien)

    naechster_schritt, statusgruppe = ermittle_naechsten_schritt(
        materialien=materialien,
        befund_bereit=befund_bereit,
        kultur_bearbeitet=kultur_bearbeitet,
        unterstuetztes_material_vorhanden=unterstuetztes_material_vorhanden,
    )

    return Fallstatus(
        patient=patient,
        materialien=materialien,
        material_erfasst=material_erfasst,
        kultur_bearbeitet=kultur_bearbeitet,
        befund_bereit=befund_bereit,
        unterstuetztes_material_vorhanden=unterstuetztes_material_vorhanden,
        bevorzugtes_material=bevorzugtes_material,
        naechster_schritt=naechster_schritt,
        statusgruppe=statusgruppe,
    )


def baue_statusliste(patientenakten: list[tuple[Patient, list[Material]]]) -> list[Fallstatus]:
    """Baut die Statusliste fuer alle Patientenakten."""
    return [
        baue_fallstatus(patient, materialien)
        for patient, materialien in patientenakten
    ]


def filtere_statusliste(
    statusliste: list[Fallstatus],
    suchtext: str,
    statusfilter: str,
) -> list[Fallstatus]:
    """Filtert die Statusliste nach Suchtext und Statusfilter."""
    suchtext_bereinigt = suchtext.strip().casefold()

    gefiltert: list[Fallstatus] = []

    for status in statusliste:
        patient = status.patient

        if suchtext_bereinigt:
            suchfelder = (
                patient.vorname,
                patient.nachname,
                patient.id,
                patient.geschlecht,
            )
            if not any(suchtext_bereinigt in str(wert).casefold() for wert in suchfelder):
                continue

        if statusfilter == FILTER_OHNE_MATERIAL and status.material_erfasst:
            continue

        if statusfilter == FILTER_KULTUR_OFFEN:
            if not status.material_erfasst or status.befund_bereit:
                continue

        if statusfilter == FILTER_BEFUND_BEREIT and not status.befund_bereit:
            continue

        if statusfilter == FILTER_ABGESCHLOSSEN and not status.befund_bereit:
            continue

        if statusfilter == FILTER_OFFEN and status.befund_bereit:
            continue

        gefiltert.append(status)

    return gefiltert


def zaehle_materialien(statusliste: list[Fallstatus]) -> int:
    """Zaehlt alle Materialien in der Statusliste."""
    return sum(len(status.materialien) for status in statusliste)


def zaehle_status(statusliste: list[Fallstatus]) -> dict[str, int]:
    """Berechnet Kennzahlen fuer die Statusuebersicht."""
    return {
        "patienten": len(statusliste),
        "materialien": zaehle_materialien(statusliste),
        "mit_material": sum(1 for status in statusliste if status.material_erfasst),
        "kultur_bearbeitet": sum(1 for status in statusliste if status.kultur_bearbeitet),
        "befund_bereit": sum(1 for status in statusliste if status.befund_bereit),
        "offen": sum(1 for status in statusliste if not status.befund_bereit),
    }


def zeige_kennzahlkarte(titel: str, wert: int, beschreibung: str) -> None:
    """Zeigt eine einzelne Kennzahlenkarte."""
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-title">{escape(titel)}</div>
            <div class="status-card-value">{wert}</div>
            <div class="status-card-text">{escape(beschreibung)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_kennzahlen(statusliste: list[Fallstatus]) -> None:
    """Zeigt die wichtigsten Kennzahlen."""
    zahlen = zaehle_status(statusliste)

    spalte_1, spalte_2, spalte_3, spalte_4, spalte_5 = st.columns(5)

    with spalte_1:
        zeige_kennzahlkarte(
            "Patienten",
            zahlen["patienten"],
            "Alle aktuell geladenen Patienten.",
        )

    with spalte_2:
        zeige_kennzahlkarte(
            "Materialien",
            zahlen["materialien"],
            "Alle Materialien aus den Patientenakten.",
        )

    with spalte_3:
        zeige_kennzahlkarte(
            "Mit Material",
            zahlen["mit_material"],
            "Patienten mit mindestens einem Material.",
        )

    with spalte_4:
        zeige_kennzahlkarte(
            "Kultur bearbeitet",
            zahlen["kultur_bearbeitet"],
            "Fälle mit Wachstum, Keim oder Beurteilung.",
        )

    with spalte_5:
        zeige_kennzahlkarte(
            "Befund bereit",
            zahlen["befund_bereit"],
            "Fälle mit gespeicherter Beurteilung.",
        )


def zeige_legende() -> None:
    """Zeigt die Statuslegende."""
    st.markdown(
        """
        <div class="legend-box">
            <span class="status-chip chip-patient">✓ Patient erfasst</span>
            <span class="status-chip chip-material">✓ Material erfasst</span>
            <span class="status-chip chip-kultur">✓ Kultur bearbeitet</span>
            <span class="status-chip chip-befund">✓ Befund bereit</span>
            <span class="status-chip chip-offen">○ offen</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_filterbereich() -> tuple[str, str]:
    """Zeigt Suche und Statusfilter."""
    with st.container(border=True):
        st.markdown("### Filter")

        such_spalte, filter_spalte = st.columns((2, 1))

        with such_spalte:
            suchtext = st.text_input(
                "Suche nach Patient, ID oder Geschlecht",
                key=FALLSTATUS_SUCHE_SCHLUESSEL,
            )

        with filter_spalte:
            statusfilter = st.selectbox(
                "Status",
                options=[
                    FILTER_ALLE,
                    FILTER_OFFEN,
                    FILTER_OHNE_MATERIAL,
                    FILTER_KULTUR_OFFEN,
                    FILTER_BEFUND_BEREIT,
                    FILTER_ABGESCHLOSSEN,
                ],
                key=FALLSTATUS_FILTER_SCHLUESSEL,
            )

    return suchtext, statusfilter


def status_chip(text: str, aktiv: bool, css_klasse: str) -> str:
    """Erzeugt einen Statuschip."""
    if aktiv:
        return f'<span class="status-chip {css_klasse}">✓ {escape(text)}</span>'

    return f'<span class="status-chip chip-offen">○ {escape(text)}</span>'


def beschreibe_bevorzugtes_material(material: Material | None) -> str:
    """Erzeugt eine kurze Materialbeschreibung."""
    if material is None:
        return "Kein Material vorhanden."

    materialtyp = loese_materialtyp_label_auf(material.materialtyp_code)
    analyse = loese_analyse_label_auf(material.klinische_frage_code)

    return (
        f"{materialtyp} · {analyse} · Eingang: "
        f"{formatiere_datum(material.eingangsdatum)}"
    )


def oeffne_details(patient_id: str) -> None:
    """Oeffnet die Patientendetailansicht innerhalb der Patientenuebersicht."""
    if not aktiviere_patientendetailansicht(patient_id):
        st.error("Die Patientendetailansicht konnte nicht geöffnet werden.")
        return

    st.switch_page("views/patientenuebersicht.py")


def oeffne_materialerfassung(patient_id: str) -> None:
    """Oeffnet die Materialerfassung fuer einen Patienten."""
    merke_patient_id_fuer_material_erfassen(patient_id)
    st.switch_page("views/material_erfassen.py")


def oeffne_kulturseite(material: Material | None) -> None:
    """Oeffnet Kulturen ablesen fuer ein unterstuetztes Material."""
    if material is None:
        st.warning("Für diesen Patienten ist kein geeignetes Material vorhanden.")
        return

    if not ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
        st.warning(
            "Für dieses Material ist der Kulturworkflow aktuell nicht freigeschaltet."
        )
        return

    if not aktiviere_kulturen_ablesen(material.id):
        st.error("Die Seite 'Kulturen ablesen' konnte nicht geöffnet werden.")
        return

    st.switch_page("views/kulturen_ablesen.py")


def zeige_fallkarte(status: Fallstatus) -> None:
    """Zeigt einen Patientenfall als Statuskarte."""
    patient = status.patient
    material = status.bevozugtes_material if hasattr(status, "bevozugtes_material") else status.bevorzugtes_material

    with st.container(border=True):
        kopf_spalte, status_spalte, schritt_spalte, aktion_spalte = st.columns(
            (2.3, 2.6, 2.0, 2.0)
        )

        with kopf_spalte:
            st.markdown(
                f"""
                <div class="fall-name">👤 {escape(patient.vorname)} {escape(patient.nachname)}</div>
                <div class="fall-subtitle">
                    Geburtsdatum: {escape(formatiere_datum(patient.geburtsdatum))}<br>
                    Geschlecht: {escape(patient.geschlecht)}<br>
                    Erstellt: {escape(formatiere_zeitpunkt(patient.erstellt_am))}
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(f"Patienten-ID: {patient.id}")

        with status_spalte:
            chips = [
                status_chip("Patient erfasst", True, "chip-patient"),
                status_chip("Material erfasst", status.material_erfasst, "chip-material"),
                status_chip("Kultur bearbeitet", status.kultur_bearbeitet, "chip-kultur"),
                status_chip("Befund bereit", status.befund_bereit, "chip-befund"),
            ]

            st.markdown("".join(chips), unsafe_allow_html=True)
            st.caption(beschreibe_bevorzugtes_material(material))

        with schritt_spalte:
            st.markdown(
                f"""
                <div class="next-step-box">
                    <strong>Nächster Schritt</strong><br>
                    {escape(status.naechster_schritt)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with aktion_spalte:
            if st.button(
                "Details öffnen",
                key=f"fallstatus_details_{patient.id}",
                use_container_width=True,
            ):
                oeffne_details(patient.id)

            if not status.material_erfasst:
                if st.button(
                    "Material erfassen",
                    key=f"fallstatus_material_{patient.id}",
                    use_container_width=True,
                    type="primary",
                ):
                    oeffne_materialerfassung(patient.id)
            elif status.unterstuetztes_material_vorhanden and not status.befund_bereit:
                if st.button(
                    "Kulturen öffnen",
                    key=f"fallstatus_kultur_{patient.id}",
                    use_container_width=True,
                    type="primary",
                ):
                    oeffne_kulturseite(material)
            else:
                st.caption("Weitere Bearbeitung über Details.")


def zeige_statusliste(statusliste: list[Fallstatus]) -> None:
    """Zeigt alle gefilterten Fallstatuskarten."""
    st.markdown("### Fallliste")

    if not statusliste:
        st.info("Für die gesetzten Filter wurden keine Fälle gefunden.")
        return

    for status in statusliste:
        zeige_fallkarte(status)


def main() -> None:
    """Rendert die Fallstatus-Seite."""
    zeige_seitenstil()

    show_header("Fallstatus")

    st.write(
        "Diese Seite zeigt den aktuellen Bearbeitungsstand aller Patientenfälle. "
        "Sie nutzt die vollständigen Patientenakten inklusive Materialien und gespeicherter Kulturdaten."
    )

    patientenakten = lade_alle_patientenakten()
    if patientenakten is None:
        return

    if not patientenakten:
        st.info("Es sind noch keine Patienten erfasst.")
        st.page_link(
            "views/patienten_erfassen.py",
            label="Patient erfassen",
            icon=":material/person_add:",
        )
        return

    statusliste = baue_statusliste(patientenakten)

    zeige_kennzahlen(statusliste)
    st.divider()
    zeige_legende()

    suchtext, statusfilter = zeige_filterbereich()
    gefilterte_statusliste = filtere_statusliste(
        statusliste=statusliste,
        suchtext=suchtext,
        statusfilter=statusfilter,
    )

    st.caption(
        f"Angezeigte Fälle: {len(gefilterte_statusliste)} von {len(statusliste)}"
    )

    st.divider()
    zeige_statusliste(gefilterte_statusliste)


main()