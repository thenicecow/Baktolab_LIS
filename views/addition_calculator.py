"""Streamlit-Seite fuer das Resistenzmonitoring mit Verlauf, Aggregation und Visualisierungen."""

from __future__ import annotations

from datetime import datetime
from typing import TypedDict, cast

import altair as alt
import pandas as pd
import pytz
import streamlit as st

import functions.mdr_rules as mdr_regeln
from functions.addition import percent, subtract
from functions.resistenzmonitoring import (
    MONATSNAMEN,
    VERLAUF_DATEIPFAD,
    baue_auswertungsperiode,
    baue_kombinationsuebersicht,
    baue_matrixdaten,
    baue_plot_daten,
    baue_verlaufseintrag,
    berechne_verlaufskennzahlen,
    filtere_verlauf_nach_kombination,
    hole_jahresoptionen,
    hole_leeres_verlaufs_dataframe,
    normalisiere_verlaufsdaten,
)
from utils.data_manager import DataManager


Hinweis = tuple[str, str]
RunId = tuple[str, str, str, int, int]


class ResistenzErgebnis(TypedDict):
    """Struktur fuer das zuletzt berechnete Resistenz-Ergebnis."""

    timestamp: str
    organism: str
    period: str
    antibiotic: str
    ab_class: str
    total: int
    resistant: int
    sensitive: int
    rate: float
    label: str
    hints: list[Hinweis]


KEIM_OPTIONEN: tuple[str, ...] = tuple(mdr_regeln.UNTERSTUETZTE_KEIME)
ANTIBIOTIKA_OPTIONEN: tuple[str, ...] = tuple(mdr_regeln.UNTERSTUETZTE_ANTIBIOTIKA)

VERLAUF_DF_SCHLUESSEL = "resistenzmonitoring_verlauf_df"
VERLAUF_BENUTZER_SCHLUESSEL = "resistenzmonitoring_benutzer"
LETZTE_SPEICHERUNG_SCHLUESSEL = "resistenzmonitoring_last_saved"
ERGEBNIS_SCHLUESSEL = "resistenzmonitoring_result"

FARBSKALA_RESISTENZ = alt.Scale(
    domain=[0, 5, 10, 100],
    range=["#2ca02c", "#84cc16", "#f59e0b", "#d62728"],
)


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


def hole_gespeichertes_ergebnis() -> ResistenzErgebnis | None:
    """Liest das zuletzt berechnete Ergebnis typisiert aus dem Session State."""
    ergebnis = st.session_state.get(ERGEBNIS_SCHLUESSEL)
    if not isinstance(ergebnis, dict):
        return None

    return cast(ResistenzErgebnis, ergebnis)


def setze_gespeichertes_ergebnis(ergebnis: ResistenzErgebnis) -> None:
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
        verlauf = hole_leeres_verlaufs_dataframe()
    else:
        geladene_daten = data_manager.load_user_data(
            VERLAUF_DATEIPFAD,
            initial_value=hole_leeres_verlaufs_dataframe(),
        )
        verlauf = normalisiere_verlaufsdaten(geladene_daten)

    st.session_state[VERLAUF_DF_SCHLUESSEL] = verlauf
    st.session_state[VERLAUF_BENUTZER_SCHLUESSEL] = aktueller_benutzer
    st.session_state[LETZTE_SPEICHERUNG_SCHLUESSEL] = None
    entferne_gespeichertes_ergebnis()


def hole_verlaufsdaten() -> pd.DataFrame:
    """Liefert die aktuell im Zustand gehaltenen Verlaufsdaten normalisiert zurueck."""
    daten = st.session_state.get(VERLAUF_DF_SCHLUESSEL, hole_leeres_verlaufs_dataframe())
    return normalisiere_verlaufsdaten(daten)


def setze_verlaufsdaten(verlaufsdaten: pd.DataFrame) -> None:
    """Aktualisiert die gespeicherten Verlaufsdaten im Session State konsistent."""
    st.session_state[VERLAUF_DF_SCHLUESSEL] = normalisiere_verlaufsdaten(verlaufsdaten)


