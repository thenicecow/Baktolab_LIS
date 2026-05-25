"""Streamlit-Seite fuer die Auswertung der Probeneingaenge."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from persistenz import PatientenRepository
from ui.header import show_header


PROBENEINGANG_ZEITRAUM_SCHLUESSEL = "probeneingang_auswertung_zeitraum"


def zeige_seitenstil() -> None:
    """Fuegt lokale Styles fuer die Probeneingang-Auswertung hinzu."""
    st.markdown(
        """
        <style>
        .status-card {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            min-height: 125px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.07);
        }

        .status-card-title {
            color: #1d4ed8;
            font-size: 0.95rem;
            font-weight: 850;
            margin-bottom: 0.25rem;
        }

        .status-card-value {
            color: #0f172a;
            font-size: 1.75rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 0.25rem;
        }

        .status-card-text {
            color: #475569;
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .analysis-box {
            background: linear-gradient(135deg, #f8fbff 0%, #ffffff 100%);
            border: 1px solid #dbeafe;
            border-left: 7px solid #2563eb;
            border-radius: 16px;
            padding: 1rem 1.15rem;
            margin-top: 0.75rem;
            margin-bottom: 1rem;
        }

        .analysis-title {
            color: #1d4ed8;
            font-weight: 850;
            font-size: 1rem;
            margin-bottom: 0.3rem;
        }

        .analysis-text {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .heatmap-legend {
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.35rem;
            font-size: 0.82rem;
            color: #475569;
        }

        .legend-dot-blue {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border-radius: 4px;
            background: #dbeafe;
            border: 1px solid #93c5fd;
            margin-right: 0.25rem;
            vertical-align: -0.15rem;
        }

        .legend-dot-green {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border-radius: 4px;
            background: #bbf7d0;
            border: 1px solid #22c55e;
            margin-right: 0.25rem;
            vertical-align: -0.15rem;
        }

        .legend-dot-red {
            display: inline-block;
            width: 1rem;
            height: 1rem;
            border-radius: 4px;
            background: #fecaca;
            border: 1px solid #f87171;
            margin-right: 0.25rem;
            vertical-align: -0.15rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def lade_alle_patientenakten() -> list[tuple[Patient, list[Material]]] | None:
    """Laedt alle Patienten mit vollstaendigen Materiallisten."""
    repository = PatientenRepository()

    try:
        patienten = repository.lade_alle_patienten()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Die Patienten konnten nicht geladen werden."
            )
        )
        return None

    patientenakten: list[tuple[Patient, list[Material]]] = []

    for patient in patienten:
        try:
            patientenakte = repository.lade_patientenakte_nach_id(patient.id)
        except Exception:
            st.warning(
                f"Die Patientenakte von {patient.vorname} {patient.nachname} "
                "konnte nicht vollständig geladen werden."
            )
            patientenakten.append((patient, []))
            continue

        if patientenakte is None:
            patientenakten.append((patient, []))
            continue

        patient_aus_akte, materialien = patientenakte
        patientenakten.append((patient_aus_akte, materialien))

    return patientenakten


def sammle_alle_materialien(
    patientenakten: list[tuple[Patient, list[Material]]],
) -> list[Material]:
    """Sammelt alle Materialien aus allen Patientenakten."""
    materialien: list[Material] = []

    for _patient, patientenmaterialien in patientenakten:
        materialien.extend(patientenmaterialien)

    return materialien


def baue_probeneingang_dataframe(materialien: list[Material]) -> pd.DataFrame:
    """Baut ein DataFrame mit Probeneingangsdatum, Materialtyp und Analyse."""
    zeilen: list[dict[str, object]] = []

    for material in materialien:
        zeilen.append(
            {
                "Eingangsdatum": material.eingangsdatum,
                "Materialtyp": loese_materialtyp_label_auf(material.materialtyp_code),
                "Analyse": loese_analyse_label_auf(material.klinische_frage_code),
            }
        )

    if not zeilen:
        return pd.DataFrame(columns=["Eingangsdatum", "Materialtyp", "Analyse"])

    daten = pd.DataFrame(zeilen)
    daten["Eingangsdatum"] = pd.to_datetime(daten["Eingangsdatum"])
    daten["Datum"] = daten["Eingangsdatum"].dt.date
    daten["Jahr"] = daten["Eingangsdatum"].dt.isocalendar().year.astype(int)
    daten["Kalenderwoche"] = daten["Eingangsdatum"].dt.isocalendar().week.astype(int)
    daten["Wochentag_Nr"] = daten["Eingangsdatum"].dt.weekday
    daten["Wochentag"] = daten["Wochentag_Nr"].map(
        {
            0: "Mo",
            1: "Di",
            2: "Mi",
            3: "Do",
            4: "Fr",
            5: "Sa",
            6: "So",
        }
    )
    daten["KW"] = daten.apply(
        lambda zeile: f"{int(zeile['Jahr'])}-KW {int(zeile['Kalenderwoche']):02d}",
        axis=1,
    )

    return daten


def filtere_probeneingang_nach_zeitraum(
    daten: pd.DataFrame,
    zeitraum: str,
) -> pd.DataFrame:
    """Filtert die Probeneingangsdaten nach einem einfachen Zeitraum."""
    if daten.empty or zeitraum == "Alle Daten":
        return daten

    max_datum = daten["Eingangsdatum"].max()

    if zeitraum == "Letzte 30 Tage":
        grenze = max_datum - pd.Timedelta(days=30)
    elif zeitraum == "Letzte 90 Tage":
        grenze = max_datum - pd.Timedelta(days=90)
    elif zeitraum == "Letzte 180 Tage":
        grenze = max_datum - pd.Timedelta(days=180)
    else:
        return daten

    return daten[daten["Eingangsdatum"] >= grenze]


def baue_tageszaehlung(daten: pd.DataFrame) -> pd.DataFrame:
    """Zaehlt Probeneingaenge pro Tag."""
    if daten.empty:
        return pd.DataFrame(columns=["Datum", "Proben"])

    return (
        daten.groupby("Datum")
        .size()
        .reset_index(name="Proben")
        .sort_values("Datum")
    )


def baue_heatmap_daten(daten: pd.DataFrame) -> pd.DataFrame:
    """Baut eine Heatmap-Matrix nach Kalenderwoche und Wochentag."""
    if daten.empty:
        return pd.DataFrame()

    heatmap = (
        daten.groupby(["KW", "Wochentag"])
        .size()
        .reset_index(name="Proben")
        .pivot(index="KW", columns="Wochentag", values="Proben")
        .fillna(0)
    )

    wochentage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    for tag in wochentage:
        if tag not in heatmap.columns:
            heatmap[tag] = 0

    heatmap = heatmap[wochentage]
    heatmap = heatmap.sort_index()

    return heatmap.astype(int)


def ermittle_heatmap_referenzwerte(heatmap: pd.DataFrame) -> tuple[int, float, int]:
    """Ermittelt Minimum, Mittelwert-Referenz und Maximum fuer die Heatmap-Farbskala."""
    if heatmap.empty:
        return 0, 0.0, 0

    werte = heatmap.to_numpy().flatten()
    positive_werte = [int(wert) for wert in werte if int(wert) > 0]

    if not positive_werte:
        return 0, 0.0, 0

    min_wert = min(positive_werte)
    max_wert = max(positive_werte)

    if max_wert > min_wert:
        mittelwert = (min_wert + max_wert) / 2
    else:
        mittelwert = float(max_wert)

    return min_wert, mittelwert, max_wert


def interpoliere_farbe(wert: int, min_wert: int, max_wert: int) -> str:
    """Berechnet eine Zellfarbe von Blau ueber Gruen bis Rot.

    Blau = wenig/keine Proben
    Gruen = mittlerer Bereich
    Rot = hoechster Probeneingang
    """
    if wert <= 0:
        return "#f8fafc"

    if max_wert <= min_wert:
        return "#bbf7d0"

    anteil = (wert - min_wert) / (max_wert - min_wert)
    anteil = min(max(anteil, 0), 1)

    blau = (219, 234, 254)
    gruen = (187, 247, 208)
    rot = (254, 202, 202)

    if anteil <= 0.5:
        teilanteil = anteil / 0.5
        start = blau
        ende = gruen
    else:
        teilanteil = (anteil - 0.5) / 0.5
        start = gruen
        ende = rot

    r = int(start[0] + (ende[0] - start[0]) * teilanteil)
    g = int(start[1] + (ende[1] - start[1]) * teilanteil)
    b = int(start[2] + (ende[2] - start[2]) * teilanteil)

    return f"#{r:02x}{g:02x}{b:02x}"


def style_heatmap(heatmap: pd.DataFrame):
    """Stylt eine Heatmap-Matrix anhand von Minimum, Mitte und Maximum."""
    min_wert, _mittelwert, max_wert = ermittle_heatmap_referenzwerte(heatmap)

    def style_zelle(wert: object) -> str:
        try:
            zahl = int(wert)
        except (TypeError, ValueError):
            zahl = 0

        hintergrund = interpoliere_farbe(
            wert=zahl,
            min_wert=min_wert,
            max_wert=max_wert,
        )

        return (
            f"background-color: {hintergrund}; "
            "color: #0f172a; "
            "font-weight: 750; "
            "text-align: center;"
        )

    return heatmap.style.map(style_zelle).format("{:.0f}")


def zeige_kennzahlkarte(titel: str, wert: int | str, beschreibung: str) -> None:
    """Zeigt eine einzelne Kennzahlenkarte."""
    st.markdown(
        f"""
        <div class="status-card">
            <div class="status-card-title">{escape(str(titel))}</div>
            <div class="status-card-value">{escape(str(wert))}</div>
            <div class="status-card-text">{escape(str(beschreibung))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_probeneingang_kennzahlen(daten: pd.DataFrame) -> None:
    """Zeigt Kennzahlen zur Probeneingang-Auswertung."""
    if daten.empty:
        return

    tagesdaten = baue_tageszaehlung(daten)

    proben_total = len(daten)
    aktive_tage = len(tagesdaten)
    durchschnitt = proben_total / aktive_tage if aktive_tage else 0

    staerkster_tag = tagesdaten.sort_values("Proben", ascending=False).iloc[0]
    staerkster_tag_label = formatiere_datum(staerkster_tag["Datum"])
    staerkster_tag_wert = int(staerkster_tag["Proben"])

    spalte_1, spalte_2, spalte_3, spalte_4 = st.columns(4)

    with spalte_1:
        zeige_kennzahlkarte(
            "Proben total",
            proben_total,
            "Alle Materialien im ausgewählten Zeitraum.",
        )

    with spalte_2:
        zeige_kennzahlkarte(
            "Eingangstage",
            aktive_tage,
            "Tage mit mindestens einem Probeneingang.",
        )

    with spalte_3:
        zeige_kennzahlkarte(
            "Ø pro Eingangstag",
            f"{durchschnitt:.1f}",
            "Durchschnittliche Probenzahl an aktiven Tagen.",
        )

    with spalte_4:
        zeige_kennzahlkarte(
            "Stärkster Tag",
            staerkster_tag_wert,
            staerkster_tag_label,
        )


def zeige_probeneingang_interpretation(daten: pd.DataFrame) -> None:
    """Zeigt eine kurze automatische Interpretation der Probeneingangsdaten."""
    if daten.empty:
        return

    tagesdaten = baue_tageszaehlung(daten)
    heatmap = baue_heatmap_daten(daten)

    proben_total = len(daten)
    aktive_tage = len(tagesdaten)

    staerkster_tag = tagesdaten.sort_values("Proben", ascending=False).iloc[0]
    staerkster_tag_label = formatiere_datum(staerkster_tag["Datum"])
    staerkster_tag_wert = int(staerkster_tag["Proben"])

    if not heatmap.empty:
        min_wert, mittelwert, max_wert = ermittle_heatmap_referenzwerte(heatmap)
        max_position = heatmap.stack().idxmax()
        max_kw = str(max_position[0])
        max_wochentag = str(max_position[1])
    else:
        min_wert = 0
        mittelwert = 0.0
        max_wert = staerkster_tag_wert
        max_kw = "-"
        max_wochentag = "-"

    st.markdown(
        f"""
        <div class="analysis-box">
            <div class="analysis-title">Interpretation</div>
            <div class="analysis-text">
                Im ausgewählten Zeitraum wurden <strong>{proben_total}</strong> Proben an
                <strong>{aktive_tage}</strong> Eingangstagen erfasst.
                Der stärkste einzelne Probentag war der <strong>{escape(staerkster_tag_label)}</strong>
                mit <strong>{staerkster_tag_wert}</strong> Proben.
                In der Heatmap liegt der höchste Wochen-/Wochentag-Wert bei
                <strong>{max_wert}</strong> Proben in <strong>{escape(max_kw)}</strong> am
                <strong>{escape(max_wochentag)}</strong>.
                Die Farbskala orientiert sich am kleinsten vorhandenen positiven Wert
                <strong>{min_wert}</strong>, am mittleren Referenzbereich um
                <strong>{mittelwert:.1f}</strong> und am Maximum
                <strong>{max_wert}</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def zeige_materialtyp_und_analyse_auswertung(daten: pd.DataFrame) -> None:
    """Zeigt einfache zusätzliche Auswertungen nach Materialtyp und Analyse."""
    if daten.empty:
        return

    materialtyp_zaehlung = daten["Materialtyp"].value_counts().reset_index()
    materialtyp_zaehlung.columns = ["Materialtyp", "Anzahl"]

    analyse_zaehlung = daten["Analyse"].value_counts().reset_index()
    analyse_zaehlung.columns = ["Analyse", "Anzahl"]

    spalte_1, spalte_2 = st.columns(2)

    with spalte_1:
        st.markdown("#### Proben nach Materialtyp")
        st.dataframe(
            materialtyp_zaehlung,
            use_container_width=True,
            hide_index=True,
        )

    with spalte_2:
        st.markdown("#### Proben nach Analyse")
        st.dataframe(
            analyse_zaehlung,
            use_container_width=True,
            hide_index=True,
        )


def zeige_heatmap_referenz(heatmap: pd.DataFrame) -> None:
    """Zeigt die Farbreferenz der Heatmap."""
    min_wert, mittelwert, max_wert = ermittle_heatmap_referenzwerte(heatmap)

    st.markdown(
        f"""
        <span class="heatmap-legend"><span class="legend-dot-blue"></span>
        wenig / keine Proben</span>
        <span class="heatmap-legend"><span class="legend-dot-green"></span>
        mittlerer Bereich</span>
        <span class="heatmap-legend"><span class="legend-dot-red"></span>
        viele Proben</span>
        """,
        unsafe_allow_html=True,
    )

    if max_wert > 0:
        st.caption(
            f"Referenz: wenig ab {min_wert} Probe(n), mittlerer Bereich um "
            f"{mittelwert:.1f} Probe(n), Maximum {max_wert} Probe(n). "
            "Tage ohne Proben bleiben neutral beziehungsweise sehr hell."
        )


def main() -> None:
    """Rendert die Probeneingang-Auswertung."""
    zeige_seitenstil()

    show_header("Probeneingang-Auswertung")

    st.write(
        "Diese Seite wertet aus, wann Proben im Labor eingegangen sind. "
        "Die Auswertung basiert auf dem Eingangsdatum der gespeicherten Materialien."
    )

    patientenakten = lade_alle_patientenakten()
    if patientenakten is None:
        return

    materialien = sammle_alle_materialien(patientenakten)
    daten = baue_probeneingang_dataframe(materialien)

    if daten.empty:
        st.info("Für die Auswertung sind noch keine Materialien vorhanden.")
        st.page_link(
            "views/material_erfassen.py",
            label="Material erfassen",
            icon=":material/science:",
        )
        return

    with st.container(border=True):
        zeitraum = st.selectbox(
            "Zeitraum",
            options=[
                "Alle Daten",
                "Letzte 30 Tage",
                "Letzte 90 Tage",
                "Letzte 180 Tage",
            ],
            key=PROBENEINGANG_ZEITRAUM_SCHLUESSEL,
        )

    daten_gefiltert = filtere_probeneingang_nach_zeitraum(daten, zeitraum)

    if daten_gefiltert.empty:
        st.info("Im gewählten Zeitraum wurden keine Proben gefunden.")
        return

    zeige_probeneingang_kennzahlen(daten_gefiltert)

    st.divider()

    st.markdown("### Proben pro Tag")
    tagesdaten = baue_tageszaehlung(daten_gefiltert)
    tagesdiagramm = tagesdaten.set_index("Datum")
    st.bar_chart(tagesdiagramm["Proben"])

    st.divider()

    st.markdown("### Heatmap nach Kalenderwoche und Wochentag")

    heatmap = baue_heatmap_daten(daten_gefiltert)
    zeige_heatmap_referenz(heatmap)

    if heatmap.empty:
        st.info("Für die Heatmap sind nicht genügend Daten vorhanden.")
    else:
        st.dataframe(
            style_heatmap(heatmap),
            use_container_width=True,
        )

    zeige_probeneingang_interpretation(daten_gefiltert)

    st.divider()

    zeige_materialtyp_und_analyse_auswertung(daten_gefiltert)


main()