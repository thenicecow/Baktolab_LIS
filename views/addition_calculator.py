# views/addition_calculator.py

import streamlit as st
import pandas as pd
import altair as alt

from functions.addition import subtract, percent


def classify_rate(rate_pct: float) -> str:
    """Einfache Ampel-Klassifikation."""
    if rate_pct < 5:
        return "🟢 niedrig (<5%)"
    if rate_pct <= 10:
        return "🟠 mittel (5–10%)"
    return "🔴 hoch (>10%)"


def is_enterobacterales(organism: str) -> bool:
    return organism in ["E. coli", "Klebsiella pneumoniae"]


def antibiotic_class(antibiotic: str) -> str:
    if antibiotic in ["Meropenem", "Imipenem"]:
        return "Carbapenem"
    if antibiotic in ["Ceftriaxon", "Cefepim"]:
        return "Cephalosporin"
    if antibiotic in ["Penicillin"]:
        return "Penicillin"
    return "Other"


def show_mdr_texts(organism: str, ab_class: str, resistant_n: int):
    """
    Zusätzliche Texte bei 'multiresistenten' Konstellationen.
    """
    if resistant_n <= 0:
        return

    # Enterobacterales + Carbapenem resistent -> CPE/CRE Hinweis
    if is_enterobacterales(organism) and ab_class == "Carbapenem":
        st.warning(
            "Warnhinweis: Carbapenem-Resistenz bei Enterobacterales ist besonders relevant "
            "(mögliche CRE/CPE). Bestätigung/Abklärung und Hygienemassnahmen gemäss Spitalhygiene prüfen."
        )

    # Enterobacterales + Cephalosporin resistent -> ESBL-Verdacht Hinweis
    if is_enterobacterales(organism) and ab_class == "Cephalosporin":
        st.info(
            "Hinweis: Cephalosporin-Resistenz bei Enterobacterales kann auf ESBL/AmpC hindeuten. "
            "Interpretation gemäss Spitalhygiene-Richtlinien."
        )

    # S. aureus + Penicillin resistent -> MRSA Hinweis
    if organism == "S. aureus" and ab_class == "Penicillin":
        st.warning(
            "Hinweis: Penicillin-Resistenz bei S. aureus ist häufig ein Hinweis auf MRSA. Weitere Tests (z. B. Oxacillin/Cefoxitin) zur Bestätigung empfohlen."
        )

    # Pseudomonas + Carbapenem resistent -> CRPA Hinweis
    if organism == "Pseudomonas aeruginosa" and ab_class == "Carbapenem":
        st.warning(
            "Warnhinweis: Carbapenem-Resistenz bei Pseudomonas aeruginosa kann klinisch relevant sein "
            "(z. B. CRPA). Abklärung und Therapie gemäss Spitalhygiene prüfen."
        )