def speichere_verlaufsdaten(verlaufsdaten: pd.DataFrame) -> None:
    """Persistiert benutzerspezifische Verlaufsdaten ueber den vorhandenen Datenmanager."""
    data_manager.save_user_data(
        normalisiere_verlaufsdaten(verlaufsdaten),
        VERLAUF_DATEIPFAD,
    )


def baue_donut_chart(chart_daten: pd.DataFrame) -> alt.Chart:
    """Erzeugt die Donut-Visualisierung fuer resistente und sensible Isolate."""
    return (
        alt.Chart(chart_daten)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta("Anzahl:Q"),
            color=alt.Color(
                "Kategorie:N",
                scale=alt.Scale(
                    domain=["Sensibel", "Resistent"],
                    range=["#2ca02c", "#d62728"],
                ),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Kategorie:N"),
                alt.Tooltip("Anzahl:Q"),
                alt.Tooltip("Anteil:Q", format=".1%"),
            ],
        )
        .properties(height=300)
    )


def baue_trend_chart(verlauf_kombination: pd.DataFrame) -> alt.Chart:
    """Erzeugt die Zeitreihen-Visualisierung fuer eine Keim-Antibiotikum-Kombination."""
    chart_basis = alt.Chart(verlauf_kombination).encode(
        x=alt.X(
            "Periode_dt:T",
            title="Auswertungsperiode",
            axis=alt.Axis(format="%b %Y"),
        ),
        y=alt.Y(
            "Resistenzrate_plot:Q",
            title="Resistenzrate in %",
            scale=alt.Scale(domain=[0, 100]),
        ),
        tooltip=[
            alt.Tooltip("Auswertungsperiode:N", title="Auswertungsperiode"),
            alt.Tooltip("Keim:N", title="Keim"),
            alt.Tooltip("Antibiotikum:N", title="Antibiotikum"),
            alt.Tooltip("Resistenzrate_plot:Q", title="Resistenzrate in %", format=".1f"),
        ],
    )

    if len(verlauf_kombination) == 1:
        return chart_basis.mark_point(size=120, color="#2563eb").properties(height=350)

    return chart_basis.mark_line(point=True, color="#2563eb").properties(height=350)


def baue_heatmap_chart(matrix_daten: pd.DataFrame) -> alt.LayerChart:
    """Erzeugt eine Heatmap ueber Perioden und Antibiotika fuer einen ausgewaehlten Keim."""
    perioden_sortierung = (
        matrix_daten.loc[:, ["Auswertungsperiode", "Periode_dt"]]
        .drop_duplicates()
        .sort_values("Periode_dt")["Auswertungsperiode"]
        .tolist()
    )

    chart_basis = alt.Chart(matrix_daten).encode(
        x=alt.X(
            "Auswertungsperiode:N",
            title="Auswertungsperiode",
            sort=perioden_sortierung,
        ),
        y=alt.Y(
            "Antibiotikum:N",
            title="Antibiotikum",
            sort=list(ANTIBIOTIKA_OPTIONEN),
        ),
        color=alt.Color(
            "Resistenzrate_plot:Q",
            title="Resistenzrate in %",
            scale=FARBSKALA_RESISTENZ,
        ),
        tooltip=[
            alt.Tooltip("Auswertungsperiode:N", title="Auswertungsperiode"),
            alt.Tooltip("Antibiotikum:N", title="Antibiotikum"),
            alt.Tooltip(
                "Resistenzrate_plot:Q",
                title="Durchschnittliche Resistenzrate in %",
                format=".1f",
            ),
        ],
    )

    return (
        chart_basis.mark_rect()
        + chart_basis.mark_text(size=11, color="#111827").encode(
            text=alt.Text("Resistenzrate_anzeige:N")
        )
    ).properties(height=320)


def baue_chart_daten_fuer_ergebnis(ergebnis: ResistenzErgebnis) -> pd.DataFrame:
    """Erzeugt die Datenbasis fuer die Donut-Visualisierung eines Ergebnisses."""
    chart_daten = pd.DataFrame(
        {
            "Kategorie": ["Sensibel", "Resistent"],
            "Anzahl": [int(ergebnis["sensitive"]), int(ergebnis["resistant"])],
        }
    )
    total_n = int(chart_daten["Anzahl"].sum())
    chart_daten["Anteil"] = chart_daten["Anzahl"] / total_n if total_n > 0 else 0.0
    return chart_daten


