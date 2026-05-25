"""Streamlit-Seite für die Übersicht aller Patienten."""

from __future__ import annotations

import streamlit as st

from domaene import Patient
from functions.gemeinsam.anzeige_hilfen import formatiere_datum, formatiere_zeitpunkt
from functions.patienten.loeschen import (
    bereinige_patientbezogenen_zustand_nach_loeschung,
    hole_und_entferne_erfolgsmeldung,
    loesche_patient,
    merke_erfolgreiche_loeschung,
)
from functions.patienten.navigation import (
    aktiviere_patientenbearbeitung,
    aktiviere_patientendetailansicht,
    deaktiviere_patientenbearbeitung,
    deaktiviere_patientendetailansicht,
    hat_gueltige_patientenbearbeiten_route,
    hat_gueltige_patientendetail_route,
    ist_patientenbearbeitung_aktiv,
    ist_patientendetailansicht_aktiv,
)
from functions.patienten.uebersicht import (
    filtere_patienten,
    lade_patienten,
)
from ui.header import show_header
from views.patient_bearbeiten import main as rendere_patientenbearbeitung
from views.patientendetail import main as rendere_patientendetailansicht


def zeige_seitenstil() -> None:
    """Fuegt kleine visuelle Verbesserungen fuer die Patientenuebersicht hinzu."""
    st.markdown(
        """
        <style>
        div[class*="st-key-patient_loeschtrigger_"] button,
        div[class*="st-key-patient_loeschbestaetigung_"] button {
            background: #DC2626 !important;
            color: #ffffff !important;
            border: none !important;
            box-shadow: none !important;
            border-radius: 8px !important;
        }

        div[class*="st-key-patient_loeschtrigger_"] button:hover,
        div[class*="st-key-patient_loeschbestaetigung_"] button:hover {
            background: #B91C1C !important;
            color: #ffffff !important;
            border: none !important;
        }

        div[class*="st-key-patient_loeschtrigger_"] button:focus,
        div[class*="st-key-patient_loeschtrigger_"] button:active,
        div[class*="st-key-patient_loeschtrigger_"] button:focus-visible,
        div[class*="st-key-patient_loeschbestaetigung_"] button:focus,
        div[class*="st-key-patient_loeschbestaetigung_"] button:active,
        div[class*="st-key-patient_loeschbestaetigung_"] button:focus-visible {
            outline: none !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[class*="st-key-patient_loeschtrigger_"] button:disabled,
        div[class*="st-key-patient_loeschbestaetigung_"] button:disabled {
            background: #FCA5A5 !important;
            color: #ffffff !important;
            border: none !important;
        }

        .patient-kachel {
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 16px;
            padding: 1rem;
            min-height: 130px;
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(247,249,252,0.96));
        }

        .patient-kachel-icon {
            font-size: 2rem;
            line-height: 1;
            margin-bottom: 0.35rem;
        }

        .patient-kachel-zahl {
            font-size: 1.6rem;
            font-weight: 750;
            margin-bottom: 0.15rem;
        }

        .patient-kachel-label {
            font-size: 0.95rem;
            font-weight: 650;
            margin-bottom: 0.2rem;
        }

        .patient-kachel-caption {
            color: rgba(49, 51, 63, 0.65);
            font-size: 0.82rem;
        }

        .patient-chip {
            display: inline-block;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 999px;
            padding: 0.25rem 0.7rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            background: rgba(250,250,250,0.8);
            font-size: 0.88rem;
        }

        .patient-hinweisbox {
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-radius: 16px;
            padding: 1rem;
            background: rgba(247,249,252,0.8);
        }

        .patient-zeilenkopf {
            color: rgba(49, 51, 63, 0.72);
            font-size: 0.88rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def oeffne_patientendetail(patient_id: str) -> None:
    """Aktiviert die interne Detailansicht innerhalb der Patientenübersicht."""
    if not aktiviere_patientendetailansicht(patient_id):
        st.error("Die Patientendetailansicht konnte nicht geöffnet werden.")
        return

    st.rerun()


def oeffne_patientbearbeitung(patient_id: str) -> None:
    """Aktiviert die interne Bearbeitung innerhalb der Patientenübersicht."""
    if not aktiviere_patientenbearbeitung(patient_id):
        st.error("Die Patientenbearbeitung konnte nicht geöffnet werden.")
        return

    st.rerun()


def bestaetige_und_loesche_patient(patient: Patient) -> None:
    """Löscht einen Patienten über die bestehende Löschlogik und aktualisiert die Übersicht."""
    erfolgsmeldung = loesche_patient(patient.id)

    if erfolgsmeldung is None:
        return

    bereinige_patientbezogenen_zustand_nach_loeschung()
    merke_erfolgreiche_loeschung(erfolgsmeldung)
    st.rerun()


def zeige_patientendetailansicht_innerhalb_der_uebersicht() -> None:
    """Rendert die bestehende Patientendetailansicht innerhalb der sichtbaren Übersicht."""
    rendere_patientendetailansicht()


def zeige_patientenbearbeitung_innerhalb_der_uebersicht() -> None:
    """Rendert die bestehende Patientenbearbeitung innerhalb der sichtbaren Übersicht."""
    rendere_patientenbearbeitung()


def zeige_erfolgsmeldungen() -> None:
    """Zeigt eine zwischengespeicherte Erfolgsmeldung zur Patientenlöschung an."""
    erfolgsmeldung = hole_und_entferne_erfolgsmeldung()

    if erfolgsmeldung:
        st.success(erfolgsmeldung)


def zeige_navigation() -> None:
    """Zeigt die wichtigsten Navigationsaktionen der Patientenuebersicht."""
    with st.container(border=True):
        st.markdown("### Navigation")

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


def zeige_uebersichtskacheln(
    patienten: list[Patient],
    gefilterte_patienten: list[Patient],
    suchtext: str,
) -> None:
    """Zeigt kleine visuelle Kennzahlen zur Patientenliste."""
    gesamtzahl = len(patienten)
    trefferzahl = len(gefilterte_patienten)
    suche_aktiv = bool(suchtext.strip())

    if suche_aktiv:
        suchstatus = "Suche aktiv"
        suchcaption = f"Gefiltert nach: {suchtext.strip()}"
    else:
        suchstatus = "Keine Suche"
        suchcaption = "Alle Patienten werden angezeigt."

    kachel_1, kachel_2, kachel_3 = st.columns(3)

    with kachel_1:
        st.markdown(
            f"""
            <div class="patient-kachel">
                <div class="patient-kachel-icon">👥</div>
                <div class="patient-kachel-zahl">{gesamtzahl}</div>
                <div class="patient-kachel-label">Patienten total</div>
                <div class="patient-kachel-caption">Alle aktuell erfassten Patienten.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kachel_2:
        st.markdown(
            f"""
            <div class="patient-kachel">
                <div class="patient-kachel-icon">🔎</div>
                <div class="patient-kachel-zahl">{trefferzahl}</div>
                <div class="patient-kachel-label">Aktuelle Treffer</div>
                <div class="patient-kachel-caption">Patienten nach angewandter Suche.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kachel_3:
        st.markdown(
            f"""
            <div class="patient-kachel">
                <div class="patient-kachel-icon">📋</div>
                <div class="patient-kachel-zahl">{suchstatus}</div>
                <div class="patient-kachel-label">Listenstatus</div>
                <div class="patient-kachel-caption">{suchcaption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def zeige_suchbereich() -> str:
    """Zeigt die Suche optisch abgesetzt an und liefert den Suchtext."""
    with st.container(border=True):
        st.markdown("### Patienten suchen")
        st.markdown(
            """
            <div>
                <span class="patient-chip">🔎 Suche nach Vorname</span>
                <span class="patient-chip">🔎 Suche nach Nachname</span>
                <span class="patient-chip">📋 Ergebnisliste wird automatisch gefiltert</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        suchtext = st.text_input("Suche nach Vorname oder Nachname")

    return suchtext


def zeige_leermeldung() -> None:
    """Zeigt eine Leermeldung an, wenn noch keine Patienten vorhanden sind."""
    st.markdown(
        """
        <div class="patient-hinweisbox">
            <h3>👥 Noch keine Patienten erfasst</h3>
            <p>Erfasse zuerst einen Patienten, damit die Übersicht genutzt werden kann.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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


def zeige_leermeldung_keine_treffer(suchtext: str) -> None:
    """Zeigt eine Meldung an, wenn die Suche keine Treffer liefert."""
    st.markdown(
        f"""
        <div class="patient-hinweisbox">
            <h3>🔎 Keine Treffer gefunden</h3>
            <p>Zur Suche <strong>{suchtext.strip()}</strong> wurden keine Patienten gefunden.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_tabellenkopf() -> None:
    """Rendert den Tabellenkopf der Patientenliste."""
    spalten = st.columns((2.0, 2.0, 1.7, 1.5, 1.8, 1.1, 1.3, 1.3))
    ueberschriften = (
        "Vorname",
        "Nachname",
        "Geburtsdatum",
        "Geschlecht",
        "Erstellt am",
        "Details",
        "Bearbeiten",
        "Löschen",
    )

    for spalte, ueberschrift in zip(spalten, ueberschriften):
        spalte.markdown(f"<span class='patient-zeilenkopf'><strong>{ueberschrift}</strong></span>", unsafe_allow_html=True)


def zeige_loeschaktion(patient: Patient) -> None:
    """Zeigt die abgesicherte Löschaktion für einen Patienten in der Übersicht an."""
    with st.container(key=f"patient_loeschtrigger_{patient.id}"):
        with st.popover("Löschen", use_container_width=True):
            st.warning(
                f"Patient {patient.vorname} {patient.nachname} wird mit allen "
                "zugehörigen Materialien und Kulturdaten dauerhaft gelöscht."
            )
            st.caption("Diese Aktion kann nicht rückgängig gemacht werden.")

            with st.container(key=f"patient_loeschbestaetigung_{patient.id}"):
                if st.button(
                    "Löschen bestätigen",
                    key=f"patient_loeschen_{patient.id}",
                    type="primary",
                    use_container_width=True,
                ):
                    bestaetige_und_loesche_patient(patient)


def zeige_patientenzeile(patient: Patient) -> None:
    """Rendert eine einzelne Zeile der Patientenliste."""
    with st.container(border=True):
        spalten = st.columns((2.0, 2.0, 1.7, 1.5, 1.8, 1.1, 1.3, 1.3))

        spalten[0].markdown(f"👤 **{patient.vorname}**")
        spalten[1].write(patient.nachname)
        spalten[2].write(formatiere_datum(patient.geburtsdatum))
        spalten[3].write(patient.geschlecht)
        spalten[4].write(formatiere_zeitpunkt(patient.erstellt_am))

        if spalten[5].button(
            "Details",
            key=f"patient_detail_{patient.id}",
            use_container_width=True,
        ):
            oeffne_patientendetail(patient.id)

        if spalten[6].button(
            "Bearbeiten",
            key=f"patient_bearbeiten_{patient.id}",
            use_container_width=True,
        ):
            oeffne_patientbearbeitung(patient.id)

        with spalten[7]:
            zeige_loeschaktion(patient)


def zeige_patientenliste(gefilterte_patienten: list[Patient]) -> None:
    """Zeigt die gefilterte Patientenliste mit Kopfzeile und Patientenzeilen."""
    st.subheader("Patientenliste")
    zeige_tabellenkopf()
    st.divider()

    for patient in gefilterte_patienten:
        zeige_patientenzeile(patient)


def main() -> None:
    """Rendert die Patientenübersicht und bindet die Fachlogik ein."""
    zeige_seitenstil()

    if hat_gueltige_patientenbearbeiten_route():
        zeige_patientenbearbeitung_innerhalb_der_uebersicht()
        return

    if hat_gueltige_patientendetail_route():
        zeige_patientendetailansicht_innerhalb_der_uebersicht()
        return

    if ist_patientenbearbeitung_aktiv():
        deaktiviere_patientenbearbeitung()
        st.warning(
            "Die Patientenbearbeitung konnte nicht geöffnet werden, "
            "weil keine gültige Patienten-ID vorhanden ist."
        )

    if ist_patientendetailansicht_aktiv():
        deaktiviere_patientendetailansicht()
        st.warning(
            "Die Patientendetailansicht konnte nicht geöffnet werden, "
            "weil keine gültige Patienten-ID vorhanden ist."
        )

    show_header("Patientenuebersicht")
    st.write("Hier siehst du alle erfassten Patienten.")

    zeige_erfolgsmeldungen()
    zeige_navigation()

    patienten = lade_patienten()
    if patienten is None:
        return

    if not patienten:
        zeige_leermeldung()
        return

    st.divider()

    suchtext = zeige_suchbereich()
    gefilterte_patienten = filtere_patienten(patienten, suchtext)

    zeige_uebersichtskacheln(
        patienten=patienten,
        gefilterte_patienten=gefilterte_patienten,
        suchtext=suchtext,
    )

    if suchtext.strip():
        st.caption(
            f"Treffer: {len(gefilterte_patienten)} von {len(patienten)} Patienten"
        )
    else:
        st.caption(f"Anzahl Patienten: {len(patienten)}")

    if not gefilterte_patienten:
        zeige_leermeldung_keine_treffer(suchtext)
        return

    st.divider()
    zeige_patientenliste(gefilterte_patienten)


main()