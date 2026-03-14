# views/addition_calculator.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import pytz

from utils.data_manager import DataManager
from functions.addition import subtract, percent
from functions.mdr_rules import classify_rate, antibiotic_class, get_mdr_hints


DEFAULT_COLUMNS = [
    "Zeitpunkt",
    "Auswertungsperiode",
    "Keim",
    "Antibiotikum",
    "Resistenzrate in %",
]

# DataManager für SwitchDrive / WebDAV
data_manager = DataManager(
    fs_protocol="webdav",
    fs_root_folder="resistenzmonitoring_app"
)

current_username = st.session_state.get("username")

# Verlauf neu laden, wenn kein Verlauf vorhanden ist
# ODER wenn sich der eingeloggte Benutzer geändert hat
if (
    "data_df" not in st.session_state
    or st.session_state.get("data_df_username") != current_username
):
    if current_username:
        loaded_df = data_manager.load_user_data(
            "resistance_data.csv",
            initial_value=pd.DataFrame(columns=DEFAULT_COLUMNS)
        )
        if isinstance(loaded_df, pd.DataFrame):
            st.session_state["data_df"] = loaded_df
        else:
            st.session_state["data_df"] = pd.DataFrame(columns=DEFAULT_COLUMNS)
    else:
        st.session_state["data_df"] = pd.DataFrame(columns=DEFAULT_COLUMNS)

    st.session_state["data_df_username"] = current_username

    # Benutzerspezifische States zurücksetzen
    st.session_state["last_saved"] = None
    if "result" in st.session_state:
        del st.session_state["result"]

if "last_saved" not in st.session_state:
    st.session_state["last_saved"] = None


