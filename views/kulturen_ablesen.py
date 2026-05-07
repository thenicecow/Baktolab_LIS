"""Streamlit-Seite fuer die Funktion ``Kulturen ablesen`` mit Bildbestaetigung fuer Keimzahlen."""

from __future__ import annotations

from pathlib import Path
import runpy

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
    aktiviere_befund,
    deaktiviere_befund,
    deaktiviere_kulturen_ablesen,
    hat_gueltige_befund_route,
    hole_material_id_fuer_kulturen_ablesen,
    ist_befund_aktiv,
)


ROLLEN: tuple[str, ...] = ("pathogen", "kontaminante")
KEIMGRUPPEN: tuple[str, ...] = ("gramnegative_staebchen", "gpk_gps", "andere")
KEIMZAHL_CODES: tuple[str, ...] = tuple(
    code for code in ("k4", "p4", "p5", "g5") if code in ERLAUBTE_KEIMZAHL_CODES
)

PROJEKTWURZEL = Path(__file__).resolve().parent.parent
REFERENZBILD_ORDNER = PROJEKTWURZEL / "assets" / "referenzbilder"
REFERENZBILD_DATEIBASEN: dict[str, str] = {
    "k4": "k4",
    "p4": "p4",
    "p5": "p5",
    "g5": "g5",
}
REFERENZBILD_TITEL: dict[str, str] = {
    "k4": "Referenzbild K4",
    "p4": "Referenzbild P4",
    "p5": "Referenzbild P5",
    "g5": "Referenzbild G5",
}
REFERENZBILD_ENDUNGEN: tuple[str, ...] = (".png", ".jpg", ".jpeg")
REFERENZBILD_BREITE_PIXEL = 140


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


def zeige_befund_innerhalb_kulturen_ablesen() -> None:
    """Rendert die interne Befundansicht innerhalb der bestehenden Kulturseite."""
    befundansicht_pfad = Path(__file__).with_name("befund.py")
    runpy.run_path(str(befundansicht_pfad), run_name="__main__")


def baue_formularschluessel(material_id: str, feldname: str) -> str:
    """Erzeugt einen stabilen Session-State-Schluessel fuer das lokale Kulturformular."""
    return f"kulturen_ablesen_{material_id}_{feldname}"


def baue_keimzahl_bestaetigt_schluessel(material_id: str, index: int) -> str:
    """Erzeugt den Session-State-Schluessel fuer den Bestaetigungsstatus einer Keimzahl."""
    return baue_formularschluessel(material_id, f"keimzahl_bestaetigt_{index}")


def baue_bestaetigte_keimzahl_schluessel(material_id: str, index: int) -> str:
    """Erzeugt den Session-State-Schluessel fuer die zuletzt bestaetigte Keimzahl."""
    return baue_formularschluessel(material_id, f"bestaetigte_keimzahl_code_{index}")


def baue_referenzbild_anzeigen_schluessel(material_id: str, index: int) -> str:
    """Erzeugt den Session-State-Schluessel fuer die Sichtbarkeit des Referenzbilds."""
    return baue_formularschluessel(material_id, f"referenzbild_anzeigen_{index}")


def hole_ausgewaehlte_keimzahl(material_id: str, index: int) -> str:
    """Liest die aktuell ausgewaehlte Keimzahl eines Keims aus dem Session State."""
    wert = st.session_state.get(
        baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
        KEIMZAHL_CODES[0],
    )

    if not isinstance(wert, str):
        return KEIMZAHL_CODES[0]

    bereinigt = wert.strip()
    if bereinigt not in KEIMZAHL_CODES:
        return KEIMZAHL_CODES[0]

    return bereinigt


def hole_bestaetigte_keimzahl(material_id: str, index: int) -> str | None:
    """Liest die aktuell bestaetigte Keimzahl eines Keims aus dem Session State."""
    wert = st.session_state.get(baue_bestaetigte_keimzahl_schluessel(material_id, index))

    if not isinstance(wert, str):
        return None

    bereinigt = wert.strip()
    if bereinigt not in KEIMZAHL_CODES:
        return None

    return bereinigt


def ist_keimzahl_bestaetigt(material_id: str, index: int) -> bool:
    """Prueft, ob die aktuell ausgewaehlte Keimzahl dieses Keims bestaetigt wurde."""
    return bool(
        st.session_state.get(
            baue_keimzahl_bestaetigt_schluessel(material_id, index),
            False,
        )
    )