def zeige_ergebnis_metadaten(ergebnis: ResistenzErgebnis) -> None:
    """Zeigt Metadaten und Kernkennzahlen des aktuellen Ergebnisses an."""
    detailzeilen = [
        f"**Zeitpunkt:** {ergebnis['timestamp']}",
        f"**Auswertungsperiode:** {ergebnis['period']}",
        f"**Keim:** {ergebnis['organism']}",
        f"**Antibiotikum:** {ergebnis['antibiotic']}",
        f"**Klasse:** {ergebnis['ab_class']}",
    ]
    st.markdown("  \n".join(detailzeilen))
    st.metric("Resistenzrate", f"{float(ergebnis['rate']):.1f}%")
    st.metric("Einstufung", str(ergebnis["label"]))
    st.metric(
        "Daten (resistent / gesamt)",
        f"{int(ergebnis['resistant'])}/{int(ergebnis['total'])}",
    )


def zeige_ergebnis_hinweise(ergebnis: ResistenzErgebnis) -> None:
    """Zeigt vorhandene fachliche Hinweise zur aktuellen Berechnung an."""
    if not ergebnis["hints"]:
        return

    with st.expander("Interpretation und Hinweise"):
        for hinweis_typ, text in ergebnis["hints"]:
            if hinweis_typ == "warning":
                st.warning(text)
            else:
                st.info(text)


def zeige_ergebnis_visualisierung(ergebnis: ResistenzErgebnis) -> None:
    """Zeigt die grafische Aufbereitung des aktuellen Ergebnisses an."""
    chart_daten = baue_chart_daten_fuer_ergebnis(ergebnis)

    st.subheader("Visualisierung der aktuellen Berechnung")
    chart_spalte, detail_spalte = st.columns([2, 1])

    with chart_spalte:
        st.altair_chart(baue_donut_chart(chart_daten), use_container_width=True)

    with detail_spalte:
        resistent = chart_daten.loc[chart_daten["Kategorie"] == "Resistent"].iloc[0]
        sensibel = chart_daten.loc[chart_daten["Kategorie"] == "Sensibel"].iloc[0]
        st.markdown(
            f"**Resistent:** {float(resistent['Anteil']):.1%}<br>({int(resistent['Anzahl'])} Isolate)",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"**Sensibel:** {float(sensibel['Anteil']):.1%}<br>({int(sensibel['Anzahl'])} Isolate)",
            unsafe_allow_html=True,
        )

    st.caption(
        f"Auswertung: {ergebnis['organism']} - {ergebnis['antibiotic']} ({ergebnis['period']})"
    )