def main():
    st.title("Rechner Resistenzmonitoring")

    # Eingabeformular
    with st.form("res_form"):
        st.subheader("Auswahl")

        organism = st.selectbox(
            "Keim",
            ["E. coli", "S. aureus", "Klebsiella pneumoniae", "Pseudomonas aeruginosa"],
        )

        antibiotic = st.selectbox(
            "Antibiotikum",
            ["Meropenem", "Imipenem", "Ceftriaxon", "Cefepim", "Penicillin", "Ciprofloxacin", "Gentamicin"],
        )

        st.subheader("Testergebnisse")
        total = st.number_input("Anzahl getesteter Isolate (gesamt)", min_value=0, value=0, step=1)
        resistant = st.number_input("Anzahl resistenter Isolate", min_value=0, value=0, step=1)

        st.write("Auswertungsperiode erfassen:")
        col1, col2 = st.columns(2)

        with col1:
            month = st.selectbox(
                "Monat",
                [
                    "Januar", "Februar", "März", "April",
                    "Mai", "Juni", "Juli", "August",
                    "September", "Oktober", "November", "Dezember"
                ]
            )

        with col2:
            year = st.selectbox(
                "Jahr",
                [2026, 2025, 2024, 2023, 2022, 2021, 2020]
            )

        period = f"{month} {year}"
        submitted = st.form_submit_button("Berechnen")

    has_result = "result" in st.session_state

    if not submitted and not has_result:
        st.info("Werte eingeben und auf **Berechnen** klicken.")

    # Berechnung durchführen
    if submitted:
        if resistant > total:
            st.error("Fehler: 'resistente Isolate' darf nicht größer sein als 'gesamt'.")
            st.stop()

        rate = percent(resistant, total)
        if rate is None:
            st.error("Fehler: Gesamtzahl ist 0 – Resistenzrate kann nicht berechnet werden.")
            st.stop()

        sensitive = subtract(total, resistant)
        label = classify_rate(rate)
        ab_class = antibiotic_class(antibiotic)
        hints = get_mdr_hints(organism, ab_class, resistant)

        timestamp = datetime.now(
            pytz.timezone("Europe/Zurich")
        ).strftime("%d.%m.%Y %H:%M")

        st.session_state["result"] = {
            "timestamp": timestamp,
            "organism": organism,
            "period": period,
            "antibiotic": antibiotic,
            "ab_class": ab_class,
            "total": int(total),
            "resistant": int(resistant),
            "sensitive": int(sensitive),
            "rate": float(rate),
            "label": label,
            "hints": hints,
        }

        # Verlauf aktualisieren
        run_id = (period, organism, antibiotic, int(total), int(resistant))
        if st.session_state.get("last_saved") != run_id:
            new_row = pd.DataFrame(
                {
                    "Zeitpunkt": [timestamp],
                    "Auswertungsperiode": [period],
                    "Keim": [organism],
                    "Antibiotikum": [antibiotic],
                    "Resistenzrate in %": [float(rate)],
                }
            )

            st.session_state["data_df"] = pd.concat(
                [st.session_state["data_df"], new_row],
                ignore_index=True,
            )
            st.session_state["last_saved"] = run_id

            # Verlauf persistent speichern
            try:
                data_manager.save_user_data(
                    st.session_state["data_df"],
                    "resistance_data.csv"
                )
            except Exception as e:
                st.error(f"Fehler beim Speichern: {type(e).__name__}: {e}")

        has_result = True

    # Nur anzeigen, wenn wirklich eine aktuelle Berechnung vorliegt
    if has_result:
        r = st.session_state["result"]

        # Ergebnisanzeige
        st.subheader("Ergebnis")
        left, right = st.columns([2, 1])

        with left:
            st.markdown(
                f"**Zeitpunkt:** {r['timestamp']}  \n"
                f"**Auswertungsperiode:** {r['period']}  \n"
                f"**Keim:** {r['organism']}  \n"
                f"**Antibiotikum:** {r['antibiotic']}  \n"
                f"**Klasse:** {r['ab_class']}"
            )
            st.metric("Resistenzrate", f"{r['rate']:.1f}%")
            st.metric("Einstufung", r["label"])
            st.metric("Daten (res/gesamt)", f"{r['resistant']}/{r['total']}")

        with right:
            if r["hints"]:
                st.info("⚠️ Öffne 'Interpretation und Hinweise' für klinische Hinweise.")

        # Zusatztexte / Interpretation
        if r["hints"]:
            with st.expander("Interpretation und Hinweise"):
                for hint_type, text in r["hints"]:
                    if hint_type == "warning":
                        st.warning(text)
                    else:
                        st.info(text)

        # Visualisierung aktuelle Auswertung
        st.subheader("Visualisierung")

        chart_df = pd.DataFrame(
            {
                "Kategorie": ["Sensible", "Resistent"],
                "Anzahl": [r["sensitive"], r["resistant"]],
            }
        )

        total_n = int(chart_df["Anzahl"].sum())
        chart_df["Share"] = chart_df["Anzahl"] / total_n if total_n > 0 else 0.0

        color_scale = alt.Scale(
            domain=["Sensible", "Resistent"],
            range=["#2ca02c", "#d62728"]
        )

        donut_chart = (
            alt.Chart(chart_df)
            .mark_arc(innerRadius=60)
            .encode(
                theta=alt.Theta("Anzahl:Q"),
                color=alt.Color("Kategorie:N", scale=color_scale, legend=None),
                tooltip=[
                    alt.Tooltip("Kategorie:N"),
                    alt.Tooltip("Anzahl:Q"),
                    alt.Tooltip("Share:Q", format=".1%"),
                ],
            )
            .properties(height=300)
        )

        c1, c2 = st.columns([2, 1])

        with c1:
            st.altair_chart(donut_chart, use_container_width=True)

        with c2:
            share_s = float(chart_df.loc[chart_df["Kategorie"] == "Sensible", "Share"].iloc[0])
            share_r = float(chart_df.loc[chart_df["Kategorie"] == "Resistent", "Share"].iloc[0])

            abs_s = int(chart_df.loc[chart_df["Kategorie"] == "Sensible", "Anzahl"].iloc[0])
            abs_r = int(chart_df.loc[chart_df["Kategorie"] == "Resistent", "Anzahl"].iloc[0])

            st.markdown(
                f"🔴 **Resistent:** {share_r:.1%}<br>({abs_r} Isolate)",
                unsafe_allow_html=True
            )
            st.markdown(
                f"🟢 **Sensibel:** {share_s:.1%}<br>({abs_s} Isolate)",
                unsafe_allow_html=True
            )

        st.caption(f"Auswertung: {r['organism']} – {r['antibiotic']} ({r['period']})")

    # Verlaufstabelle immer anzeigen
    st.subheader("Verlauf der Berechnungen")
    st.dataframe(st.session_state["data_df"], use_container_width=True)

    # Grafischer Verlauf immer anzeigen
    st.subheader("Grafischer Verlauf")

    if st.session_state["data_df"].empty:
        st.info("Noch keine Verlaufsdaten vorhanden.")
        return

    plot_df = st.session_state["data_df"].copy()

    # Spalten robust aufbereiten
    plot_df["Zeitpunkt_dt"] = pd.to_datetime(
        plot_df["Zeitpunkt"].astype(str),
        format="%d.%m.%Y %H:%M",
        errors="coerce"
    )
    plot_df["Resistenzrate_plot"] = pd.to_numeric(
        plot_df["Resistenzrate in %"],
        errors="coerce"
    )

    plot_df = plot_df.dropna(subset=["Zeitpunkt_dt", "Resistenzrate_plot"])

    if plot_df.empty:
        st.info("Noch keine gültigen Verlaufsdaten vorhanden.")
        return

    col1, col2 = st.columns(2)

    with col1:
        organism_options = sorted(plot_df["Keim"].astype(str).dropna().unique())
        selected_organism = st.selectbox(
            "Keim für Verlauf auswählen",
            organism_options,
            key="trend_organism"
        )

    with col2:
        antibiotic_options = sorted(
            plot_df.loc[
                plot_df["Keim"] == selected_organism,
                "Antibiotikum"
            ].astype(str).dropna().unique()
        )
        selected_antibiotic = st.selectbox(
            "Antibiotikum für Verlauf auswählen",
            antibiotic_options,
            key="trend_antibiotic"
        )

    filtered_df = plot_df[
        (plot_df["Keim"] == selected_organism) &
        (plot_df["Antibiotikum"] == selected_antibiotic)
    ].sort_values("Zeitpunkt_dt")

    if filtered_df.empty:
        st.info("Für diese Kombination sind noch keine Verlaufsdaten vorhanden.")
        return

    if len(filtered_df) == 1:
        trend_chart = alt.Chart(filtered_df).mark_point(size=120).encode(
            x=alt.X("Zeitpunkt_dt:T", title="Zeitpunkt"),
            y=alt.Y("Resistenzrate_plot:Q", title="Resistenzrate in %"),
            tooltip=[
                alt.Tooltip("Zeitpunkt_dt:T", title="Zeitpunkt"),
                alt.Tooltip("Auswertungsperiode:N", title="Auswertungsperiode"),
                alt.Tooltip("Keim:N", title="Keim"),
                alt.Tooltip("Antibiotikum:N", title="Antibiotikum"),
                alt.Tooltip("Resistenzrate_plot:Q", title="Resistenzrate in %", format=".1f"),
            ],
        ).properties(height=350)
    else:
        trend_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
            x=alt.X("Zeitpunkt_dt:T", title="Zeitpunkt"),
            y=alt.Y("Resistenzrate_plot:Q", title="Resistenzrate in %"),
            tooltip=[
                alt.Tooltip("Zeitpunkt_dt:T", title="Zeitpunkt"),
                alt.Tooltip("Auswertungsperiode:N", title="Auswertungsperiode"),
                alt.Tooltip("Keim:N", title="Keim"),
                alt.Tooltip("Antibiotikum:N", title="Antibiotikum"),
                alt.Tooltip("Resistenzrate_plot:Q", title="Resistenzrate in %", format=".1f"),
            ],
        ).properties(height=350)

    st.altair_chart(trend_chart, use_container_width=True)


if __name__ == "__main__":
    main()