def soll_referenzbild_angezeigt_werden(material_id: str, index: int) -> bool:
    """Liefert, ob das Referenzbild fuer einen Keim aktuell sichtbar sein soll."""
    schluessel = baue_referenzbild_anzeigen_schluessel(material_id, index)

    if schluessel not in st.session_state:
        return True

    return bool(st.session_state.get(schluessel, False))


def hole_referenzbild_pfad(keimzahl_code: str) -> Path:
    """Sucht das Referenzbild zur gewaehlten Keimzahl im festen Projektordner."""
    dateibasis = REFERENZBILD_DATEIBASEN.get(keimzahl_code, keimzahl_code)
    basis_pfad = REFERENZBILD_ORDNER / dateibasis

    for endung in REFERENZBILD_ENDUNGEN:
        kandidat = basis_pfad.with_suffix(endung)
        if kandidat.exists():
            return kandidat

    return basis_pfad.with_suffix(".png")


def setze_keimzahl_als_unbestaetigt(material_id: str, index: int) -> None:
    """Setzt eine geaenderte Keimzahl sofort in den unbestaetigten Zustand zurueck."""
    st.session_state[baue_keimzahl_bestaetigt_schluessel(material_id, index)] = False
    st.session_state[baue_bestaetigte_keimzahl_schluessel(material_id, index)] = None
    st.session_state[baue_referenzbild_anzeigen_schluessel(material_id, index)] = True


def bestaetige_keimzahl(material_id: str, index: int) -> None:
    """Uebernimmt die aktuell ausgewaehlte Keimzahl als bestaetigten Wert."""
    ausgewaehlte_keimzahl = hole_ausgewaehlte_keimzahl(material_id, index)
    st.session_state[baue_bestaetigte_keimzahl_schluessel(material_id, index)] = (
        ausgewaehlte_keimzahl
    )
    st.session_state[baue_keimzahl_bestaetigt_schluessel(material_id, index)] = True
    st.session_state[baue_referenzbild_anzeigen_schluessel(material_id, index)] = False


def lehne_keimzahl_ab(material_id: str, index: int) -> None:
    """Belaesst die Auswahl in einem unbestaetigten Zustand, damit sie korrigiert werden kann."""
    st.session_state[baue_keimzahl_bestaetigt_schluessel(material_id, index)] = False
    st.session_state[baue_bestaetigte_keimzahl_schluessel(material_id, index)] = None
    st.session_state[baue_referenzbild_anzeigen_schluessel(material_id, index)] = False


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
        st.session_state[baue_keimzahl_bestaetigt_schluessel(material.id, index)] = True
        st.session_state[baue_bestaetigte_keimzahl_schluessel(material.id, index)] = (
            keim.keimzahl_code
        )
        st.session_state[baue_referenzbild_anzeigen_schluessel(material.id, index)] = False

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


def hole_aktuellen_keimeintrag(material_id: str, index: int) -> dict[str, object]:
    """Liest einen einzelnen lokalen Keimeintrag aus dem Session State."""
    keim_id = st.session_state.get(baue_formularschluessel(material_id, f"keim_id_{index}"), "")
    rolle = st.session_state.get(
        baue_formularschluessel(material_id, f"rolle_{index}"),
        ROLLEN[0],
    )
    keimgruppe = st.session_state.get(
        baue_formularschluessel(material_id, f"keimgruppe_{index}"),
        KEIMGRUPPEN[0],
    )

    ausgewaehlte_keimzahl = hole_ausgewaehlte_keimzahl(material_id, index)
    bestaetigte_keimzahl = hole_bestaetigte_keimzahl(material_id, index)
    keimzahl_bestaetigt = ist_keimzahl_bestaetigt(material_id, index) and (
        bestaetigte_keimzahl is not None
    )

    return {
        "keim_id": str(keim_id).strip(),
        "keimzahl_code": bestaetigte_keimzahl or "",
        "ausgewaehlte_keimzahl_code": ausgewaehlte_keimzahl,
        "keimzahl_bestaetigt": keimzahl_bestaetigt,
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
            "unbestaetigte_keime": [],
            "beurteilung": None,
        }

    keime: list[dict[str, str]] = []
    unbestaetigte_keime: list[dict[str, str]] = []

    for index in range(hole_keimanzahl(material_id)):
        keimeintrag = hole_aktuellen_keimeintrag(material_id, index)

        keim_id = str(keimeintrag["keim_id"]).strip()
        if not keim_id:
            continue

        rolle = str(keimeintrag["rolle"]).strip()
        keimgruppe = str(keimeintrag["keimgruppe"]).strip()
        ausgewaehlte_keimzahl = str(keimeintrag["ausgewaehlte_keimzahl_code"]).strip()

        if bool(keimeintrag["keimzahl_bestaetigt"]):
            keime.append(
                {
                    "keim_id": keim_id,
                    "keimzahl_code": str(keimeintrag["keimzahl_code"]).strip(),
                    "rolle": rolle,
                    "keimgruppe": keimgruppe,
                }
            )
            continue

        unbestaetigte_keime.append(
            {
                "keim_id": keim_id,
                "ausgewaehlte_keimzahl_code": ausgewaehlte_keimzahl,
                "rolle": rolle,
                "keimgruppe": keimgruppe,
            }
        )

    return {
        "wachstum": True,
        "keime": keime,
        "unbestaetigte_keime": unbestaetigte_keime,
        "beurteilung": None,
    }