def mdr_has_hints(organism: str, ab_class: str, resistant_n: int) -> bool:
    if resistant_n <= 0:
        return False
    if is_enterobacterales(organism) and ab_class in {"Carbapenem", "Cephalosporin"}:
        return True
    if organism == "S. aureus" and ab_class == "Penicillin":
        return True
    if organism == "Pseudomonas aeruginosa" and ab_class == "Carbapenem":
        return True
    return False

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
            period = st.selectbox(
                "Zeitperiode",
                ["letzter Monat", "letzte 3 Monate", "letztes Halbjahr", "letztes Jahr"],
            )

        st.subheader("Antibiotikum")
        antibiotic = st.selectbox(
            "Antibiotikum (Beispiele)",
            [
                "Meropenem",     # Carbapenem
                "Imipenem",      # Carbapenem
                "Ceftriaxon",    # Cephalosporin
                "Cefepim",       # Cephalosporin
                "Penicillin",    # Penicillin
                "Ciprofloxacin", # Other
                "Gentamicin",    # Other
            ],
        )

        st.subheader("Labordaten")
        total = st.number_input("Anzahl getesteter Isolate (gesamt)", min_value=0, value=100, step=1)
        resistant = st.number_input("Anzahl resistenter Isolate", min_value=0, value=10, step=1)

        submitted = st.form_submit_button("Berechnen")

    if not submitted:
        st.info("Werte eingeben und auf **Berechnen** klicken.")
        return

    # Plausibilitätschecks
    if resistant > total:
        st.error("Fehler: 'resistente Isolate' darf nicht größer sein als 'gesamt'.")
        return

    # Berechnung
    rate = percent(resistant, total)  # None wenn total==0
    if rate is None:
        st.error("Fehler: Gesamtzahl ist 0 – Resistenzrate kann nicht berechnet werden.")
        return

    sensitive = subtract(total, resistant)
    label = classify_rate(rate)

    ab_class = antibiotic_class(antibiotic)

    # Ergebnisanzeige
    st.subheader("Ergebnis")
    left, right = st.columns([2, 1])
    with left:
        st.markdown(
            f"**Zeitperiode:** {period}  \n"
            f"**Keim:** {organism}  \n"
            f"**Antibiotikum:** {antibiotic}  \n"
            f"**Klasse:** {ab_class}"
        )
        st.write("")
        st.metric("Resistenzrate", f"{rate:.1f}%")
        st.metric("Einstufung", label)
        st.metric("Daten (res/gesamt)", f"{resistant}/{total}")
    with right:
        st.write("")
        if mdr_has_hints(organism, ab_class, resistant):
            st.info("Tipp: Öffne 'Interpretation und Hinweise' für klinische Hinweise.")
        

    # Zusatztexte / Interpretation (ausblendbar)
    if mdr_has_hints(organism, ab_class, resistant):
        with st.expander("Interpretation und Hinweise"):
            show_mdr_texts(organism, ab_class, resistant)

    # Visualisierung
    st.subheader("Visualisierung")
    chart_df = pd.DataFrame({
        "Kategorie": ["Sensible", "Resistent"],
        "Anzahl": [sensitive, resistant],
    })
    # Anteil als Bruch
    total_n = chart_df["Anzahl"].sum()
    if total_n > 0:
        chart_df["Share"] = chart_df["Anzahl"] / total_n
    else:
        chart_df["Share"] = 0.0

    # Farbzuordnung:
    color_scale = alt.Scale(
        domain=["Sensible", "Resistent"],
        range=["#2ca02c", "#d62728"]
    )
    # Kreisdiagramm
    donut_chart = (
        alt.Chart(chart_df)
        .encode(
            theta=alt.Theta("Anzahl:Q"),
            color=alt.Color("Kategorie:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("Kategorie:N"),
                alt.Tooltip("Anzahl:Q"),
                alt.Tooltip("Share:Q", format=".1%")
            ]
        )
        .mark_arc(innerRadius=60)
        .properties(height=300)
    )

    # Layout: Donut links, Prozentanzeige rechts
    c1, c2 = st.columns([2, 1])
    with c1:
        st.altair_chart(donut_chart, use_container_width=True)

    with c2:
        # Werte für Anzeige rechts
        share_s = chart_df.loc[chart_df["Kategorie"] == "Sensible", "Share"].iloc[0]
        share_r = chart_df.loc[chart_df["Kategorie"] == "Resistent", "Share"].iloc[0]

        st.markdown(f"**Anteile**")
        st.write("")
        st.markdown(f"🔴 **Resistent:** {share_r:.1%}  \n( Anzahl: {int(chart_df.loc[chart_df['Kategorie']=='Resistent','Anzahl'].iloc[0])} )")
        st.markdown(f"🟢 **Sensible:** {share_s:.1%}  \n( Anzahl: {int(chart_df.loc[chart_df['Kategorie']=='Sensible','Anzahl'].iloc[0])} )")
        

    st.caption(f"Auswertung: {organism} – {antibiotic} ({period})")


if __name__ == "__main__":
    main()