# views/addition_calculator.py

import streamlit as st
import pandas as pd

from functions.addition import subtract, percent


def classify_rate(rate_pct: float) -> str:
    """Einfache Ampel-Klassifikation."""
    if rate_pct < 10:
        return "🟢 niedrig (<10%)"
    if rate_pct <= 25:
        return "🟠 mittel (10–25%)"
    return "🔴 hoch (>25%)"


def is_enterobacterales(organism: str) -> bool:
    return organism in ["E. coli", "Klebsiella pneumoniae"]


def antibiotic_class(antibiotic: str) -> str:
    """
    Ordnet eine Auswahl grob einer Klasse zu.
    (Einfach gehalten für Anfänger.)
    """
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
    Sehr vereinfachte Regeln (didaktisch).
    """
    if resistant_n <= 0:
        return

    # Enterobacterales + Carbapenem resistent -> CPE/CRE Hinweis
    if is_enterobacterales(organism) and ab_class == "Carbapenem":
        st.warning(
            "Warnhinweis: Carbapenem-Resistenz bei Enterobacterales ist besonders relevant "
            "(mögliche CRE/CPE). Bestätigung/Abklärung und Hygienemassnahmen gemäss lokalen Vorgaben prüfen."
        )

    # Enterobacterales + Cephalosporin resistent -> ESBL-Verdacht Hinweis
    if is_enterobacterales(organism) and ab_class == "Cephalosporin":
        st.info(
            "Hinweis: Cephalosporin-Resistenz bei Enterobacterales kann auf ESBL/AmpC hindeuten. "
            "Interpretation gemäss lokalen Richtlinien."
        )

    # S. aureus + Penicillin resistent -> MRSA Hinweis (didaktisch sauber formuliert)
    if organism == "S. aureus" and ab_class == "Penicillin":
        st.warning(
            "Hinweis: Penicillin-Resistenz bei S. aureus ist häufig. "
            "MRSA wird jedoch über Oxacillin/Cefoxitin beurteilt (nicht über Penicillin)."
        )

    # Pseudomonas + Carbapenem resistent -> CRPA Hinweis
    if organism == "Pseudomonas aeruginosa" and ab_class == "Carbapenem":
        st.warning(
            "Warnhinweis: Carbapenem-Resistenz bei Pseudomonas aeruginosa kann klinisch relevant sein "
            "(z. B. CRPA). Abklärung und Therapie gemäss lokalen Vorgaben."
        )


def main():
    st.title("Bakterienfilter – Resistenzmonitor (einfach)")

    # ---- Eingaben (einfach, nachvollziehbar) ----
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

    # ---- Plausibilitätscheck ----
    if resistant > total:
        st.error("Fehler: 'resistente Isolate' darf nicht größer sein als 'gesamt'.")
        return

    # ---- Berechnung (über functions/addition.py) ----
    rate = percent(resistant, total)  # None wenn total==0
    if rate is None:
        st.error("Fehler: Gesamtzahl ist 0 – Resistenzrate kann nicht berechnet werden.")
        return

    sensitive = subtract(total, resistant)
    label = classify_rate(rate)

    ab_class = antibiotic_class(antibiotic)

    # ---- Ergebnis (Zeitperiode + Keim + AB sichtbar) ----
    st.subheader("Ergebnis")
    st.markdown(
        f"**Zeitperiode:** {period}  \n"
        f"**Keim:** {organism}  \n"
        f"**Antibiotikum:** {antibiotic}  \n"
        f"**Klasse:** {ab_class}"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Resistenzrate", f"{rate:.1f}%")
    with c2:
        st.metric("Einstufung", label)
    with c3:
        st.metric("Daten", f"{resistant}/{total}")

    # ---- Zusatztexte zu Multiresistenzen (vereinfachte Regeln) ----
    show_mdr_texts(organism, ab_class, resistant)

    # ---- Kleine Visualisierung (sehr einfach) ----
    st.subheader("Visualisierung")
    df = pd.DataFrame(
        {
            "Kategorie": ["Sensible", "Resistent"],
            "Anzahl": [sensitive, resistant],
        }
    ).set_index("Kategorie")
    st.bar_chart(df)

    # Unten nochmals klar sichtbar (wie verlangt)
    st.caption(f"Auswertung: {organism} – {antibiotic} ({period})")


if __name__ == "__main__":
    main()