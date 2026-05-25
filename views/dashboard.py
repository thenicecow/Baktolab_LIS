"""Streamlit-Seite für das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
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

        .dashboard-help-box {
            background: #f8fbff;
            border: 1px solid #dbeafe;
            border-left: 6px solid #2563eb;
            border-radius: 16px;
            padding: 0.95rem 1.1rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .dashboard-help-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }

        .dashboard-help-text {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .demo-mini-card {
            background: #ffffff;
            border: 1px solid #dcfce7;
            border-radius: 14px;
            padding: 0.8rem 0.9rem;
            min-height: 105px;
        }

        .demo-mini-title {
            color: #166534;
            font-weight: 850;
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
        }

        .demo-label {
            color: #64748b;
            font-size: 0.75rem;
            font-weight: 750;
            margin-bottom: 0.1rem;
        }

        .demo-value {
            color: #0f172a;
            font-size: 0.9rem;
            font-weight: 650;
            margin-bottom: 0.35rem;
        }

        .status-chip {
            display: inline-block;
            padding: 0.35rem 0.65rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 750;
            margin: 0.2rem 0.25rem 0.2rem 0;
        }

        .chip-lila {
            background: #ede9fe;
            color: #5b21b6;
        }

        .chip-tuerkisgruen {
            background: #ccfbf1;
            color: #115e59;
        }

        .chip-hellgruen {
            background: #ecfccb;
            color: #3f6212;
        }

        .chip-gruen {
            background: #dcfce7;
            color: #14532d;
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


def zeige_hilfe_glossar_hinweis() -> None:
    """Zeigt einen dezenten Hinweis auf die Hilfe- und Glossarseite."""
    linke_spalte, rechte_spalte = st.columns((3, 1))

    with linke_spalte:
        st.markdown(
            """
            <div class="dashboard-help-box">
                <div class="dashboard-help-title">Hilfe & Glossar</div>
                <div class="dashboard-help-text">
                    Fachbegriffe, Keimzahl-Codes, Abkürzungen und der BaktoLab-Workflow
                    sind auf einer eigenen Hilfeseite zusammengefasst.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with rechte_spalte:
        st.write("")
        st.write("")
        st.page_link(
            "views/hilfe_glossar.py",
            label="Hilfe öffnen",
            icon=":material/help:",
        )


def zeige_demofall_wertkarte(titel: str, werte: list[tuple[str, str]]) -> None:
    """Rendert eine kompakte Karte mit Demo-Falldaten."""
    html_werte = ""

    for label, wert in werte:
        html_werte += f"""
        <div class="demo-label">{label}</div>
        <div class="demo-value">{wert}</div>
        """

    st.markdown(
        f"""
        <div class="demo-mini-card">
            <div class="demo-mini-title">{titel}</div>
            {html_werte}
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_demofall() -> None:
    """Zeigt einen weniger prominenten Demo-Fall fuer neue Benutzer."""
    with st.expander("Demo-Fall für neue Benutzer anzeigen"):
        st.caption(
            "Diese Beispielwerte werden nur angezeigt und nicht automatisch gespeichert. "
            "Sie helfen neuen Benutzern, den BaktoLab-Workflow Schritt für Schritt nachzuvollziehen."
        )

        patient_spalte, material_spalte, kultur_spalte = st.columns(3)

        with patient_spalte:
            zeige_demofall_wertkarte(
                titel="Patient",
                werte=[
                    ("Vorname", "Max"),
                    ("Nachname", "Muster"),
                    ("Geburtsdatum", "12.04.1985"),
                    ("Geschlecht", "Männlich"),
                ],
            )

        with material_spalte:
            zeige_demofall_wertkarte(
                titel="Material",
                werte=[
                    ("Materialtyp", "Urin"),
                    ("Analyse", "Allgemeine Bakteriologie"),
                    ("Abnahmedatum", "heutiges Datum"),
                    ("Eingangsdatum", "heutiges Datum"),
                ],
            )

        with kultur_spalte:
            zeige_demofall_wertkarte(
                titel="Kulturdaten",
                werte=[
                    ("Wachstum", "Ja"),
                    ("Keim", "Escherichia coli"),
                    ("Keimzahl", "p5 = 100'000 KBE/ml"),
                    ("Erwartung", "ID + Resi"),
                ],
            )

        st.caption(
            "Empfohlener Ablauf: Patient erfassen → Material erfassen → Kulturen ablesen "
            "→ Beurteilung berechnen → validieren → Befund als PDF herunterladen."
        )

        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            if st.button(
                "Patient erfassen starten",
                use_container_width=True,
                key="dashboard_demo_patient_starten",
            ):
                st.switch_page("views/patienten_erfassen.py")

        with rechte_spalte:
            st.page_link(
                "views/material_erfassen.py",
                label="Material erfassen öffnen",
                icon=":material/science:",
            )


def zeige_status_legende() -> None:
    """Zeigt eine einfache Status-Legende fuer den Workflow."""
    st.markdown("### Status-Legende")

    with st.container(border=True):
        st.markdown(
            """
            <span class="status-chip chip-lila">Patient erfasst</span>
            <span class="status-chip chip-tuerkisgruen">Material aufgenommen</span>
            <span class="status-chip chip-hellgruen">Kultur in Bearbeitung</span>
            <span class="status-chip chip-gruen">Befund validiert</span>
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

    zeige_workflow_uebersicht()
    zeige_hilfe_glossar_hinweis()
    zeige_demofall()
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