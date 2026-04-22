"""Streamlit-Seite fuer die vorbereitete Funktion ``Kulturen ablesen``."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from domaene import ERLAUBTE_KEIMZAHL_CODES, Kulturdaten, Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_patient_label,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import (
    baue_kulturdaten_aus_formularwerten,
    hole_kulturdaten_oder_standard,
    ist_material_fuer_kulturen_ablesen_unterstuetzt,
    lade_materialkontext_fuer_kulturen_ablesen,
    speichere_kulturdaten_fuer_material,
)
from functions.kulturen.beurteilung import (
    UrinBeurteilung,
    beurteile_urin_allgemeine_bakteriologie,
)
from functions.kulturen.navigation import (
    deaktiviere_kulturen_ablesen,
    hole_material_id_fuer_kulturen_ablesen,
)


ROLLEN: tuple[str, ...] = ("pathogen", "kontaminante")
KEIMGRUPPEN: tuple[str, ...] = ("gramnegative_staebchen", "gpk_gps", "andere")
KEIMZAHL_CODES: tuple[str, ...] = tuple(
    code for code in ("k4", "p4", "p5", "g5") if code in ERLAUBTE_KEIMZAHL_CODES
)


def kehre_zur_patientendetailansicht_zurueck() -> None:
    """Beendet die Kulturseite und wechselt zur sichtbaren Patientenuebersicht zurueck."""
    deaktiviere_kulturen_ablesen()
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


def baue_formularschluessel(material_id: str, feldname: str) -> str:
    """Erzeugt einen stabilen Session-State-Schluessel fuer das lokale Kulturformular."""
    return f"kulturen_ablesen_{material_id}_{feldname}"


def initialisiere_formularzustand(material: Material) -> None:
    """Initialisiert den Formularzustand aus gespeicherten oder leeren Kulturdaten."""
    initialisiert_schluessel = baue_formularschluessel(material.id, "formular_initialisiert")
    if st.session_state.get(initialisiert_schluessel, False):
        return

    kulturdaten = hole_kulturdaten_oder_standard(material)
    wachstum_schluessel = baue_formularschluessel(material.id, "wachstum")
    keimanzahl_schluessel = baue_formularschluessel(material.id, "keimanzahl")

    st.session_state[wachstum_schluessel] = "nein" if kulturdaten.wachstum is False else "ja"

    keimanzahl = len(kulturdaten.keime) if kulturdaten.keime else 1
    st.session_state[keimanzahl_schluessel] = max(1, keimanzahl)

    for index, keim in enumerate(kulturdaten.keime):
        st.session_state[baue_formularschluessel(material.id, f"keim_id_{index}")] = keim.keim_id
        st.session_state[baue_formularschluessel(material.id, f"keimzahl_code_{index}")] = (
            keim.keimzahl_code
        )
        st.session_state[baue_formularschluessel(material.id, f"rolle_{index}")] = keim.rolle
        st.session_state[baue_formularschluessel(material.id, f"keimgruppe_{index}")] = (
            keim.keimgruppe
        )

    st.session_state[initialisiert_schluessel] = True


def hole_keimanzahl(material_id: str) -> int:
    """Liest die aktuell lokale Anzahl vorbereiteter Keime fuer das Material."""
    schluessel = baue_formularschluessel(material_id, "keimanzahl")
    wert = st.session_state.get(schluessel, 1)

    if not isinstance(wert, int):
        return 1

    return max(1, wert)


def erhoehe_keimanzahl(material_id: str) -> None:
    """Erhoeht lokal die Anzahl sichtbarer Keimeingaenge um eins."""
    schluessel = baue_formularschluessel(material_id, "keimanzahl")
    st.session_state[schluessel] = hole_keimanzahl(material_id) + 1


def hole_wachstum(material_id: str) -> bool:
    """Liest, ob lokal Wachstum fuer das Material ausgewaehlt ist."""
    schluessel = baue_formularschluessel(material_id, "wachstum")
    return st.session_state.get(schluessel, "ja") == "ja"


def hole_aktuellen_keimeintrag(material_id: str, index: int) -> dict[str, str]:
    """Liest einen einzelnen lokalen Keimeintrag aus dem Session State."""
    keim_id = st.session_state.get(baue_formularschluessel(material_id, f"keim_id_{index}"), "")
    keimzahl_code = st.session_state.get(
        baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
        KEIMZAHL_CODES[0],
    )
    rolle = st.session_state.get(
        baue_formularschluessel(material_id, f"rolle_{index}"),
        ROLLEN[0],
    )
    keimgruppe = st.session_state.get(
        baue_formularschluessel(material_id, f"keimgruppe_{index}"),
        KEIMGRUPPEN[0],
    )

    return {
        "keim_id": str(keim_id).strip(),
        "keimzahl_code": str(keimzahl_code).strip(),
        "rolle": str(rolle).strip(),
        "keimgruppe": str(keimgruppe).strip(),
    }


def hole_formularvorschau(material_id: str) -> dict[str, object]:
    """Baut eine Vorschau der aktuell erfassten Kulturdaten."""
    wachstum = hole_wachstum(material_id)

    if not wachstum:
        return {
            "wachstum": False,
            "keime": [],
            "beurteilung": None,
        }

    keime: list[dict[str, str]] = []

    for index in range(hole_keimanzahl(material_id)):
        keimeintrag = hole_aktuellen_keimeintrag(material_id, index)

        if not keimeintrag["keim_id"]:
            continue

        keime.append(keimeintrag)

    return {
        "wachstum": True,
        "keime": keime,
        "beurteilung": None,
    }


def baue_kulturdaten_aus_formularvorschau(
    material: Material,
    beurteilung: str | None,
) -> Kulturdaten | None:
    """Erzeugt Kulturdaten aus der aktuellen Formulareingabe."""
    vorschau = hole_formularvorschau(material.id)

    if vorschau["wachstum"] and not vorschau["keime"]:
        st.error("Bitte erfasse mindestens einen Keim oder waehle bei Wachstum 'nein'.")
        return None

    return baue_kulturdaten_aus_formularwerten(
        wachstum=bool(vorschau["wachstum"]),
        keime=list(vorschau["keime"]),
        beurteilung=beurteilung,
    )


def zeige_materialkontext(materialreferenz: str) -> tuple[Patient, Material] | None:
    """Laedt und zeigt den Materialkontext fuer die Kulturseite an."""
    st.caption(f"Aktuelle Materialreferenz: {materialreferenz}")

    try:
        materialkontext = lade_materialkontext_fuer_kulturen_ablesen()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Das ausgewaehlte Material konnte nicht geladen werden."
            )
        )
        return None

    if materialkontext is None:
        st.warning(
            "Zur gesetzten Materialreferenz konnte kein vorhandenes Material gefunden werden."
        )
        return None

    patient, material = materialkontext

    with st.container(border=True):
        st.markdown("**Aktuelles Material**")
        st.write(f"Patient: {formatiere_patient_label(patient)}")
        st.write(f"Material-ID: {material.id}")
        st.write(f"Materialtyp: {loese_materialtyp_label_auf(material.materialtyp_code)}")
        st.write(f"Analyse: {loese_analyse_label_auf(material.klinische_frage_code)}")
        st.write(f"Eingangsdatum: {formatiere_datum(material.eingangsdatum)}")

    return patient, material


def zeige_keimeingabe(material_id: str) -> None:
    """Rendert die Eingabemaske fuer eine variable Anzahl Keime."""
    st.markdown("**Keime erfassen**")

    for index in range(hole_keimanzahl(material_id)):
        with st.container(border=True):
            st.caption(f"Keim {index + 1}")

            st.text_input(
                "Keim-ID",
                key=baue_formularschluessel(material_id, f"keim_id_{index}"),
                placeholder="z.B. Escherichia coli",
            )

            linke_spalte, mittlere_spalte, rechte_spalte = st.columns(3)

            with linke_spalte:
                st.selectbox(
                    "Keimzahl",
                    options=list(KEIMZAHL_CODES),
                    key=baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
                )

            with mittlere_spalte:
                st.selectbox(
                    "Rolle",
                    options=list(ROLLEN),
                    key=baue_formularschluessel(material_id, f"rolle_{index}"),
                )

            with rechte_spalte:
                st.selectbox(
                    "Keimgruppe",
                    options=list(KEIMGRUPPEN),
                    key=baue_formularschluessel(material_id, f"keimgruppe_{index}"),
                )

    if st.button("Weiteren Keim hinzufuegen", use_container_width=True):
        erhoehe_keimanzahl(material_id)
        st.rerun()


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


def zeige_vorschau(material_id: str) -> None:
    """Zeigt die aktuell erfassten Kulturdaten als Vorschau an."""
    vorschau = hole_formularvorschau(material_id)

    st.subheader("Aktuelle Vorschau")

    with st.container(border=True):
        st.write(f"Wachstum: {'ja' if vorschau['wachstum'] else 'nein'}")

        keime = vorschau["keime"]

        if not keime:
            if vorschau["wachstum"]:
                st.info("Aktuell sind noch keine vollstaendigen Keimeintraege erfasst.")
            else:
                st.info("Es ist aktuell 'kein Wachstum' ausgewaehlt.")
            return

        st.dataframe(
            pd.DataFrame(keime),
            use_container_width=True,
            hide_index=True,
        )


def zeige_beurteilung(beurteilung: UrinBeurteilung | None) -> None:
    """Zeigt das aktuell vorhandene Beurteilungsergebnis uebersichtlich an."""
    st.subheader("Beurteilung")

    if beurteilung is None:
        st.info("Fuer dieses Material ist aktuell noch keine berechnete Beurteilung gespeichert.")
        return

    with st.container(border=True):
        st.markdown(f"**Gesamtbeurteilung:** {beurteilung.gesamtbeurteilung}")

        if beurteilung.hinweise:
            for hinweis in beurteilung.hinweise:
                st.caption(hinweis)

        if not beurteilung.keimbeurteilungen:
            return

        tabellendaten = [
            {
                "Keim-ID": keim.keim_id,
                "Keimzahl": keim.keimzahl_code,
                "Rolle": keim.rolle,
                "Effektive Rolle": keim.effektive_rolle,
                "Ergebnis": keim.ergebnis or "",
                "Begruendung": keim.begruendung,
            }
            for keim in beurteilung.keimbeurteilungen
        ]

        st.dataframe(
            pd.DataFrame(tabellendaten),
            use_container_width=True,
            hide_index=True,
        )


def main() -> None:
    """Rendert die Seite ``Kulturen ablesen`` mit speicherbarer Eingabemaske."""
    st.title("Kulturen ablesen")
    st.info(
        "Diese Seite gilt aktuell nur fuer Urin mit der Analyse "
        "Allgemeine Bakteriologie. Kulturdaten und berechnete Beurteilung "
        "werden materialbezogen gespeichert."
    )

    zeige_aktionsleiste()

    materialreferenz = hole_material_id_fuer_kulturen_ablesen()

    if materialreferenz is None:
        st.info("Es ist aktuell kein Material fuer 'Kulturen ablesen' ausgewaehlt.")
        return

    materialkontext = zeige_materialkontext(materialreferenz)
    if materialkontext is None:
        return

    _patient, material = materialkontext

    if not ist_material_fuer_kulturen_ablesen_unterstuetzt(material):
        st.warning(
            "Diese Beurteilung wird aktuell nur fuer Material 'Urin' "
            "mit der Analyse 'Allgemeine Bakteriologie' unterstuetzt."
        )
        return

    initialisiere_formularzustand(material)

    aktuelle_beurteilung = hole_gespeicherte_beurteilung(material)

    st.subheader("Kulturdaten")
    st.radio(
        "Wachstum",
        options=("ja", "nein"),
        key=baue_formularschluessel(material.id, "wachstum"),
        horizontal=True,
    )

    if hole_wachstum(material.id):
        zeige_keimeingabe(material.id)

    button_spalte_links, button_spalte_rechts = st.columns(2)

    with button_spalte_links:
        if st.button(
            "Kulturdaten speichern",
            type="secondary",
            use_container_width=True,
        ):
            if speichere_kulturdaten(material):
                aktuelle_beurteilung = None

    with button_spalte_rechts:
        if st.button(
            "Beurteilung berechnen",
            type="primary",
            use_container_width=True,
        ):
            berechnete_beurteilung = berechne_und_speichere_beurteilung(material)
            if berechnete_beurteilung is not None:
                aktuelle_beurteilung = berechnete_beurteilung

    zeige_vorschau(material.id)
    zeige_beurteilung(aktuelle_beurteilung)


main()

