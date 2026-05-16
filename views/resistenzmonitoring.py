"""Streamlit-Seite für das Resistenzmonitoring."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

import functions.mdr_rules as mdr_regeln
import functions.resistenzmonitoring_ansicht as resistenzmonitoring_ansicht
from ui.header import show_header


def main() -> None:
    show_header("Resistenzmonitoring")

    st.write(
        "Hier kannst du eine einfache Resistenzauswertung für einen ausgewählten Keim "
        "und ein Antibiotikum durchführen."
    )

    submitted, keim, antibiotikum, total, resistant, periode = (
        resistenzmonitoring_ansicht.zeige_berechnungsformular()
    )

    if not submitted:
        st.info("Fülle das Formular aus und klicke auf 'Berechnen und speichern'.")
        return

    if total <= 0:
        st.error("Die Gesamtzahl getesteter Isolate muss grösser als 0 sein.")
        return

    if resistant < 0 or resistant > total:
        st.error(
            "Die Anzahl resistenter Isolate muss zwischen 0 und der Gesamtzahl liegen."
        )
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

    resistenzmonitoring_ansicht.zeige_ergebnis(ergebnis)


if __name__ == "__main__":
    main()
