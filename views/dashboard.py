"""Streamlit-Seite für das Dashboard."""

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class DashboardZusatzkarte:
    """Beschreibt eine zusätzliche Dashboard-Aktionskarte."""

    titel: str
    beschreibung: str
    seitenpfad: str
    icon: str
    color: str
    button_text: str = "Öffnen"
    button_typ: str = "secondary"


def zeige_dashboard_design_css() -> None:
    """Ergaenzt lokale Styles fuer zusaetzliche Dashboard-Bereiche."""
    st.markdown(
        """
        <style>
        .dashboard-intro-box {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-left: 7px solid #2563eb;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            margin-bottom: 1rem;
        }

        .dashboard-intro-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 1.1rem;
            margin-bottom: 0.25rem;
        }

        .dashboard-intro-text {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.45;
        }

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


def zeige_intro(anzeige_name: str) -> None:
    """Zeigt eine kurze Einfuehrung ins Dashboard."""
    st.markdown(
        f"""
        <div class="dashboard-intro-box">
            <div class="dashboard-intro-title">Willkommen, {anzeige_name}</div>
            <div class="dashboard-intro-text">
                Das Dashboard zeigt den Laborworkflow und bietet direkten Zugriff auf die wichtigsten
                Bereiche der App.
            </div>
        </div>
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
    """Zeigt einen stabilen, fachlichen Workflow-Ueberblick mit integrierter Status-Legende."""
    st.markdown("### Workflow-Übersicht")

    spalte_1, spalte_2, spalte_3, spalte_4 = st.columns(4)

    with spalte_1:
        zeige_workflow_schritt(
            nummer=1,
            titel="Patient erfassen",
            beschreibung="Stammdaten aufnehmen und eine eindeutige Patientenakte erstellen.",
        )

    with spalte_2:
        zeige_workflow_schritt(
            nummer=2,
            titel="Material erfassen",
            beschreibung="Probe einem Patienten zuordnen, Materialtyp wählen und Datumsangaben prüfen.",
        )

    with spalte_3:
        zeige_workflow_schritt(
            nummer=3,
            titel="Kulturen ablesen",
            beschreibung="Wachstum, Keim, Keimzahl und Rolle erfassen und fachlich beurteilen.",
        )

    with spalte_4:
        zeige_workflow_schritt(
            nummer=4,
            titel="Befund exportieren",
            beschreibung="Validierte Kulturdaten prüfen und den mikrobiologischen Befund als PDF herunterladen.",
        )

    with st.container(border=True):
        st.markdown("**Status-Legende**")
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
            "Der genaue Bearbeitungsstand aller Fälle ist über den Fallstatus sichtbar."
        )


def hole_zusaetzliche_hauptaktionskarten() -> list[DashboardZusatzkarte]:
    """Liefert zusätzliche Hauptaktionen."""
    return [
        DashboardZusatzkarte(
            titel="Patientenübersicht",
            beschreibung=(
                "Zeigt alle erfassten Patienten, ermöglicht Suche, Detailansicht, "
                "Bearbeitung und sichere Löschaktion."
            ),
            seitenpfad="views/patientenuebersicht.py",
            icon=":material/people:",
            color="#2563EB",
            button_text="Übersicht öffnen",
            button_typ="primary",
        ),
        DashboardZusatzkarte(
            titel="Kulturen ablesen",
            beschreibung=(
                "Öffnet den Kulturworkflow für unterstützte Urinmaterialien mit "
                "Allgemeiner Bakteriologie."
            ),
            seitenpfad="views/kulturen_ablesen.py",
            icon=":material/biotech:",
            color="#16A34A",
            button_text="Kulturen öffnen",
            button_typ="secondary",
        ),
    ]


def hole_zusaetzliche_nebenaktionskarten() -> list[DashboardZusatzkarte]:
    """Liefert zusätzliche weitere Aktionen."""
    return [
        DashboardZusatzkarte(
            titel="Fallstatus",
            beschreibung=(
                "Zeigt den aktuellen Bearbeitungsstand aller Patientenfälle mit Material, "
                "Kulturstatus, Befundstatus und nächstem Schritt."
            ),
            seitenpfad="views/fallstatus.py",
            icon=":material/fact_check:",
            color="#22C55E",
            button_text="Fallstatus öffnen",
            button_typ="primary",
        ),
        DashboardZusatzkarte(
            titel="Probeneingang-Auswertung",
            beschreibung=(
                "Analysiert den Probeneingang nach Tagen, Kalenderwochen und Wochentagen "
                "inklusive Heatmap für Belastungsspitzen."
            ),
            seitenpfad="views/probeneingang_auswertung.py",
            icon=":material/analytics:",
            color="#F97316",
            button_text="Auswertung öffnen",
            button_typ="secondary",
        ),
        DashboardZusatzkarte(
            titel="Hilfe & Glossar",
            beschreibung=(
                "Erklärt Fachbegriffe, Keimzahl-Codes, Abkürzungen und den BaktoLab-Workflow."
            ),
            seitenpfad="views/hilfe_glossar.py",
            icon=":material/help:",
            color="#7C3AED",
            button_text="Hilfe öffnen",
            button_typ="secondary",
        ),
    ]


