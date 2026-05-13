"""Streamlit-Seite fuer das Resistenzmonitoring mit Verlauf, Aggregation und Visualisierungen."""

from __future__ import annotations

from datetime import datetime

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


UNTERSTUETZTE_KEIME: tuple[str, ...] = tuple(mdr_regeln.UNTERSTUETZTE_KEIME)
UNTERSTUETZTE_ANTIBIOTIKA: tuple[str, ...] = tuple(mdr_regeln.UNTERSTUETZTE_ANTIBIOTIKA)
antibiotic_class = mdr_regeln.antibiotic_class
classify_rate = mdr_regeln.classify_rate
get_mdr_hints = mdr_regeln.get_mdr_hints

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
    st.session_state.pop(ERGEBNIS_SCHLUESSEL, None)


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
            sort=list(UNTERSTUETZTE_ANTIBIOTIKA),
        ),
        color=alt.Color(
            "Resistenzrate_plot:Q",
            title="Resistenzrate in %",
            scale=FARBSKALA_RESISTENZ,
        ),
        tooltip=[
            alt.Tooltip("Auswertungsperiode:N", title="Auswertungsperiode"),
            alt.Tooltip("Antibiotikum:N", title="Antibiotikum"),
            alt.Tooltip("Resistenzrate_plot:Q", title="Durchschnittliche Resistenzrate in %", format=".1f"),
        ],
    )

    return (
        chart_basis.mark_rect()
        + chart_basis.mark_text(size=11, color="#111827").encode(
            text=alt.Text("Resistenzrate_anzeige:N")
        )
    ).properties(height=320)


def verarbeite_berechnung(
    keim: str,
    antibiotikum: str,
    total: int,
    resistant: int,
    periode: str,
) -> None:
    """Validiert eine Eingabe, berechnet die Resistenzrate und speichert den Verlauf."""
    if resistant > total:
        st.session_state.pop(ERGEBNIS_SCHLUESSEL, None)
        st.error("Die Anzahl resistenter Isolate darf nicht groesser sein als die Gesamtzahl.")
        return

    rate = percent(resistant, total)
    if rate is None:
        st.session_state.pop(ERGEBNIS_SCHLUESSEL, None)
        st.error("Die Resistenzrate kann bei einer Gesamtzahl von 0 nicht berechnet werden.")
        return

    sensitive = subtract(total, resistant)
    klasse = antibiotic_class(antibiotikum)
    hinweise = get_mdr_hints(keim, klasse, resistant)
    zeitpunkt = datetime.now(pytz.timezone("Europe/Zurich")).strftime("%d.%m.%Y %H:%M")

    st.session_state[ERGEBNIS_SCHLUESSEL] = {
        "timestamp": zeitpunkt,
        "organism": keim,
        "period": periode,
        "antibiotic": antibiotikum,
        "ab_class": klasse,
        "total": int(total),
        "resistant": int(resistant),
        "sensitive": int(sensitive),
        "rate": float(rate),
        "label": classify_rate(float(rate)),
        "hints": hinweise,
    }

    run_id = (periode, keim, antibiotikum, int(total), int(resistant))
    if st.session_state.get(LETZTE_SPEICHERUNG_SCHLUESSEL) == run_id:
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
    st.session_state[LETZTE_SPEICHERUNG_SCHLUESSEL] = run_id

    try:
        speichere_verlaufsdaten(aktualisierte_daten)
    except Exception as exc:
        st.error(f"Fehler beim Speichern: {type(exc).__name__}: {exc}")


def zeige_ergebnis(ergebnis: dict[str, object]) -> None:
    """Zeigt das Ergebnis der aktuellen Berechnung inklusive Donut-Diagramm an."""
    st.subheader("Aktuelles Ergebnis")

    linke_spalte, rechte_spalte = st.columns([2, 1])

    with linke_spalte:
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

    with rechte_spalte:
        if ergebnis["hints"]:
            st.info("Klinische Hinweise sind im Abschnitt 'Interpretation und Hinweise' verfuegbar.")

    if ergebnis["hints"]:
        with st.expander("Interpretation und Hinweise"):
            for hinweis_typ, text in ergebnis["hints"]:
                if hinweis_typ == "warning":
                    st.warning(text)
                else:
                    st.info(text)

    chart_daten = pd.DataFrame(
        {
            "Kategorie": ["Sensibel", "Resistent"],
            "Anzahl": [int(ergebnis["sensitive"]), int(ergebnis["resistant"])],
        }
    )
    total_n = int(chart_daten["Anzahl"].sum())
    chart_daten["Anteil"] = chart_daten["Anzahl"] / total_n if total_n > 0 else 0.0

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