def verarbeite_berechnung(
    keim: str,
    antibiotikum: str,
    total: int,
    resistant: int,
    periode: str,
) -> None:
    """Validiert eine Eingabe, berechnet die Resistenzrate und speichert den Verlauf."""
    if resistant > total:
        entferne_gespeichertes_ergebnis()
        st.error("Die Anzahl resistenter Isolate darf nicht groesser sein als die Gesamtzahl.")
        return

    rate = percent(resistant, total)
    if rate is None:
        entferne_gespeichertes_ergebnis()
        st.error("Die Resistenzrate kann bei einer Gesamtzahl von 0 nicht berechnet werden.")
        return

    sensitive = subtract(total, resistant)
    antibiotikaklasse = mdr_regeln.antibiotic_class(antibiotikum)
    hinweise = mdr_regeln.get_mdr_hints(keim, antibiotikaklasse, resistant)
    zeitpunkt = hole_zeitpunkt()

    ergebnis: ResistenzErgebnis = {
        "timestamp": zeitpunkt,
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
    setze_gespeichertes_ergebnis(ergebnis)

    run_id = baue_run_id(periode, keim, antibiotikum, total, resistant)
    if hole_letzte_speicherung() == run_id:
        return

    neuer_eintrag = baue_verlaufseintrag(
        zeitpunkt=zeitpunkt,
        auswertungsperiode=periode,
        keim=keim,
        antibiotikum=antibiotikum,
        resistenzrate=float(rate),
    )
    aktualisierte_daten = pd.concat([hole_verlaufsdaten(), neuer_eintrag], ignore_index=True)
    aktualisierte_daten = normalisiere_verlaufsdaten(aktualisierte_daten)
    setze_verlaufsdaten(aktualisierte_daten)
    setze_letzte_speicherung(run_id)

    try:
        speichere_verlaufsdaten(aktualisierte_daten)
    except Exception as exc:
        st.error(f"Fehler beim Speichern: {type(exc).__name__}: {exc}")


def zeige_ergebnis(ergebnis: ResistenzErgebnis) -> None:
    """Zeigt das Ergebnis der aktuellen Berechnung strukturiert an."""
    st.subheader("Aktuelles Ergebnis")
    linke_spalte, rechte_spalte = st.columns([2, 1])

    with linke_spalte:
        zeige_ergebnis_metadaten(ergebnis)

    with rechte_spalte:
        if ergebnis["hints"]:
            st.info("Klinische Hinweise sind im Abschnitt 'Interpretation und Hinweise' verfuegbar.")

    zeige_ergebnis_hinweise(ergebnis)
    zeige_ergebnis_visualisierung(ergebnis)


def formatiere_prozentwert(wert: float | None) -> str:
    """Formatiert einen optionalen Prozentwert fuer Metriken."""
    if wert is None:
        return "-"
    return f"{float(wert):.1f}%"


def formatiere_veraenderung(wert: float | None) -> str:
    """Formatiert eine optionale Veraenderung in Prozentpunkten fuer Metriken."""
    if wert is None:
        return "-"
    return f"{float(wert):+.1f} %-Pkt."


def waehle_trendkombination(plot_daten: pd.DataFrame) -> tuple[str, str]:
    """Rendert die Auswahllogik fuer die Trendanalyse und liefert die Kombination zurueck."""
    auswahl_links, auswahl_rechts = st.columns(2)

    with auswahl_links:
        ausgewaehlter_keim = st.selectbox(
            "Keim fuer Detailauswertung auswaehlen",
            options=sorted(plot_daten["Keim"].astype(str).dropna().unique()),
            key="trend_organism",
        )

    antibiotika_optionen = sorted(
        plot_daten.loc[plot_daten["Keim"] == ausgewaehlter_keim, "Antibiotikum"]
        .astype(str)
        .dropna()
        .unique()
    )

    with auswahl_rechts:
        ausgewaehltes_antibiotikum = st.selectbox(
            "Antibiotikum fuer Trend auswaehlen",
            options=antibiotika_optionen,
            key="trend_antibiotic",
        )

    return ausgewaehlter_keim, ausgewaehltes_antibiotikum


def zeige_verlaufskennzahlen_abschnitt(kennzahlen: dict[str, float | int | str | None]) -> None:
    """Zeigt die wichtigsten Kennzahlen zur aktuell ausgewaehlten Trendkombination an."""
    metric_spalten = st.columns(4)
    metric_spalten[0].metric("Eintraege", int(kennzahlen["anzahl_eintraege"]))
    metric_spalten[1].metric(
        "Letzte Resistenzrate",
        formatiere_prozentwert(cast(float | None, kennzahlen["letzte_rate"])),
    )
    metric_spalten[2].metric(
        "Durchschnitt",
        formatiere_prozentwert(cast(float | None, kennzahlen["durchschnitt_rate"])),
    )
    metric_spalten[3].metric(
        "Seit Start",
        formatiere_veraenderung(cast(float | None, kennzahlen["veraenderung_seit_start"])),
    )

    letzte_periode = kennzahlen["letzte_periode"]
    if isinstance(letzte_periode, str) and letzte_periode:
        st.caption(f"Letzte beruecksichtigte Periode: {letzte_periode}")


def zeige_aggregierte_keimauswertung(plot_daten: pd.DataFrame, keim: str) -> None:
    """Zeigt Uebersicht und Matrix fuer den aktuell ausgewaehlten Keim an."""
    st.subheader("Aggregierte Uebersicht fuer den ausgewaehlten Keim")
    uebersicht = baue_kombinationsuebersicht(plot_daten, keim)
    if not uebersicht.empty:
        st.dataframe(uebersicht, use_container_width=True)

    matrix_daten = baue_matrixdaten(plot_daten, keim)
    if matrix_daten.empty:
        st.info("Fuer den ausgewaehlten Keim sind noch keine Matrixdaten vorhanden.")
        return

    st.caption(
        "Wenn fuer dieselbe Periode mehrere Eintraege existieren, zeigt die Matrix den Mittelwert je Antibiotikum."
    )
    st.altair_chart(baue_heatmap_chart(matrix_daten), use_container_width=True)


def zeige_verlaufsbereich(verlaufsdaten: pd.DataFrame) -> None:
    """Zeigt tabellarische, trendbasierte und aggregierte Verlaufsauswertungen an."""
    st.subheader("Verlauf der Berechnungen")
    st.dataframe(verlaufsdaten, use_container_width=True)

    plot_daten = baue_plot_daten(verlaufsdaten)
    if plot_daten.empty:
        st.info("Noch keine gueltigen Verlaufsdaten vorhanden.")
        return

    st.subheader("Trendanalyse")
    ausgewaehlter_keim, ausgewaehltes_antibiotikum = waehle_trendkombination(plot_daten)

    verlauf_kombination = filtere_verlauf_nach_kombination(
        plot_daten,
        ausgewaehlter_keim,
        ausgewaehltes_antibiotikum,
    )
    if verlauf_kombination.empty:
        st.info("Fuer diese Kombination sind noch keine Verlaufsdaten vorhanden.")
        return

    kennzahlen = berechne_verlaufskennzahlen(verlauf_kombination)
    zeige_verlaufskennzahlen_abschnitt(kennzahlen)
    st.altair_chart(baue_trend_chart(verlauf_kombination), use_container_width=True)
    zeige_aggregierte_keimauswertung(plot_daten, ausgewaehlter_keim)


def zeige_berechnungsformular() -> tuple[bool, str, str, int, int, str]:
    """Rendert das Berechnungsformular und liefert die aktuellen Eingabewerte zurueck."""
    with st.form("res_form"):
        st.subheader("Auswahl")
        keim = st.selectbox("Keim", options=list(KEIM_OPTIONEN))
        antibiotikum = st.selectbox("Antibiotikum", options=list(ANTIBIOTIKA_OPTIONEN))

        st.subheader("Testergebnisse")
        total = st.number_input("Anzahl getesteter Isolate", min_value=0, value=0, step=1)
        resistant = st.number_input("Anzahl resistenter Isolate", min_value=0, value=0, step=1)

        st.write("Auswertungsperiode erfassen:")
        linke_spalte, rechte_spalte = st.columns(2)

        with linke_spalte:
            monat = st.selectbox("Monat", options=list(MONATSNAMEN))

        with rechte_spalte:
            jahr = st.selectbox("Jahr", options=hole_jahresoptionen())

        periode = baue_auswertungsperiode(monat, int(jahr))
        submitted = st.form_submit_button("Berechnen und speichern")

    return submitted, keim, antibiotikum, int(total), int(resistant), periode


def main() -> None:
    """Rendert die Seite fuer das Resistenzmonitoring."""
    initialisiere_resistenzmonitoring()

    st.title("Resistenzmonitoring")
    st.info(
        "Verlaufsdaten werden benutzerspezifisch gespeichert, beim Laden bereinigt "
        "und fuer die Analyse aggregiert."
    )

    if hole_aktuellen_benutzernamen() is None:
        st.error("Es konnte kein angemeldeter Benutzer ermittelt werden.")
        return

    submitted, keim, antibiotikum, total, resistant, periode = zeige_berechnungsformular()

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
        zeige_ergebnis(ergebnis)

    zeige_verlaufsbereich(hole_verlaufsdaten())


if __name__ == "__main__":
    main()

