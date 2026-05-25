"""Hilfe- und Glossarseite für BaktoLab."""

from __future__ import annotations

import streamlit as st

from ui.header import show_header


def zeige_design_css() -> None:
    """Ergaenzt lokale Styles fuer die Hilfe- und Glossarseite."""
    st.markdown(
        """
        <style>
        .hilfe-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            min-height: 145px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
            margin-bottom: 0.8rem;
        }

        .hilfe-card-title {
            color: #1d4ed8;
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .hilfe-card-text {
            color: #475569;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .hinweis-box {
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-left: 7px solid #f97316;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .hinweis-title {
            color: #7c2d12;
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.35rem;
        }

        .hinweis-text {
            color: #7c2d12;
            font-size: 0.92rem;
            line-height: 1.5;
        }

        .workflow-step {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.65rem;
        }

        .workflow-number {
            display: inline-block;
            background: #2563eb;
            color: white;
            font-weight: 800;
            border-radius: 999px;
            width: 1.8rem;
            height: 1.8rem;
            line-height: 1.8rem;
            text-align: center;
            margin-right: 0.5rem;
        }

        .workflow-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 1rem;
        }

        .workflow-text {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
            margin-top: 0.35rem;
        }

        .workflow-graphic-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            min-height: 150px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
        }

        .workflow-graphic-number {
            background: #2563eb;
            color: white;
            font-weight: 850;
            border-radius: 999px;
            width: 2rem;
            height: 2rem;
            line-height: 2rem;
            margin: 0 auto 0.6rem auto;
        }

        .workflow-graphic-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
        }

        .workflow-graphic-text {
            color: #475569;
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .keimzahl-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            min-height: 145px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        }

        .keimzahl-code {
            font-size: 1.55rem;
            font-weight: 900;
            margin-bottom: 0.35rem;
        }

        .keimzahl-value {
            font-size: 1rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }

        .keimzahl-text {
            color: #475569;
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .keimzahl-k4 {
            border: 1px solid #c7d2fe;
            border-left: 7px solid #6366f1;
        }

        .keimzahl-p4 {
            border: 1px solid #bfdbfe;
            border-left: 7px solid #2563eb;
        }

        .keimzahl-p5 {
            border: 1px solid #bbf7d0;
            border-left: 7px solid #22c55e;
        }

        .keimzahl-g5 {
            border: 1px solid #fed7aa;
            border-left: 7px solid #f97316;
        }

        .code-k4 {
            color: #4f46e5;
        }

        .code-p4 {
            color: #1d4ed8;
        }

        .code-p5 {
            color: #15803d;
        }

        .code-g5 {
            color: #c2410c;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def zeige_hilfe_karte(titel: str, text: str) -> None:
    """Zeigt eine kleine Hilfekarte."""
    st.markdown(
        f"""
        <div class="hilfe-card">
            <div class="hilfe-card-title">{titel}</div>
            <div class="hilfe-card-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_workflow_schritt(nummer: int, titel: str, text: str) -> None:
    """Zeigt einen Workflow-Schritt."""
    st.markdown(
        f"""
        <div class="workflow-step">
            <span class="workflow-number">{nummer}</span>
            <span class="workflow-title">{titel}</span>
            <div class="workflow-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_prototyp_hinweis() -> None:
    """Zeigt einen Hinweis zu Datenschutz und Prototyp-Charakter."""
    st.markdown(
        """
        <div class="hinweis-box">
            <div class="hinweis-title">Wichtiger Hinweis</div>
            <div class="hinweis-text">
                BaktoLab ist ein Prototyp für Ausbildungs- und Demonstrationszwecke.
                Bitte keine echten Patientendaten erfassen. Die App ist nicht für den
                produktiven medizinischen Einsatz vorgesehen.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_app_hilfe() -> None:
    """Zeigt eine allgemeine Hilfe zur App."""
    st.markdown("## Hilfe zur App")

    spalte_1, spalte_2, spalte_3 = st.columns(3)

    with spalte_1:
        zeige_hilfe_karte(
            titel="Zweck der App",
            text=(
                "BaktoLab bildet einen mikrobiologischen Laborworkflow ab. "
                "Die App verbindet Patientenaufnahme, Materialerfassung, "
                "Kulturbeurteilung, Befundanzeige und PDF-Export."
            ),
        )

    with spalte_2:
        zeige_hilfe_karte(
            titel="Hauptworkflow",
            text=(
                "Der vollständige Workflow ist aktuell besonders für Urinproben "
                "mit der Analyse Allgemeine Bakteriologie vorgesehen."
            ),
        )

    with spalte_3:
        zeige_hilfe_karte(
            titel="Resistenzmonitoring",
            text=(
                "Das Resistenzmonitoring ist ein unabhängiger Bereich für "
                "spitalhygienische oder infektiologische Fragestellungen."
            ),
        )


def zeige_workflow_grafik_karte(nummer: int, titel: str, text: str) -> None:
    """Zeigt eine Karte fuer die visuelle Workflow-Grafik."""
    st.markdown(
        f"""
        <div class="workflow-graphic-card">
            <div class="workflow-graphic-number">{nummer}</div>
            <div class="workflow-graphic-title">{titel}</div>
            <div class="workflow-graphic-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_workflow_grafik() -> None:
    """Zeigt den BaktoLab-Workflow als visuelle Grafik."""
    st.markdown("## Visuelle Workflow-Grafik")
    st.caption(
        "Diese Übersicht zeigt den idealen Ablauf von der Patientenaufnahme bis zum PDF-Befund."
    )

    spalten = st.columns(6)

    schritte = [
        (1, "Patient", "Stammdaten erfassen"),
        (2, "Material", "Probe zuordnen"),
        (3, "Kultur", "Wachstum und Keim erfassen"),
        (4, "Beurteilung", "Empfehlung berechnen"),
        (5, "Validierung", "Daten fachlich freigeben"),
        (6, "PDF", "Befund exportieren"),
    ]

    for spalte, (nummer, titel, text) in zip(spalten, schritte):
        with spalte:
            zeige_workflow_grafik_karte(nummer, titel, text)


def zeige_keimzahl_grafik_karte(
    code: str,
    wert: str,
    text: str,
    css_klasse: str,
    code_klasse: str,
) -> None:
    """Zeigt eine visuelle Karte fuer einen Keimzahl-Code."""
    st.markdown(
        f"""
        <div class="keimzahl-card {css_klasse}">
            <div class="keimzahl-code {code_klasse}">{code}</div>
            <div class="keimzahl-value">{wert}</div>
            <div class="keimzahl-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_keimzahl_code_grafik() -> None:
    """Zeigt die Keimzahl-Codes als visuelle Karten."""
    st.markdown("## Keimzahl-Code-Grafik")
    st.caption(
        "Die Keimzahl-Codes vereinfachen die Erfassung der Bakterienmenge im Urinbefund."
    )

    spalte_1, spalte_2, spalte_3, spalte_4 = st.columns(4)

    with spalte_1:
        zeige_keimzahl_grafik_karte(
            code="k4",
            wert="<10'000",
            text="weniger als 10'000 KBE/ml",
            css_klasse="keimzahl-k4",
            code_klasse="code-k4",
        )

    with spalte_2:
        zeige_keimzahl_grafik_karte(
            code="p4",
            wert="10'000",
            text="10'000 KBE/ml",
            css_klasse="keimzahl-p4",
            code_klasse="code-p4",
        )

    with spalte_3:
        zeige_keimzahl_grafik_karte(
            code="p5",
            wert="100'000",
            text="100'000 KBE/ml",
            css_klasse="keimzahl-p5",
            code_klasse="code-p5",
        )

    with spalte_4:
        zeige_keimzahl_grafik_karte(
            code="g5",
            wert=">100'000",
            text="mehr als 100'000 KBE/ml",
            css_klasse="keimzahl-g5",
            code_klasse="code-g5",
        )


def zeige_workflow_erklaerung() -> None:
    """Zeigt den BaktoLab-Workflow als Schrittfolge."""
    st.markdown("## Workflow-Erklärung")

    zeige_workflow_schritt(
        nummer=1,
        titel="Patient erfassen",
        text=(
            "Zuerst werden die Stammdaten des Patienten erfasst. "
            "Dazu gehören Vorname, Nachname, Geburtsdatum und Geschlecht."
        ),
    )

    zeige_workflow_schritt(
        nummer=2,
        titel="Material erfassen",
        text=(
            "Anschliessend wird ein Material einem bestehenden Patienten zugeordnet. "
            "Dabei werden Materialtyp, Analyse, Abnahmedatum und Eingangsdatum festgelegt."
        ),
    )

    zeige_workflow_schritt(
        nummer=3,
        titel="Kulturen ablesen",
        text=(
            "Bei unterstütztem Material, aktuell vor allem Urin mit Allgemeiner "
            "Bakteriologie, wird der Kulturworkflow geöffnet. Dort werden Wachstum, "
            "Keim, Keimzahl und Rolle erfasst."
        ),
    )

    zeige_workflow_schritt(
        nummer=4,
        titel="Beurteilung berechnen",
        text=(
            "Nach der Erfassung der Kulturdaten berechnet die App eine fachliche "
            "Beurteilung und zeigt an, ob zum Beispiel Identifikation oder "
            "Resistenztestung empfohlen wird."
        ),
    )

    zeige_workflow_schritt(
        nummer=5,
        titel="Validieren und Befund öffnen",
        text=(
            "Nach der Prüfung können die Daten validiert werden. Danach öffnet sich "
            "der mikrobiologische Befund."
        ),
    )

    zeige_workflow_schritt(
        nummer=6,
        titel="PDF herunterladen",
        text=(
            "Der validierte Befund kann als PDF-Datei heruntergeladen und gespeichert werden."
        ),
    )


def zeige_keimzahl_codes() -> None:
    """Zeigt die Keimzahl-Codes."""
    st.markdown("## Keimzahl-Codes als Tabelle")

    keimzahl_daten = [
        {
            "Code": "k4",
            "Bedeutung": "kleiner als 10'000 koloniebildende Einheiten pro Milliliter",
            "Kurzform": "<10'000 KBE/ml",
        },
        {
            "Code": "p4",
            "Bedeutung": "10'000 koloniebildende Einheiten pro Milliliter",
            "Kurzform": "10'000 KBE/ml",
        },
        {
            "Code": "p5",
            "Bedeutung": "100'000 koloniebildende Einheiten pro Milliliter",
            "Kurzform": "100'000 KBE/ml",
        },
        {
            "Code": "g5",
            "Bedeutung": "grösser als 100'000 koloniebildende Einheiten pro Milliliter",
            "Kurzform": ">100'000 KBE/ml",
        },
    ]

    st.dataframe(
        keimzahl_daten,
        use_container_width=True,
        hide_index=True,
    )


def zeige_abkuerzungen() -> None:
    """Zeigt wichtige Abkuerzungen aus BaktoLab."""
    st.markdown("## Abkürzungen")

    abkuerzungen = [
        {
            "Abkürzung": "kw",
            "Bedeutung": "Kein Wachstum",
            "Kontext": "Kulturbeurteilung / Befund",
        },
        {
            "Abkürzung": "ID + Resi",
            "Bedeutung": "Identifikation und Resistenztestung durchführen",
            "Kontext": "fachliche Empfehlung",
        },
        {
            "Abkürzung": "kf",
            "Bedeutung": "Keimflora",
            "Kontext": "Zusatzflora / Beurteilung",
        },
        {
            "Abkürzung": "kfzus",
            "Bedeutung": "zusätzlicher Keim im Sinne von Keimflora",
            "Kontext": "Zusatzflora / Beurteilung",
        },
        {
            "Abkürzung": "uriflor",
            "Bedeutung": "Urinflora beziehungsweise Kontaminationsflora",
            "Kontext": "Urinbefund",
        },
        {
            "Abkürzung": "urikont",
            "Bedeutung": "Hinweis auf Urinkontamination",
            "Kontext": "Urinbefund",
        },
    ]

    st.dataframe(
        abkuerzungen,
        use_container_width=True,
        hide_index=True,
    )


def zeige_glossar() -> None:
    """Zeigt ein Glossar mit wichtigen Fachbegriffen."""
    st.markdown("## Glossar")

    glossar = [
        {
            "Begriff": "KBE/ml",
            "Erklärung": (
                "Koloniebildende Einheiten pro Milliliter. Einheit zur ungefähren "
                "Quantifizierung bakteriellen Wachstums."
            ),
        },
        {
            "Begriff": "Keim",
            "Erklärung": (
                "Mikroorganismus, der in einer Probe nachgewiesen oder beurteilt wird."
            ),
        },
        {
            "Begriff": "Keimzahl",
            "Erklärung": (
                "Menge der nachgewiesenen Keime in einer Probe, in BaktoLab über Codes "
                "wie k4, p4, p5 und g5 dargestellt."
            ),
        },
        {
            "Begriff": "Kontamination",
            "Erklärung": (
                "Hinweis darauf, dass eine Probe möglicherweise durch Begleit- oder "
                "Umgebungsflora verunreinigt wurde."
            ),
        },
        {
            "Begriff": "Urinflora",
            "Erklärung": (
                "Mikrobielle Flora, die im Urinkontext als Begleit- oder "
                "Kontaminationsflora interpretiert werden kann."
            ),
        },
        {
            "Begriff": "Identifikation",
            "Erklärung": (
                "Fachlicher Schritt zur genaueren Bestimmung eines nachgewiesenen Keims."
            ),
        },
        {
            "Begriff": "Resistenztestung",
            "Erklärung": (
                "Untersuchung, ob ein Keim gegenüber bestimmten Antibiotika empfindlich "
                "oder resistent ist."
            ),
        },
        {
            "Begriff": "Validierung",
            "Erklärung": (
                "Fachliche Freigabe eines Befunds nach Prüfung der erfassten Daten."
            ),
        },
        {
            "Begriff": "Befund",
            "Erklärung": (
                "Strukturierte Zusammenfassung der mikrobiologischen Untersuchungsergebnisse."
            ),
        },
        {
            "Begriff": "Resistenzmonitoring",
            "Erklärung": (
                "Auswertung resistenter und getesteter Isolate über Zeiträume hinweg."
            ),
        },
    ]

    st.dataframe(
        glossar,
        use_container_width=True,
        hide_index=True,
    )


def zeige_faq() -> None:
    """Zeigt haeufige Fragen."""
    st.markdown("## Häufige Fragen")

    with st.expander(
        "Warum funktioniert der vollständige Workflow vor allem mit Urin und Allgemeiner Bakteriologie?"
    ):
        st.write(
            "Der aktuelle Prototyp wurde gezielt auf einen klar abgegrenzten "
            "mikrobiologischen Workflow ausgelegt. Urin mit Allgemeiner Bakteriologie "
            "eignet sich dafür gut, weil Wachstum, Keimzahl, Keimrolle und Beurteilung "
            "strukturiert abgebildet werden können."
        )

    with st.expander("Kann ich andere Materialtypen erfassen?"):
        st.write(
            "Ja. Andere Materialtypen können erfasst und in der Patientenakte gespeichert werden. "
            "Der vollständige Kulturworkflow mit automatischer Beurteilung und Befund ist aktuell "
            "jedoch nicht für alle Materialtypen vollständig umgesetzt."
        )

    with st.expander("Wofür ist das Resistenzmonitoring gedacht?"):
        st.write(
            "Das Resistenzmonitoring dient der Darstellung getesteter und resistenter Isolate. "
            "Es ist unabhängig vom Patientenworkflow nutzbar und kann zum Beispiel für "
            "spitalhygienische oder infektiologische Fragestellungen verwendet werden."
        )

    with st.expander("Darf die App mit echten Patientendaten verwendet werden?"):
        st.write(
            "Nein. BaktoLab ist ein Ausbildungs- und Demonstrationsprototyp. "
            "Für Tests und Präsentationen sollten ausschliesslich fiktive Daten verwendet werden."
        )


def main() -> None:
    """Rendert die Hilfe- und Glossarseite."""
    zeige_design_css()

    show_header("Hilfe & Glossar")

    st.caption(
        "Diese Seite erklärt den BaktoLab-Workflow, wichtige Fachbegriffe, "
        "Keimzahl-Codes und Abkürzungen."
    )

    zeige_prototyp_hinweis()
    zeige_app_hilfe()
    zeige_workflow_grafik()
    zeige_keimzahl_code_grafik()
    zeige_workflow_erklaerung()
    zeige_keimzahl_codes()
    zeige_abkuerzungen()
    zeige_glossar()
    zeige_faq()


main()