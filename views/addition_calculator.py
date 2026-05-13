"""Streamlit-Seite fuer das Resistenzmonitoring mit sauber getrenntem Seitenablauf."""

from __future__ import annotations

from datetime import datetime
from typing import cast

import pandas as pd
import pytz
import streamlit as st

import functions.mdr_rules as mdr_regeln
import functions.resistenzmonitoring as resistenz_daten
import functions.resistenzmonitoring_ansicht as resistenz_ansicht
from functions.addition import percent, subtract
from utils.data_manager import DataManager


RunId = tuple[str, str, str, int, int]

VERLAUF_DF_SCHLUESSEL = "resistenzmonitoring_verlauf_df"
VERLAUF_BENUTZER_SCHLUESSEL = "resistenzmonitoring_benutzer"
LETZTE_SPEICHERUNG_SCHLUESSEL = "resistenzmonitoring_last_saved"
ERGEBNIS_SCHLUESSEL = "resistenzmonitoring_result"

data_manager = DataManager(
    fs_protocol="webdav",
    fs_root_folder="BMLD_APP_DATA",
)


def hole_aktuellen_benutzernamen() -> str | None:
    """Liest den aktuell angemeldeten Benutzernamen defensiv aus dem Session State."""
    benutzername = st.session_state.get("username")
    if not isinstance(benutzername, str):
        return None

    bereinigt = benutzername.strip()
    return bereinigt or None


def hole_gespeichertes_ergebnis() -> resistenz_ansicht.ResistenzErgebnis | None:
    """Liest das zuletzt berechnete Ergebnis typisiert aus dem Session State."""
    ergebnis = st.session_state.get(ERGEBNIS_SCHLUESSEL)
    if not isinstance(ergebnis, dict):
        return None

    return cast(resistenz_ansicht.ResistenzErgebnis, ergebnis)


def setze_gespeichertes_ergebnis(ergebnis: resistenz_ansicht.ResistenzErgebnis) -> None:
    """Speichert das aktuelle Berechnungsergebnis im Session State."""
    st.session_state[ERGEBNIS_SCHLUESSEL] = ergebnis


def entferne_gespeichertes_ergebnis() -> None:
    """Entfernt ein vorhandenes Berechnungsergebnis aus dem Session State."""
    st.session_state.pop(ERGEBNIS_SCHLUESSEL, None)


def hole_letzte_speicherung() -> RunId | None:
    """Liest die Kennung der zuletzt gespeicherten Berechnung aus dem Session State."""
    letzte_speicherung = st.session_state.get(LETZTE_SPEICHERUNG_SCHLUESSEL)
    if not isinstance(letzte_speicherung, tuple) or len(letzte_speicherung) != 5:
        return None

    return cast(RunId, letzte_speicherung)


def setze_letzte_speicherung(run_id: RunId) -> None:
    """Speichert die Kennung der zuletzt persistierten Berechnung."""
    st.session_state[LETZTE_SPEICHERUNG_SCHLUESSEL] = run_id


def baue_run_id(
    periode: str,
    keim: str,
    antibiotikum: str,
    total: int,
    resistant: int,
) -> RunId:
    """Erzeugt eine stabile Kennung fuer eine konkrete Berechnung."""
    return (periode, keim, antibiotikum, int(total), int(resistant))


def hole_zeitpunkt() -> str:
    """Liefert den aktuellen Schweizer Zeitstempel fuer Ergebnis und Verlauf."""
    return datetime.now(pytz.timezone("Europe/Zurich")).strftime("%d.%m.%Y %H:%M")


def initialisiere_resistenzmonitoring() -> None:
    """Laedt und normalisiert die benutzerspezifischen Verlaufsdaten bei Bedarf neu."""
    aktueller_benutzer = hole_aktuellen_benutzernamen()
    geladener_benutzer = st.session_state.get(VERLAUF_BENUTZER_SCHLUESSEL)

    if (
        VERLAUF_DF_SCHLUESSEL in st.session_state
        and geladener_benutzer == aktueller_benutzer
    ):
        return

    if aktueller_benutzer is None:
        verlauf = resistenz_daten.hole_leeres_verlaufs_dataframe()
    else:
        geladene_daten = data_manager.load_user_data(
            resistenz_daten.VERLAUF_DATEIPFAD,
            initial_value=resistenz_daten.hole_leeres_verlaufs_dataframe(),
        )
        verlauf = resistenz_daten.normalisiere_verlaufsdaten(geladene_daten)

    st.session_state[VERLAUF_DF_SCHLUESSEL] = verlauf
    st.session_state[VERLAUF_BENUTZER_SCHLUESSEL] = aktueller_benutzer
    st.session_state[LETZTE_SPEICHERUNG_SCHLUESSEL] = None
    entferne_gespeichertes_ergebnis()


def hole_verlaufsdaten() -> pd.DataFrame:
    """Liefert die aktuell im Zustand gehaltenen Verlaufsdaten normalisiert zurueck."""
    daten = st.session_state.get(
        VERLAUF_DF_SCHLUESSEL,
        resistenz_daten.hole_leeres_verlaufs_dataframe(),
    )
    return resistenz_daten.normalisiere_verlaufsdaten(daten)


def setze_verlaufsdaten(verlaufsdaten: pd.DataFrame) -> None:
    """Aktualisiert die gespeicherten Verlaufsdaten im Session State konsistent."""
    st.session_state[VERLAUF_DF_SCHLUESSEL] = resistenz_daten.normalisiere_verlaufsdaten(
        verlaufsdaten
    )