def baue_kulturdaten_aus_formularvorschau(
    material: Material,
    beurteilung: str | None,
) -> Kulturdaten | None:
    """Erzeugt Kulturdaten aus der aktuellen Formulareingabe."""
    vorschau = hole_formularvorschau(material.id)

    unbestaetigte_keime = vorschau.get("unbestaetigte_keime", [])
    if isinstance(unbestaetigte_keime, list) and unbestaetigte_keime:
        st.error(
            "Bitte bestaetige alle ausgewaehlten Keimzahlen anhand der Referenzbilder, "
            "bevor du speicherst oder die Beurteilung berechnest."
        )
        return None

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


def zeige_keimzahl_bestaetigung(material_id: str, index: int) -> None:
    """Zeigt Referenzbild und Bestaetigungslogik fuer die gewaehlte Keimzahl eines Keims."""
    keim_id = st.session_state.get(baue_formularschluessel(material_id, f"keim_id_{index}"), "")
    if not isinstance(keim_id, str) or not keim_id.strip():
        return

    ausgewaehlte_keimzahl = hole_ausgewaehlte_keimzahl(material_id, index)
    referenzbild_pfad = hole_referenzbild_pfad(ausgewaehlte_keimzahl)
    referenzbild_vorhanden = referenzbild_pfad.exists()
    referenzbild_titel = REFERENZBILD_TITEL.get(
        ausgewaehlte_keimzahl,
        f"Referenzbild {ausgewaehlte_keimzahl.upper()}",
    )
    referenzbild_anzeigen = soll_referenzbild_angezeigt_werden(material_id, index)

    with st.container(border=True):
        st.markdown("**Visuelle Pruefung der Keimzahl**")
        st.caption(
            "Bitte pruefe die ausgewaehlte Keimzahl anhand des Referenzbilds und "
            "bestaetige oder lehne sie anschliessend ab."
        )

        if ist_keimzahl_bestaetigt(material_id, index):
            st.success(
                f"Die Keimzahl {ausgewaehlte_keimzahl.upper()} ist bestaetigt."
            )
        else:
            st.warning(
                f"Die Keimzahl {ausgewaehlte_keimzahl.upper()} ist noch nicht bestaetigt "
                "und wird noch nicht gespeichert oder beurteilt."
            )

        if referenzbild_anzeigen and referenzbild_vorhanden:
            st.image(
                str(referenzbild_pfad),
                caption=referenzbild_titel,
                width=REFERENZBILD_BREITE_PIXEL,
            )
        elif referenzbild_anzeigen and not referenzbild_vorhanden:
            st.error(
                "Das passende Referenzbild wurde nicht gefunden. "
                f"Erwarteter Dateipfad: {referenzbild_pfad}"
            )

        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            if st.button(
                "Bestaetigen",
                key=baue_formularschluessel(material_id, f"keimzahl_bestaetigen_{index}"),
                type="primary",
                use_container_width=True,
                disabled=not referenzbild_vorhanden,
            ):
                bestaetige_keimzahl(material_id, index)
                st.rerun()

        with rechte_spalte:
            if st.button(
                "Ablehnen",
                key=baue_formularschluessel(material_id, f"keimzahl_ablehnen_{index}"),
                use_container_width=True,
            ):
                lehne_keimzahl_ab(material_id, index)
                st.rerun()