def zeige_verlaufsbereich(verlaufsdaten: pd.DataFrame) -> None:
    """Zeigt tabellarische, trendbasierte und aggregierte Verlaufsauswertungen an."""
    st.subheader("Verlauf der Berechnungen")
    st.dataframe(verlaufsdaten, use_container_width=True)

    plot_daten = baue_plot_daten(verlaufsdaten)
    if plot_daten.empty:
        st.info("Noch keine gueltigen Verlaufsdaten vorhanden.")
        return

    st.subheader("Trendanalyse")
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

    verlauf_kombination = filtere_verlauf_nach_kombination(
        plot_daten,
        ausgewaehlter_keim,
        ausgewaehltes_antibiotikum,
    )
    if verlauf_kombination.empty:
        st.info("Fuer diese Kombination sind noch keine Verlaufsdaten vorhanden.")
        return

    kennzahlen = berechne_verlaufskennzahlen(verlauf_kombination)
    metric_spalten = st.columns(4)
    metric_spalten[0].metric("Eintraege", int(kennzahlen["anzahl_eintraege"]))
    metric_spalten[1].metric(
        "Letzte Resistenzrate",
        "-" if kennzahlen["letzte_rate"] is None else f"{float(kennzahlen['letzte_rate']):.1f}%",
    )
    metric_spalten[2].metric(
        "Durchschnitt",
        "-"
        if kennzahlen["durchschnitt_rate"] is None
        else f"{float(kennzahlen['durchschnitt_rate']):.1f}%",
    )
    metric_spalten[3].metric(
        "Seit Start",
        "-"
        if kennzahlen["veraenderung_seit_start"] is None
        else f"{float(kennzahlen['veraenderung_seit_start']):+.1f} %-Pkt.",
    )

    if kennzahlen["letzte_periode"] is not None:
        st.caption(f"Letzte beruecksichtigte Periode: {kennzahlen['letzte_periode']}")

    st.altair_chart(baue_trend_chart(verlauf_kombination), use_container_width=True)

    st.subheader("Aggregierte Uebersicht fuer den ausgewaehlten Keim")
    uebersicht = baue_kombinationsuebersicht(plot_daten, ausgewaehlter_keim)
    if not uebersicht.empty:
        st.dataframe(uebersicht, use_container_width=True)

    matrix_daten = baue_matrixdaten(plot_daten, ausgewaehlter_keim)
    if matrix_daten.empty:
        st.info("Fuer den ausgewaehlten Keim sind noch keine Matrixdaten vorhanden.")
        return

    st.caption(
        "Wenn fuer dieselbe Periode mehrere Eintraege existieren, zeigt die Matrix den Mittelwert je Antibiotikum."
    )
    st.altair_chart(baue_heatmap_chart(matrix_daten), use_container_width=True)


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

    with st.form("res_form"):
        st.subheader("Auswahl")

        keim = st.selectbox("Keim", options=list(UNTERSTUETZTE_KEIME))
        antibiotikum = st.selectbox("Antibiotikum", options=list(UNTERSTUETZTE_ANTIBIOTIKA))

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

    if submitted:
        verarbeite_berechnung(
            keim=keim,
            antibiotikum=antibiotikum,
            total=int(total),
            resistant=int(resistant),
            periode=periode,
        )

    if ERGEBNIS_SCHLUESSEL in st.session_state:
        zeige_ergebnis(st.session_state[ERGEBNIS_SCHLUESSEL])
    else:
        st.info("Werte eingeben und auf 'Berechnen und speichern' klicken.")

    zeige_verlaufsbereich(hole_verlaufsdaten())


if __name__ == "__main__":
    main()