def zeige_zusatzaktionskarte(karte: DashboardZusatzkarte, kompakt: bool = False) -> None:
    """Rendert eine zusätzliche Aktionskarte im farbigen Dashboard-Stil."""
    akzentfarbe = karte.color or STANDARD_AKZENTFARBE
    hintergrundfarbe = f"{akzentfarbe}18"
    icon_groesse = "2rem" if kompakt else "2.4rem"
    titel_groesse = "1.25rem" if kompakt else "2rem"
    text_min_hoehe = "7.2rem" if kompakt else "4.5rem"
    kopf_min_hoehe = "7.4rem" if kompakt else "8.6rem"
    border_top = "0.35rem" if kompakt else "0.45rem"
    border_left = "0.3rem" if kompakt else "0.35rem"
    icon_html = ""

    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: {icon_groesse}; display:block; "
            f"margin: 0 auto 0.55rem; color: {akzentfarbe};'>{icon_name}</span>"
        )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(180deg, {hintergrundfarbe} 0%, #ffffff 92%);
                border-top: {border_top} solid {akzentfarbe};
                border-left: {border_left} solid {akzentfarbe};
                border-radius: 14px;
                padding: 1rem 0.9rem 0.9rem 0.9rem;
                margin-bottom: 0.75rem;
                min-height: {kopf_min_hoehe};
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: {titel_groesse};
                        font-weight: 700;
                        line-height: 1.2;
                        color: {akzentfarbe};
                    ">
                        {karte.titel}
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
                min-height: {text_min_hoehe};
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
            karte.button_text,
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_zusatzaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)


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
                min-height: 8.6rem;
                display: flex;
                align-items: center;
                justify-content: center;
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
                min-height: 7.4rem;
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: 1.25rem;
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
                min-height: 7.2rem;
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


def zeige_hauptaktionen() -> None:
    """Zeigt Hauptaktionen mit bestehenden und zusätzlich gewünschten Karten."""
    st.markdown("### Hauptaktionen")

    hauptaktionen = list(hole_hauptaktionskarten())
    zusatzkarten = hole_zusaetzliche_hauptaktionskarten()

    alle_karten = hauptaktionen + zusatzkarten

    for start in range(0, len(alle_karten), 2):
        spalten = st.columns(2)
        kartenpaar = alle_karten[start : start + 2]

        for spalte, karte in zip(spalten, kartenpaar):
            with spalte:
                if isinstance(karte, DashboardZusatzkarte):
                    zeige_zusatzaktionskarte(karte, kompakt=False)
                else:
                    zeige_hauptaktionskarte(karte)


def ist_kulturen_ablesen_karte(karte: DashboardAktionskarte) -> bool:
    """Prueft, ob eine Karte auf Kulturen ablesen verweist."""
    titel = str(getattr(karte, "titel", "")).strip().casefold()
    seitenpfad = str(getattr(karte, "seitenpfad", "")).strip().casefold()

    return titel == "kulturen ablesen" or seitenpfad == "views/kulturen_ablesen.py"


def ist_hilfe_glossar_karte(karte: DashboardAktionskarte) -> bool:
    """Prueft, ob eine Karte auf Hilfe und Glossar verweist."""
    titel = str(getattr(karte, "titel", "")).strip().casefold()
    seitenpfad = str(getattr(karte, "seitenpfad", "")).strip().casefold()

    return titel in {"hilfe & glossar", "hilfe und glossar"} or seitenpfad == "views/hilfe_glossar.py"


def zeige_weitere_aktionen() -> None:
    """Zeigt weitere Aktionen inklusive Fallstatus, Probeneingang-Auswertung und Hilfe."""
    st.markdown("### Weitere Aktionen")

    zusatzkarten = hole_zusaetzliche_nebenaktionskarten()

    nebenaktionen = [
        karte
        for karte in hole_nebenaktionskarten()
        if not ist_kulturen_ablesen_karte(karte)
        and not ist_hilfe_glossar_karte(karte)
    ]

    alle_karten = zusatzkarten + nebenaktionen

    if not alle_karten:
        return

    spalten = st.columns(len(alle_karten))

    for spalte, karte in zip(spalten, alle_karten):
        with spalte:
            if isinstance(karte, DashboardZusatzkarte):
                zeige_zusatzaktionskarte(karte, kompakt=True)
            else:
                zeige_nebenaktionskarte(karte)


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
    st.markdown("### Demo-Fall für neue Benutzer")

    with st.expander("Beispielwerte anzeigen"):
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


def main() -> None:
    """Rendert das Dashboard und bindet die fachlichen Inhalte ein."""
    zeige_dashboard_design_css()

    anzeige_name = hole_anzeige_name(st.session_state)

    show_header(title="Dashboard")

    st.caption(DASHBOARD_UNTERTITEL)
    zeige_intro(anzeige_name)

    zeige_workflow_uebersicht()
    st.divider()

    zeige_hauptaktionen()
    st.divider()

    zeige_weitere_aktionen()
    st.divider()

    zeige_demofall()


main()