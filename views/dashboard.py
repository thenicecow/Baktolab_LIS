"""Streamlit-Seite für das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    DASHBOARD_HINWEIS,
    DASHBOARD_UNTERTITEL,
    DashboardAktionskarte,
    hole_akzentfarbe_fuer_titel,
    hole_anzeige_name,
    hole_anzeigetext_fuer_titel,
    hole_hauptaktionskarten,
    hole_nebenaktionskarten,
)
from ui.header import show_header


STANDARD_AKZENTFARBE = "#2563EB"


def zeige_dashboard_design_css() -> None:
    """Ergaenzt lokale Styles fuer zusaetzliche Dashboard-Bereiche."""
    st.markdown(
        """
        <style>
        .workflow-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            min-height: 150px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
        }

        .workflow-step-number {
            display: inline-block;
            background: #2563eb;
            color: white;
            font-weight: 800;
            border-radius: 999px;
            width: 2rem;
            height: 2rem;
            line-height: 2rem;
            text-align: center;
            margin-bottom: 0.55rem;
        }

        .workflow-card-title {
            color: #1d4ed8;
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .workflow-card-text {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .dashboard-info-box {
            background: #f8fbff;
            border: 1px solid #dbeafe;
            border-left: 7px solid #2563eb;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .dashboard-info-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 1.05rem;
            margin-bottom: 0.35rem;
        }

        .dashboard-info-text {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .status-chip {
            display: inline-block;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 750;
            margin: 0.2rem 0.25rem 0.2rem 0;
        }

        .chip-blue {
            background: #dbeafe;
            color: #1e3a8a;
        }

        .chip-green {
            background: #dcfce7;
            color: #14532d;
        }

        .chip-orange {
            background: #ffedd5;
            color: #7c2d12;
        }

        .chip-gray {
            background: #f1f5f9;
            color: #334155;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def zeige_workflow_schritt(
    nummer: int,
    titel: str,
    beschreibung: str,
) -> None:
    """Rendert eine einzelne Workflow-Karte."""
    st.markdown(
        f"""
        <div class="workflow-card">
            <div class="workflow-step-number">{nummer}</div>
            <div class="workflow-card-title">{titel}</div>
            <div class="workflow-card-text">{beschreibung}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_workflow_uebersicht() -> None:
    """Zeigt einen stabilen, fachlichen Workflow-Ueberblick ohne fehleranfaellige Zaehllogik."""
    st.markdown("### Workflow-Übersicht")

    spalte_1, spalte_2, spalte_3, spalte_4 = st.columns(4)

    with spalte_1:
        zeige_workflow_schritt(
            nummer=1,
            titel="Patient erfassen",
            beschreibung=(
                "Stammdaten aufnehmen und eine eindeutige Patientenakte erstellen."
            ),
        )

    with spalte_2:
        zeige_workflow_schritt(
            nummer=2,
            titel="Material erfassen",
            beschreibung=(
                "Probe einem Patienten zuordnen, Materialtyp wählen und Datumsangaben prüfen."
            ),
        )

    with spalte_3:
        zeige_workflow_schritt(
            nummer=3,
            titel="Kulturen ablesen",
            beschreibung=(
                "Wachstum, Keim, Keimzahl und Rolle erfassen und fachlich beurteilen."
            ),
        )

    with spalte_4:
        zeige_workflow_schritt(
            nummer=4,
            titel="Befund exportieren",
            beschreibung=(
                "Validierte Kulturdaten prüfen und den mikrobiologischen Befund als PDF herunterladen."
            ),
        )


def zeige_naechster_schritt_hilfe() -> None:
    """Zeigt eine klare Orientierung, was im Laborworkflow als Naechstes zu tun ist."""
    st.markdown(
        """
        <div class="dashboard-info-box">
            <div class="dashboard-info-title">Nächster sinnvoller Schritt</div>
            <div class="dashboard-info-text">
                Starte bei neuen Fällen mit <b>Patient erfassen</b>. Wenn der Patient bereits vorhanden ist,
                gehe direkt zu <b>Material erfassen</b>. Für Urin mit der Analyse
                <b>Allgemeine Bakteriologie</b> öffnet sich anschliessend der Kulturworkflow automatisch.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_status_legende() -> None:
    """Zeigt eine einfache Status-Legende fuer den Workflow."""
    st.markdown("### Status-Legende")

    with st.container(border=True):
        st.markdown(
            """
            <span class="status-chip chip-gray">Patient erfasst</span>
            <span class="status-chip chip-blue">Material aufgenommen</span>
            <span class="status-chip chip-orange">Kultur in Bearbeitung</span>
            <span class="status-chip chip-green">Befund validiert</span>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "Die Legende dient als Orientierung für den Ablauf. "
            "Die tatsächliche Bearbeitung erfolgt über die Hauptaktionen unten."
        )


def zeige_hauptaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine grosse Aktionskarte für die priorisierten Hauptaktionen."""
    akzentfarbe = karte.color or hole_akzentfarbe_fuer_titel(karte.titel) or STANDARD_AKZENTFARBE
    hintergrundfarbe = f"{akzentfarbe}18"
    anzeigetitel = hole_anzeigetext_fuer_titel(karte.titel) or karte.titel
    icon_html = ""

    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2.4rem; display:block; "
            f"margin: 0 auto 0.55rem; color: {akzentfarbe};'>{icon_name}</span>"
        )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(180deg, {hintergrundfarbe} 0%, #ffffff 92%);
                border-top: 0.45rem solid {akzentfarbe};
                border-left: 0.35rem solid {akzentfarbe};
                border-radius: 14px;
                padding: 1.15rem 1rem 1rem 1rem;
                margin-bottom: 0.9rem;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        line-height: 1.2;
                        color: {akzentfarbe};
                    ">
                        {anzeigetitel}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                color: #334155;
                min-height: 4.5rem;
                line-height: 1.55;
                margin-bottom: 0.6rem;
            ">
                {karte.beschreibung}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_hauptaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)


def zeige_nebenaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine kompaktere Aktionskarte für weitere Dashboard-Ziele."""
    akzentfarbe = karte.color or hole_akzentfarbe_fuer_titel(karte.titel) or STANDARD_AKZENTFARBE
    hintergrundfarbe = f"{akzentfarbe}18"
    anzeigetitel = hole_anzeigetext_fuer_titel(karte.titel) or karte.titel
    icon_html = ""

    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2rem; display:block; "
            f"margin: 0 auto 0.45rem; color: {akzentfarbe};'>{icon_name}</span>"
        )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(180deg, {hintergrundfarbe} 0%, #ffffff 92%);
                border-top: 0.35rem solid {akzentfarbe};
                border-left: 0.3rem solid {akzentfarbe};
                border-radius: 14px;
                padding: 0.95rem 0.9rem 0.85rem 0.9rem;
                margin-bottom: 0.75rem;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: 1.35rem;
                        font-weight: 700;
                        line-height: 1.25;
                        color: {akzentfarbe};
                    ">
                        {anzeigetitel}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                color: #475569;
                min-height: 5.3rem;
                line-height: 1.5;
                margin-bottom: 0.55rem;
                font-size: 0.95rem;
            ">
                {karte.beschreibung}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_nebenaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)


def main() -> None:
    """Rendert das Dashboard und bindet die fachlichen Inhalte ein."""
    zeige_dashboard_design_css()

    anzeige_name = hole_anzeige_name(st.session_state)

    show_header(title="Dashboard")

    st.caption(DASHBOARD_UNTERTITEL)
    st.write(f"Willkommen, **{anzeige_name}**.")
    st.info(DASHBOARD_HINWEIS)

    zeige_workflow_uebersicht()
    zeige_naechster_schritt_hilfe()
    zeige_status_legende()

    hauptaktionen = hole_hauptaktionskarten()
    if hauptaktionen:
        st.markdown("### Hauptaktionen")
        hauptaktions_spalten = st.columns(2)

        for spalte, karte in zip(hauptaktions_spalten, hauptaktionen):
            with spalte:
                zeige_hauptaktionskarte(karte)

    nebenaktionen = hole_nebenaktionskarten()
    if nebenaktionen:
        st.markdown("### Weitere Aktionen")
        nebenaktions_spalten = st.columns(len(nebenaktionen))

        for spalte, karte in zip(nebenaktions_spalten, nebenaktionen):
            with spalte:
                zeige_nebenaktionskarte(karte)


main()