"""Streamlit-Seite fuer das Resistenzmonitoring mit dauerhafter Verlaufsablage."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

import functions.mdr_rules as mdr_regeln
import functions.resistenzmonitoring as resistenz_daten
import functions.resistenzmonitoring_ansicht as resistenzmonitoring_ansicht
from functions.gemeinsam.anzeige_hilfen import baue_technische_fehlernachricht
from persistenz.resistenzmonitoring_repository import ResistenzmonitoringRepository
from ui.header import show_header


def lade_verlaufsdaten(
    repository: ResistenzmonitoringRepository,
) -> pd.DataFrame | None:
    """Laedt die bisher gespeicherten Verlaufseintraege defensiv aus der Persistenz."""
    try:
        return repository.lade_verlaufsdaten()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Die Verlaufsdaten des Resistenzmonitorings konnten nicht geladen werden."
            )
        )
        return None


def speichere_ergebnis_im_verlauf(
    repository: ResistenzmonitoringRepository,
    ergebnis: resistenzmonitoring_ansicht.ResistenzErgebnis,
) -> pd.DataFrame | None:
    """Speichert das aktuelle Ergebnis als neuen Verlaufseintrag."""
    verlaufseintrag = resistenz_daten.baue_verlaufseintrag(
        zeitpunkt=str(ergebnis["timestamp"]),
        auswertungsperiode=str(ergebnis["period"]),
        keim=str(ergebnis["organism"]),
        antibiotikum=str(ergebnis["antibiotic"]),
        resistenzrate=float(ergebnis["rate"]),
    )

    try:
        return repository.speichere_verlaufseintrag(verlaufseintrag)
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Das Ergebnis des Resistenzmonitorings konnte nicht gespeichert werden."
            )
        )
        return None


def zeige_verlauf_wenn_vorhanden(verlaufsdaten: pd.DataFrame) -> None:
    """Zeigt den gespeicherten Verlauf nur dann an, wenn bereits Daten vorhanden sind."""
    if verlaufsdaten.empty:
        return

    resistenzmonitoring_ansicht.zeige_verlaufsbereich(verlaufsdaten)


def main() -> None:
    """Rendert die Seite, berechnet Ergebnisse und speichert Verlaufseintraege dauerhaft."""
    show_header("Resistenzmonitoring")

    st.write(
        "Hier kannst du eine einfache Resistenzauswertung fuer einen ausgewaehlten Keim "
        "und ein Antibiotikum durchfuehren."
    )

    repository = ResistenzmonitoringRepository()
    verlaufsdaten = lade_verlaufsdaten(repository)
    if verlaufsdaten is None:
        return

    submitted, keim, antibiotikum, total, resistant, periode = (
        resistenzmonitoring_ansicht.zeige_berechnungsformular()
    )

    if not submitted:
        st.info("Fuelle das Formular aus und klicke auf 'Berechnen und speichern'.")
        zeige_verlauf_wenn_vorhanden(verlaufsdaten)
        return

    if total <= 0:
        st.error("Die Gesamtzahl getesteter Isolate muss groesser als 0 sein.")
        zeige_verlauf_wenn_vorhanden(verlaufsdaten)
        return

    if resistant < 0 or resistant > total:
        st.error(
            "Die Anzahl resistenter Isolate muss zwischen 0 und der Gesamtzahl liegen."
        )
        zeige_verlauf_wenn_vorhanden(verlaufsdaten)
        return

    sensitive = total - resistant
    rate = round(100 * resistant / total, 1)
    ab_class = mdr_regeln.antibiotic_class(antibiotikum)
    label = mdr_regeln.classify_rate(rate)
    hints = mdr_regeln.get_mdr_hints(keim, ab_class, resistant)

    ergebnis: resistenzmonitoring_ansicht.ResistenzErgebnis = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "organism": keim,
        "period": periode,
        "antibiotic": antibiotikum,
        "ab_class": ab_class,
        "total": total,
        "resistant": resistant,
        "sensitive": sensitive,
        "rate": rate,
        "label": label,
        "hints": hints,
    }

    aktualisierte_verlaufsdaten = speichere_ergebnis_im_verlauf(repository, ergebnis)

    resistenzmonitoring_ansicht.zeige_ergebnis(ergebnis)

    if aktualisierte_verlaufsdaten is not None:
        resistenzmonitoring_ansicht.zeige_verlaufsbereich(aktualisierte_verlaufsdaten)
        return

    zeige_verlauf_wenn_vorhanden(verlaufsdaten)


if __name__ == "__main__":
    main()