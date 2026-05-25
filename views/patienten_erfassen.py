"""Streamlit-Seite zur Erfassung neuer Patienten."""

from __future__ import annotations

from datetime import date

import streamlit as st

from functions.patienten.erfassung import (
    GEBURTSTAG_SCHLUESSEL,
    GEBURTSJAHR_SCHLUESSEL,
    GEBURTSMONAT_SCHLUESSEL,
    GESCHLECHTER,
    GESCHLECHT_SCHLUESSEL,
    NACHNAME_SCHLUESSEL,
    VORNAME_SCHLUESSEL,
    hole_und_entferne_erfolgsmeldung,
    initialisiere_formularzustand,
    merke_erfolgreiche_speicherung,
    speichere_patient,
)
from ui.header import show_header


GEBURTSDATUM_KALENDER_SCHLUESSEL = "geburtsdatum_kalender"


def zeige_design_css() -> None:
    """Ergänzt kleine lokale Styles für eine ruhigere Patientenerfassung."""
    st.markdown(
        """
        <style>
        .patient-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
            min-height: 120px;
        }

        .patient-card-icon {
            font-size: 2rem;
            line-height: 1;
            margin-bottom: 0.35rem;
        }

        .patient-card-title {
            font-size: 0.95rem;
            color: #1d4ed8;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .patient-card-text {
            font-size: 0.88rem;
            color: #475569;
        }

        .patient-section-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: #1d4ed8;
            margin-top: 1.2rem;
            margin-bottom: 0.6rem;
        }

        .patient-chip {
            display: inline-block;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            background: rgba(250,250,250,0.85);
            font-size: 0.88rem;
        }

        .patient-info-box {
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            background: #f8fbff;
            margin-top: 0.7rem;
            margin-bottom: 0.7rem;
        }

        .patient-info-label {
            font-size: 0.82rem;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .patient-info-title {
            font-size: 1.1rem;
            color: #0f172a;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .patient-info-text {
            font-size: 0.9rem;
            color: #475569;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def zeige_einfuehrungskarten() -> None:
    """Zeigt kleine visuelle Hinweise zur Patientenerfassung."""
    st.markdown('<div class="patient-section-title">Erfassungsschritte</div>', unsafe_allow_html=True)

    karte_1, karte_2, karte_3 = st.columns(3)

    with karte_1:
        st.markdown(
            """
            <div class="patient-card">
                <div class="patient-card-icon">👤</div>
                <div class="patient-card-title">Personendaten</div>
                <div class="patient-card-text">
                    Vorname, Nachname und Geschlecht werden für die Patientenakte erfasst.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with karte_2:
        st.markdown(
            """
            <div class="patient-card">
                <div class="patient-card-icon">📅</div>
                <div class="patient-card-title">Geburtsdatum</div>
                <div class="patient-card-text">
                    Das Datum wird bequem über den Kalender ausgewählt.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with karte_3:
        st.markdown(
            """
            <div class="patient-card">
                <div class="patient-card-icon">🆔</div>
                <div class="patient-card-title">Patienten-ID</div>
                <div class="patient-card-text">
                    Die eindeutige Patienten-ID wird automatisch erzeugt.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def zeige_formularhinweis() -> None:
    """Zeigt einen kurzen visuellen Hinweis oberhalb des Formulars."""
    st.markdown('<div class="patient-section-title">Patientendaten erfassen</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="patient-info-box">
            <div class="patient-info-label">Hinweis</div>
            <div class="patient-info-title">Bitte alle Pflichtangaben vollständig ausfüllen</div>
            <div class="patient-info-text">
                Nach dem Speichern wird der Patient in der Patientenübersicht angezeigt.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div>
            <span class="patient-chip">👤 Vorname</span>
            <span class="patient-chip">👤 Nachname</span>
            <span class="patient-chip">📅 Geburtsdatum</span>
            <span class="patient-chip">⚧ Geschlecht</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_navigation() -> None:
    """Zeigt die Navigation zurück zum Dashboard."""
    st.markdown('<div class="patient-section-title">Navigation</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.page_link(
            "views/dashboard.py",
            label="Zurück zum Dashboard",
            icon=":material/dashboard:",
        )


def hole_vorausgewaehltes_geburtsdatum() -> date:
    """Erzeugt ein Datum aus dem bestehenden Formularzustand."""
    tag = st.session_state.get(GEBURTSTAG_SCHLUESSEL, 1)
    monat = st.session_state.get(GEBURTSMONAT_SCHLUESSEL, 1)
    jahr = st.session_state.get(GEBURTSJAHR_SCHLUESSEL, 2000)

    try:
        return date(int(jahr), int(monat), int(tag))
    except ValueError:
        return date(2000, 1, 1)


def uebertrage_kalenderdatum_in_formularzustand(geburtsdatum: date) -> None:
    """Speichert das Kalenderdatum in den bisherigen Tag-, Monat- und Jahr-Schlüsseln."""
    st.session_state[GEBURTSTAG_SCHLUESSEL] = geburtsdatum.day
    st.session_state[GEBURTSMONAT_SCHLUESSEL] = geburtsdatum.month
    st.session_state[GEBURTSJAHR_SCHLUESSEL] = geburtsdatum.year


def main() -> None:
    """Rendert die Patientenerfassung und ruft die Fachlogik auf."""
    zeige_design_css()
    initialisiere_formularzustand()

    show_header("Patient erfassen")
    st.write("Hier kannst du einen neuen Patienten erfassen.")
    st.info("Die Patienten-ID wird automatisch erzeugt.")

    erfolgsmeldung = hole_und_entferne_erfolgsmeldung()
    if erfolgsmeldung:
        st.success(erfolgsmeldung)

    zeige_einfuehrungskarten()
    zeige_formularhinweis()

    with st.form("patient_erfassen_formular"):
        with st.container(border=True):
            linke_spalte, rechte_spalte = st.columns(2)

            with linke_spalte:
                st.markdown("### Persönliche Angaben")
                st.text_input("Vorname", key=VORNAME_SCHLUESSEL)

                geburtsdatum = st.date_input(
                    "Geburtsdatum",
                    value=hole_vorausgewaehltes_geburtsdatum(),
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    format="DD.MM.YYYY",
                    key=GEBURTSDATUM_KALENDER_SCHLUESSEL,
                )

                st.caption("Das Geburtsdatum kann direkt im Kalender ausgewählt werden.")

            with rechte_spalte:
                st.markdown("### Weitere Angaben")
                st.text_input("Nachname", key=NACHNAME_SCHLUESSEL)
                st.selectbox("Geschlecht", GESCHLECHTER, key=GESCHLECHT_SCHLUESSEL)

                st.markdown(
                    """
                    <div class="patient-info-box">
                        <div class="patient-info-label">Automatisch</div>
                        <div class="patient-info-title">Patienten-ID</div>
                        <div class="patient-info-text">
                            Die ID wird beim Speichern automatisch erstellt.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            speichern = st.form_submit_button(
                "Patient speichern",
                type="primary",
                use_container_width=True,
            )

    if speichern:
        uebertrage_kalenderdatum_in_formularzustand(geburtsdatum)

        neue_erfolgsmeldung = speichere_patient()
        if neue_erfolgsmeldung is not None:
            merke_erfolgreiche_speicherung(neue_erfolgsmeldung)
            st.rerun()

    zeige_navigation()


main()