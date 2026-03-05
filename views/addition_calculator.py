# views/addition_calculator.py

import streamlit as st
import pandas as pd
import altair as alt

from functions.addition import subtract, percent
from functions.mdr_rules import classify_rate, antibiotic_class, get_mdr_hints

#St.session_stat implementieren
if "data_df" not in st.session_state:
    st.session_state["data_df"] = pd.DataFrame(
        columns=["Zeitperiode", "Keim", "Antibiotikum", "Resistenzrate"]
    )
if "last_saved" not in st.session_state:
    st.session_state["last_saved"] = None

def main():
    st.title("Rechner Resistenzmonitoring")

    # Eingabe
    with st.form("res_form"):
        st.subheader("Auswahl")

        col1, col2 = st.columns(2)
        with col1:
            organism = st.selectbox(
                "Keim",
                ["E. coli", "S. aureus", "Klebsiella pneumoniae", "Pseudomonas aeruginosa"],
            )
        with col2:
            year = st.selectbox(
        "Jahr",
        [2026, 2025, 2024, 2023, 2022, 2021, 2020]
    )

        month = st.selectbox(
        "Monat",
        [
            "Januar", "Februar", "März", "April",
            "Mai", "Juni", "Juli", "August",
            "September", "Oktober", "November", "Dezember"
        ]
    )

        period = f"{month} {year}"

        st.subheader("Antibiotikum")
        antibiotic = st.selectbox(
            "Antibiotikum",
            ["Meropenem", "Imipenem", "Ceftriaxon", "Cefepim", "Penicillin", "Ciprofloxacin", "Gentamicin"],
        )

        st.subheader("Labordaten")
        total = st.number_input("Anzahl getesteter Isolate (gesamt)", min_value=0, value=100, step=1)
        resistant = st.number_input("Anzahl resistenter Isolate", min_value=0, value=10, step=1)

        submitted = st.form_submit_button("Berechnen")

    if not submitted and "result" not in st.session_state:
        st.info("Werte eingeben und auf **Berechnen** klicken.")
        return

    # Beim Klicken Berechnung durchführen
    if submitted:
        # Plausibilitätschecks
        if resistant > total:
            st.error("Fehler: 'resistente Isolate' darf nicht größer sein als 'gesamt'.")
            st.stop()

        rate = percent(resistant, total)  # None wenn total==0
        if rate is None:
            st.error("Fehler: Gesamtzahl ist 0 – Resistenzrate kann nicht berechnet werden.")
            st.stop()

        sensitive = subtract(total, resistant)
        label = classify_rate(rate)
        ab_class = antibiotic_class(antibiotic)
        hints = get_mdr_hints(organism, ab_class, resistant)

        # Resultat speichern (für Anzeige nach dem Rerun)
        st.session_state["result"] = {
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

        # Verlauf sofort speichern
        run_id = (period, organism, antibiotic, int(total), int(resistant))
        if st.session_state["last_saved"] != run_id:
            new_row = pd.DataFrame(
                {
                    "Zeitperiode": [period],
                    "Keim": [organism],
                    "Antibiotikum": [antibiotic],
                    "Resistenzrate": [float(rate)],
                }
            )
            st.session_state["data_df"] = pd.concat(
                [st.session_state["data_df"], new_row],
                ignore_index=True,
            )
            st.session_state["last_saved"] = run_id

    # gespeichertes Resultat laden (z.B. nach Rerun)
    r = st.session_state["result"]

    # Ergebnisanzeige
    st.subheader("Ergebnis")
    left, right = st.columns([2, 1])
    with left:
        st.markdown(
            f"**Auswertungszeitraum:** {r['period']}  \n"
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

    # Zusatztexte / Interpretation (ausblendbar)
    if r["hints"]:
        with st.expander("Interpretation und Hinweise"):
            for hint_type, text in r["hints"]:
                if hint_type == "warning":
                    st.warning(text)
                else:
                    st.info(text)

    # Visualisierung
    st.subheader("Visualisierung")
    chart_df = pd.DataFrame(
        {
            "Kategorie": ["Sensible", "Resistent"],
            "Anzahl": [r["sensitive"], r["resistant"]],
        }
    )

    total_n = int(chart_df["Anzahl"].sum())
    chart_df["Share"] = chart_df["Anzahl"] / total_n if total_n > 0 else 0.0

    color_scale = alt.Scale(domain=["Sensible", "Resistent"], range=["#2ca02c", "#d62728"])

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
        st.markdown(f"🔴 **Resistent:** {share_r:.1%}")
        st.markdown(f"🟢 **Sensibel:** {share_s:.1%}")

    st.caption(f"Auswertung: {r['organism']} – {r['antibiotic']} ({r['period']})")

    # Verlauf
    st.subheader("Verlauf der Berechnungen")
    st.dataframe(st.session_state["data_df"], use_container_width=True)

if __name__ == "__main__":
    main()