def speichere_verlaufsdaten(verlaufsdaten: pd.DataFrame) -> None:
    """Persistiert benutzerspezifische Verlaufsdaten ueber den vorhandenen Datenmanager."""
    data_manager.save_user_data(
        resistenz_daten.normalisiere_verlaufsdaten(verlaufsdaten),
        resistenz_daten.VERLAUF_DATEIPFAD,
    )


def zeige_fachliche_abgrenzung() -> None:
    """Zeigt die fachliche Abgrenzung des aktuellen Resistenzmonitorings an."""
    keime = ", ".join(mdr_regeln.UNTERSTUETZTE_KEIME)
    antibiotika = ", ".join(mdr_regeln.UNTERSTUETZTE_ANTIBIOTIKA)

    st.info(
        "Dieses Resistenzmonitoring ist ein separates Demo-Modul mit manueller Eingabe. "
        "Es ist aktuell nicht direkt mit patientenbezogenen Kulturdaten verknuepft."
    )
    st.caption(
        f"Unterstuetzte Keime: {keime}. Unterstuetzte Antibiotika: {antibiotika}."
    )


def validiere_berechnungseingaben(total: int, resistant: int) -> str | None:
    """Validiert die Kerneingaben fuer die Resistenzberechnung."""
    if resistant > total:
        return "Die Anzahl resistenter Isolate darf nicht groesser sein als die Gesamtzahl."

    if percent(resistant, total) is None:
        return "Die Resistenzrate kann bei einer Gesamtzahl von 0 nicht berechnet werden."

    return None


def baue_berechnungsergebnis(
    keim: str,
    antibiotikum: str,
    total: int,
    resistant: int,
    periode: str,
) -> resistenz_ansicht.ResistenzErgebnis | None:
    """Erzeugt das strukturierte Ergebnis einer validen Berechnung."""
    rate = percent(resistant, total)
    if rate is None:
        return None

    sensitive = subtract(total, resistant)
    antibiotikaklasse = mdr_regeln.antibiotic_class(antibiotikum)
    hinweise = mdr_regeln.get_mdr_hints(keim, antibiotikaklasse, resistant)

    return {
        "timestamp": hole_zeitpunkt(),
        "organism": keim,
        "period": periode,
        "antibiotic": antibiotikum,
        "ab_class": antibiotikaklasse,
        "total": int(total),
        "resistant": int(resistant),
        "sensitive": int(sensitive),
        "rate": float(rate),
        "label": mdr_regeln.classify_rate(float(rate)),
        "hints": hinweise,
    }


def speichere_berechnung_im_verlauf(
    ergebnis: resistenz_ansicht.ResistenzErgebnis,
) -> None:
    """Persistiert ein neues Berechnungsergebnis im benutzerspezifischen Verlauf."""
    run_id = baue_run_id(
        ergebnis["period"],
        ergebnis["organism"],
        ergebnis["antibiotic"],
        int(ergebnis["total"]),
        int(ergebnis["resistant"]),
    )
    if hole_letzte_speicherung() == run_id:
        return

    neuer_eintrag = resistenz_daten.baue_verlaufseintrag(
        zeitpunkt=ergebnis["timestamp"],
        auswertungsperiode=ergebnis["period"],
        keim=ergebnis["organism"],
        antibiotikum=ergebnis["antibiotic"],
        resistenzrate=float(ergebnis["rate"]),
    )
    aktualisierte_daten = pd.concat([hole_verlaufsdaten(), neuer_eintrag], ignore_index=True)
    aktualisierte_daten = resistenz_daten.normalisiere_verlaufsdaten(aktualisierte_daten)

    setze_verlaufsdaten(aktualisierte_daten)
    setze_letzte_speicherung(run_id)

    try:
        speichere_verlaufsdaten(aktualisierte_daten)
    except Exception as exc:
        st.error(f"Fehler beim Speichern: {type(exc).__name__}: {exc}")


def verarbeite_berechnung(
    keim: str,
    antibiotikum: str,
    total: int,
    resistant: int,
    periode: str,
) -> None:
    """Validiert eine Eingabe, berechnet das Ergebnis und speichert den Verlauf."""
    fehlermeldung = validiere_berechnungseingaben(total, resistant)
    if fehlermeldung is not None:
        entferne_gespeichertes_ergebnis()
        st.error(fehlermeldung)
        return

    ergebnis = baue_berechnungsergebnis(
        keim=keim,
        antibiotikum=antibiotikum,
        total=total,
        resistant=resistant,
        periode=periode,
    )
    if ergebnis is None:
        entferne_gespeichertes_ergebnis()
        st.error("Die Berechnung konnte nicht durchgefuehrt werden.")
        return

    setze_gespeichertes_ergebnis(ergebnis)
    speichere_berechnung_im_verlauf(ergebnis)


def main() -> None:
    """Rendert die Seite fuer das Resistenzmonitoring."""
    initialisiere_resistenzmonitoring()

    st.title("Resistenzmonitoring")
    zeige_fachliche_abgrenzung()

    if hole_aktuellen_benutzernamen() is None:
        st.error("Es konnte kein angemeldeter Benutzer ermittelt werden.")
        return

    submitted, keim, antibiotikum, total, resistant, periode = (
        resistenz_ansicht.zeige_berechnungsformular()
    )

    if submitted:
        verarbeite_berechnung(
            keim=keim,
            antibiotikum=antibiotikum,
            total=total,
            resistant=resistant,
            periode=periode,
        )

    ergebnis = hole_gespeichertes_ergebnis()
    if ergebnis is None:
        st.info("Werte eingeben und auf 'Berechnen und speichern' klicken.")
    else:
        resistenz_ansicht.zeige_ergebnis(ergebnis)

    resistenz_ansicht.zeige_verlaufsbereich(hole_verlaufsdaten())


if __name__ == "__main__":
    main()