def zeige_keimeingabe(material_id: str) -> None:
    """Rendert die Eingabemaske fuer eine variable Anzahl Keime."""
    st.markdown("**Keime erfassen**")

    for index in range(hole_keimanzahl(material_id)):
        with st.container(border=True):
            st.caption(f"Keim {index + 1}")

            st.text_input(
                "Keim-ID",
                key=baue_formularschluessel(material_id, f"keim_id_{index}"),
                placeholder="z. B. Escherichia coli",
            )

            linke_spalte, mittlere_spalte, rechte_spalte = st.columns(3)

            with linke_spalte:
                st.selectbox(
                    "Keimzahl",
                    options=list(KEIMZAHL_CODES),
                    key=baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
                    on_change=setze_keimzahl_als_unbestaetigt,
                    args=(material_id, index),
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

            zeige_keimzahl_bestaetigung(material_id, index)

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

        keime = vorschau.get("keime", [])
        unbestaetigte_keime = vorschau.get("unbestaetigte_keime", [])

        if not isinstance(keime, list):
            keime = []
        if not isinstance(unbestaetigte_keime, list):
            unbestaetigte_keime = []

        if not keime and not unbestaetigte_keime:
            if vorschau["wachstum"]:
                st.info("Aktuell sind noch keine vollstaendigen Keimeintraege erfasst.")
            else:
                st.info("Es ist aktuell 'kein Wachstum' ausgewaehlt.")
            return

        if keime:
            st.markdown("**Bestaetigte Keime**")
            st.dataframe(
                pd.DataFrame(keime).rename(
                    columns={
                        "keim_id": "Keim-ID",
                        "keimzahl_code": "Bestaetigte Keimzahl",
                        "rolle": "Rolle",
                        "keimgruppe": "Keimgruppe",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

        if unbestaetigte_keime:
            st.warning("Fuer mindestens einen Keim fehlt noch die Bestaetigung der Keimzahl.")
            st.dataframe(
                pd.DataFrame(unbestaetigte_keime).rename(
                    columns={
                        "keim_id": "Keim-ID",
                        "ausgewaehlte_keimzahl_code": "Ausgewaehlte Keimzahl",
                        "rolle": "Rolle",
                        "keimgruppe": "Keimgruppe",
                    }
                ),
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
    if hat_gueltige_befund_route():
        zeige_befund_innerhalb_kulturen_ablesen()
        return

    st.title("Kulturen ablesen")
    st.info(
        "Diese Seite ist aktuell nur fuer Urin mit der Analyse "
        "'Allgemeine Bakteriologie' vorgesehen. Kulturdaten und berechnete "
        "Beurteilungen werden materialbezogen gespeichert."
    )

    if ist_befund_aktiv():
        deaktiviere_befund()
        st.warning(
            "Die Befundansicht konnte nicht geoeffnet werden, "
            "weil kein gueltiger Materialkontext vorhanden ist."
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
            "Diese Beurteilung wird aktuell nur fuer Material vom Typ 'Urin' "
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

    button_spalte_links, button_spalte_mitte, button_spalte_rechts = st.columns(3)

    with button_spalte_links:
        if st.button(
            "Kulturdaten speichern",
            type="secondary",
            use_container_width=True,
        ):
            if speichere_kulturdaten(material):
                aktuelle_beurteilung = None

    with button_spalte_mitte:
        if st.button(
            "Beurteilung berechnen",
            type="secondary",
            use_container_width=True,
        ):
            berechnete_beurteilung = berechne_und_speichere_beurteilung(material)
            if berechnete_beurteilung is not None:
                aktuelle_beurteilung = berechnete_beurteilung

    with button_spalte_rechts:
        if st.button(
            "Validieren",
            type="primary",
            use_container_width=True,
        ):
            berechnete_beurteilung = validiere_und_oeffne_befund(material)
            if berechnete_beurteilung is not None:
                aktuelle_beurteilung = berechnete_beurteilung

    zeige_vorschau(material.id)
    zeige_beurteilung(aktuelle_beurteilung)


main()
