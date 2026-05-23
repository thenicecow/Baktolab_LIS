"""Hilfsfunktionen fuer Formularzustand und Teilansichten der Seite ``Kulturen ablesen``."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from domaene import ERLAUBTE_KEIMZAHL_CODES, Kulturdaten, Material
from functions.kulturen.ablesen import (
    baue_kulturdaten_aus_formularwerten,
    hole_kulturdaten_oder_standard,
)
from functions.kulturen.beurteilung import UrinBeurteilung


ROLLEN: tuple[str, ...] = ("pathogen", "kontaminante")
KEIMZAHL_CODES: tuple[str, ...] = tuple(
    code for code in ("k4", "p4", "p5", "g5") if code in ERLAUBTE_KEIMZAHL_CODES
)
KEIM_ROLLEN_NACH_KEIM: dict[str, str] = {
    "Escherichia coli": "pathogen",
    "Klebsiella pneumoniae": "pathogen",
    "Proteus mirabilis": "pathogen",
    "Enterococcus faecalis": "kontaminante",
    "Staphylococcus saprophyticus": "pathogen",
    "Pseudomonas aeruginosa": "pathogen",
    "Enterobacter cloacae complex": "pathogen",
    "Vergrünende Streptokokken": "kontaminante",
    "Koagulase negative Staphylokokken": "kontaminante",
    "Enterococcus faecium": "pathogen",
}
VORDEFINIERTE_KEIME: tuple[str, ...] = tuple(KEIM_ROLLEN_NACH_KEIM)
SONSTIGER_KEIM_OPTION = "Sonstiger Keim"
KEIM_ID_AUSWAHL_OPTIONEN: tuple[str, ...] = VORDEFINIERTE_KEIME + (SONSTIGER_KEIM_OPTION,)
VORDEFINIERTE_KEIME_NACH_CASEFOLD: dict[str, str] = {
    keim.casefold(): keim for keim in VORDEFINIERTE_KEIME
}

PROJEKTWURZEL = Path(__file__).resolve().parent.parent.parent
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


def hat_verfuegbare_keimzahl_codes() -> bool:
    """Prueft, ob mindestens ein gueltiger Keimzahl-Code verfuegbar ist."""
    return bool(KEIMZAHL_CODES)


def hole_standard_keimzahl_code() -> str:
    """Liefert defensiv einen Standard-Keimzahl-Code fuer Formularfelder."""
    if not KEIMZAHL_CODES:
        return ""

    return KEIMZAHL_CODES[0]


def baue_formularschluessel(material_id: str, feldname: str) -> str:
    """Erzeugt einen stabilen Session-State-Schluessel fuer das Kulturformular."""
    return f"kulturen_ablesen_{material_id}_{feldname}"


def baue_keimauswahl_schluessel(material_id: str, index: int) -> str:
    """Erzeugt den Session-State-Schluessel fuer die Dropdown-Auswahl eines Keims."""
    return baue_formularschluessel(material_id, f"keimauswahl_{index}")


def baue_sonstiger_keimname_schluessel(material_id: str, index: int) -> str:
    """Erzeugt den Session-State-Schluessel fuer den Freitext bei sonstigem Keim."""
    return baue_formularschluessel(material_id, f"sonstiger_keimname_{index}")


def bereinige_textwert(wert: object) -> str:
    """Bereinigt einen beliebigen Eingabewert defensiv zu einem Text."""
    if not isinstance(wert, str):
        return ""

    return wert.strip()


def ordne_keimwert_fuer_auswahl_zu(keimwert: str) -> tuple[str | None, str]:
    """Ordnet einen vorhandenen Keimwert der Dropdown-Auswahl und dem Freitext zu."""
    bereinigt = bereinige_textwert(keimwert)
    if not bereinigt:
        return None, ""

    if bereinigt.casefold() == SONSTIGER_KEIM_OPTION.casefold():
        return SONSTIGER_KEIM_OPTION, bereinigt

    vordefinierter_keim = VORDEFINIERTE_KEIME_NACH_CASEFOLD.get(bereinigt.casefold())
    if vordefinierter_keim is not None:
        return vordefinierter_keim, ""

    return SONSTIGER_KEIM_OPTION, bereinigt


def hole_ausgewaehlte_keimauswahl(material_id: str, index: int) -> str | None:
    """Liest die aktuell ausgewaehlte Keimoption fuer einen Keim."""
    auswahl_schluessel = baue_keimauswahl_schluessel(material_id, index)

    if auswahl_schluessel not in st.session_state:
        keim_id = bereinige_textwert(
            st.session_state.get(
                baue_formularschluessel(material_id, f"keim_id_{index}"),
                "",
            )
        )
        keimauswahl, _sonstiger_keimname = ordne_keimwert_fuer_auswahl_zu(keim_id)
        return keimauswahl

    bereinigt = bereinige_textwert(st.session_state.get(auswahl_schluessel))
    if not bereinigt:
        return None

    if bereinigt.casefold() == SONSTIGER_KEIM_OPTION.casefold():
        return SONSTIGER_KEIM_OPTION

    return VORDEFINIERTE_KEIME_NACH_CASEFOLD.get(bereinigt.casefold())


def hole_sonstigen_keimnamen(material_id: str, index: int) -> str:
    """Liest den Freitext fuer einen sonstigen Keim defensiv aus dem Session State."""
    sonstiger_keimname_schluessel = baue_sonstiger_keimname_schluessel(material_id, index)

    if sonstiger_keimname_schluessel in st.session_state:
        return bereinige_textwert(st.session_state.get(sonstiger_keimname_schluessel))

    keim_id = bereinige_textwert(
        st.session_state.get(
            baue_formularschluessel(material_id, f"keim_id_{index}"),
            "",
        )
    )
    keimauswahl, sonstiger_keimname = ordne_keimwert_fuer_auswahl_zu(keim_id)
    if keimauswahl == SONSTIGER_KEIM_OPTION:
        return sonstiger_keimname

    return ""


def hole_endgueltigen_keimnamen(material_id: str, index: int) -> str:
    """Liefert den endgueltigen Keimnamen aus Dropdown und optionalem Freitext."""
    keimauswahl = hole_ausgewaehlte_keimauswahl(material_id, index)
    auswahl_schluessel = baue_keimauswahl_schluessel(material_id, index)

    if keimauswahl is None:
        if auswahl_schluessel in st.session_state:
            return ""

        return bereinige_textwert(
            st.session_state.get(
                baue_formularschluessel(material_id, f"keim_id_{index}"),
                "",
            )
        )

    if keimauswahl == SONSTIGER_KEIM_OPTION:
        return hole_sonstigen_keimnamen(material_id, index)

    return keimauswahl


def hole_automatische_rolle_fuer_keimauswahl(keimauswahl: str | None) -> str | None:
    """Liefert die fachlich vorgegebene Rolle fuer einen bekannten Keim."""
    if not isinstance(keimauswahl, str):
        return None

    bereinigt = keimauswahl.strip()
    if not bereinigt or bereinigt.casefold() == SONSTIGER_KEIM_OPTION.casefold():
        return None

    vordefinierter_keim = VORDEFINIERTE_KEIME_NACH_CASEFOLD.get(bereinigt.casefold())
    if vordefinierter_keim is None:
        return None

    return KEIM_ROLLEN_NACH_KEIM.get(vordefinierter_keim)


def synchronisiere_keim_id_aus_eingabe(material_id: str, index: int) -> str:
    """Synchronisiert den endgueltigen Keimnamen in das bisherige Feld ``keim_id``."""
    keim_id = hole_endgueltigen_keimnamen(material_id, index)
    st.session_state[baue_formularschluessel(material_id, f"keim_id_{index}")] = keim_id
    return keim_id


def hole_rolle_aus_eingabe(material_id: str, index: int) -> str:
    """Liest die fachlich gueltige Rolle ohne den Widget-State nachtraeglich zu aendern."""
    rollenschluessel = baue_formularschluessel(material_id, f"rolle_{index}")
    keimauswahl = hole_ausgewaehlte_keimauswahl(material_id, index)
    automatische_rolle = hole_automatische_rolle_fuer_keimauswahl(keimauswahl)

    if automatische_rolle is not None:
        return automatische_rolle

    aktuelle_rolle = bereinige_textwert(st.session_state.get(rollenschluessel))

    if keimauswahl == SONSTIGER_KEIM_OPTION:
        if aktuelle_rolle in ROLLEN:
            return aktuelle_rolle
        return ROLLEN[0]

    if aktuelle_rolle in ROLLEN:
        return aktuelle_rolle

    return ""


def synchronisiere_rolle_aus_eingabe(material_id: str, index: int) -> str:
    """Bereitet die Rolle passend zur aktuellen Keimauswahl vor dem Rendern des Widgets vor."""
    rollenschluessel = baue_formularschluessel(material_id, f"rolle_{index}")
    rolle = hole_rolle_aus_eingabe(material_id, index)

    if rolle and st.session_state.get(rollenschluessel) != rolle:
        st.session_state[rollenschluessel] = rolle

    return rolle


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
    standard_keimzahl_code = hole_standard_keimzahl_code()
    if not standard_keimzahl_code:
        return ""

    wert = st.session_state.get(
        baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
        standard_keimzahl_code,
    )

    if not isinstance(wert, str):
        return standard_keimzahl_code

    bereinigt = wert.strip()
    if bereinigt not in KEIMZAHL_CODES:
        return standard_keimzahl_code

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
        keimauswahl, sonstiger_keimname = ordne_keimwert_fuer_auswahl_zu(keim.keim_id)
        automatische_rolle = hole_automatische_rolle_fuer_keimauswahl(keimauswahl)
        rolle = bereinige_textwert(keim.rolle)

        if automatische_rolle is not None:
            rolle = automatische_rolle
        elif rolle not in ROLLEN:
            rolle = ROLLEN[0]

        st.session_state[baue_formularschluessel(material.id, f"keim_id_{index}")] = keim.keim_id
        if keimauswahl is not None:
            st.session_state[baue_keimauswahl_schluessel(material.id, index)] = keimauswahl
        st.session_state[
            baue_sonstiger_keimname_schluessel(material.id, index)
        ] = sonstiger_keimname
        st.session_state[baue_formularschluessel(material.id, f"keimzahl_code_{index}")] = (
            keim.keimzahl_code
        )
        st.session_state[baue_formularschluessel(material.id, f"rolle_{index}")] = rolle
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
    keim_id = synchronisiere_keim_id_aus_eingabe(material_id, index)
    rolle = hole_rolle_aus_eingabe(material_id, index)

    ausgewaehlte_keimzahl = hole_ausgewaehlte_keimzahl(material_id, index)
    bestaetigte_keimzahl = hole_bestaetigte_keimzahl(material_id, index)
    keimzahl_bestaetigt = ist_keimzahl_bestaetigt(material_id, index) and (
        bestaetigte_keimzahl is not None
    )

    return {
        "keim_id": keim_id,
        "keimzahl_code": bestaetigte_keimzahl or "",
        "ausgewaehlte_keimzahl_code": ausgewaehlte_keimzahl,
        "keimzahl_bestaetigt": keimzahl_bestaetigt,
        "rolle": rolle,
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
        ausgewaehlte_keimzahl = str(keimeintrag["ausgewaehlte_keimzahl_code"]).strip()

        if bool(keimeintrag["keimzahl_bestaetigt"]):
            keime.append(
                {
                    "keim_id": keim_id,
                    "keimzahl_code": str(keimeintrag["keimzahl_code"]).strip(),
                    "rolle": rolle,
                }
            )
            continue

        unbestaetigte_keime.append(
            {
                "keim_id": keim_id,
                "ausgewaehlte_keimzahl_code": ausgewaehlte_keimzahl,
                "rolle": rolle,
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


def zeige_keimzahl_bestaetigung(material_id: str, index: int) -> None:
    """Zeigt Referenzbild und Bestaetigungslogik fuer die gewaehlte Keimzahl eines Keims."""
    keim_id = synchronisiere_keim_id_aus_eingabe(material_id, index)
    if not keim_id:
        return

    ausgewaehlte_keimzahl = hole_ausgewaehlte_keimzahl(material_id, index)
    if not ausgewaehlte_keimzahl:
        return

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
            st.success(f"Die Keimzahl {ausgewaehlte_keimzahl.upper()} ist bestätigt.")
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


def zeige_rollenauswahl(material_id: str, index: int) -> None:
    """Rendert die Rollenauswahl passend zur aktuellen Keimauswahl."""
    rollenschluessel = baue_formularschluessel(material_id, f"rolle_{index}")
    keimauswahl = hole_ausgewaehlte_keimauswahl(material_id, index)
    automatische_rolle = hole_automatische_rolle_fuer_keimauswahl(keimauswahl)

    synchronisiere_rolle_aus_eingabe(material_id, index)

    if automatische_rolle is not None:
        st.selectbox(
            "Rolle",
            options=list(ROLLEN),
            key=rollenschluessel,
            disabled=True,
        )
        st.caption("Rolle wird fuer diesen Keim automatisch gesetzt.")
        return

    if keimauswahl == SONSTIGER_KEIM_OPTION:
        st.selectbox(
            "Rolle",
            options=list(ROLLEN),
            key=rollenschluessel,
        )
        return

    st.selectbox(
        "Rolle",
        options=list(ROLLEN),
        key=rollenschluessel,
        index=None,
        placeholder="Bitte zuerst Keim auswaehlen",
        disabled=True,
    )
    st.caption("Die Rolle wird nach der Keimauswahl gesetzt.")


def zeige_keimeingabe(material_id: str) -> None:
    """Rendert die Eingabemaske fuer eine variable Anzahl Keime."""
    st.markdown("**Keime erfassen**")

    for index in range(hole_keimanzahl(material_id)):
        with st.container(border=True):
            st.caption(f"Keim {index + 1}")

            st.selectbox(
                "Keim-ID",
                options=list(KEIM_ID_AUSWAHL_OPTIONEN),
                key=baue_keimauswahl_schluessel(material_id, index),
                index=None,
                placeholder="Bitte Keim auswaehlen",
            )

            if hole_ausgewaehlte_keimauswahl(material_id, index) == SONSTIGER_KEIM_OPTION:
                st.text_input(
                    "Keimname eingeben",
                    key=baue_sonstiger_keimname_schluessel(material_id, index),
                    placeholder="z. B. Lactobacillus spp.",
                )

            synchronisiere_keim_id_aus_eingabe(material_id, index)

            linke_spalte, rechte_spalte = st.columns(2)

            with linke_spalte:
                st.selectbox(
                    "Keimzahl",
                    options=list(KEIMZAHL_CODES),
                    key=baue_formularschluessel(material_id, f"keimzahl_code_{index}"),
                    on_change=setze_keimzahl_als_unbestaetigt,
                    args=(material_id, index),
                )

            with rechte_spalte:
                zeige_rollenauswahl(material_id, index)

            zeige_keimzahl_bestaetigung(material_id, index)

    if st.button(
        "Weiteren Keim hinzufuegen",
        icon=":material/add:",
        use_container_width=True,
    ):
        erhoehe_keimanzahl(material_id)
        st.rerun()


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
                st.info("Aktuell sind noch keine vollständigen Keimeinträge erfasst.")
            else:
                st.info("Es ist aktuell 'kein Wachstum' ausgewählt.")
            return

        if keime:
            st.markdown("**Bestaetigte Keime**")
            st.dataframe(
                pd.DataFrame(keime).rename(
                    columns={
                        "keim_id": "Keim-ID",
                        "keimzahl_code": "Bestaetigte Keimzahl",
                        "rolle": "Rolle",
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
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


def zeige_beurteilung(beurteilung: UrinBeurteilung | None) -> None:
    """Zeigt das aktuell vorhandene Beurteilungsergebnis uebersichtlich an."""
    st.subheader("Beurteilung")

    if beurteilung is None:
        st.info("Für dieses Material ist aktuell noch keine berechnete Beurteilung gespeichert.")
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