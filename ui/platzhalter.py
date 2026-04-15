from __future__ import annotations

from typing import Sequence

import streamlit as st


def zeige_platzhalterseite(
    *,
    titel: str,
    beschreibung: str,
    vorbereitete_punkte: Sequence[str],
) -> None:
    st.title(titel)
    st.write(beschreibung)
    st.info("In diesem Schritt ist hier bewusst nur eine Platzhalter-Ansicht vorbereitet.")

    st.markdown("### In diesem Schritt vorbereitet")
    for punkt in vorbereitete_punkte:
        st.markdown(f"- {punkt}")
