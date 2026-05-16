"""Streamlit-Seite für das Dashboard."""

from __future__ import annotations

import streamlit as st

from functions.dashboard.logik import (
    DASHBOARD_HINWEIS,
    DASHBOARD_UNTERTITEL,
    DashboardAktionskarte,
    hole_akzentfarbe_fuer_titel,
    hole_anzeige_name,
    hole_anzeigetext_fuer_titel,
    hole_hauptaktionskarten,
    hole_nebenaktionskarten,
)
from ui.header import show_header


STANDARD_AKZENTFARBE = "#2563EB"


def zeige_hauptaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine grosse Aktionskarte für die priorisierten Hauptaktionen."""
    akzentfarbe = karte.color or hole_akzentfarbe_fuer_titel(karte.titel) or STANDARD_AKZENTFARBE
    hintergrundfarbe = f"{akzentfarbe}18"
    anzeigetitel = hole_anzeigetext_fuer_titel(karte.titel) or karte.titel
    icon_html = ""

    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2.4rem; display:block; "
            f"margin: 0 auto 0.55rem; color: {akzentfarbe};'>{icon_name}</span>"
        )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(180deg, {hintergrundfarbe} 0%, #ffffff 92%);
                border-top: 0.45rem solid {akzentfarbe};
                border-left: 0.35rem solid {akzentfarbe};
                border-radius: 14px;
                padding: 1.15rem 1rem 1rem 1rem;
                margin-bottom: 0.9rem;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        line-height: 1.2;
                        color: {akzentfarbe};
                    ">
                        {anzeigetitel}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                color: #334155;
                min-height: 4.5rem;
                line-height: 1.55;
                margin-bottom: 0.6rem;
            ">
                {karte.beschreibung}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_hauptaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)


def zeige_nebenaktionskarte(karte: DashboardAktionskarte) -> None:
    """Rendert eine kompaktere Aktionskarte für weitere Dashboard-Ziele."""
    akzentfarbe = karte.color or hole_akzentfarbe_fuer_titel(karte.titel) or STANDARD_AKZENTFARBE
    hintergrundfarbe = f"{akzentfarbe}18"
    anzeigetitel = hole_anzeigetext_fuer_titel(karte.titel) or karte.titel
    icon_html = ""

    if karte.icon:
        icon_name = karte.icon[len(":material/"):-1]
        icon_html = (
            f"<span class='material-icons' style='font-size: 2rem; display:block; "
            f"margin: 0 auto 0.45rem; color: {akzentfarbe};'>{icon_name}</span>"
        )

    with st.container(border=True):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(180deg, {hintergrundfarbe} 0%, #ffffff 92%);
                border-top: 0.35rem solid {akzentfarbe};
                border-left: 0.3rem solid {akzentfarbe};
                border-radius: 14px;
                padding: 0.95rem 0.9rem 0.85rem 0.9rem;
                margin-bottom: 0.75rem;
            ">
                <div style="text-align: center;">
                    {icon_html}
                    <div style="
                        font-size: 1.35rem;
                        font-weight: 700;
                        line-height: 1.25;
                        color: {akzentfarbe};
                    ">
                        {anzeigetitel}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="
                color: #475569;
                min-height: 5.3rem;
                line-height: 1.5;
                margin-bottom: 0.55rem;
                font-size: 0.95rem;
            ">
                {karte.beschreibung}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Öffnen",
            use_container_width=True,
            type=karte.button_typ,
            key=f"dashboard_nebenaktion_{karte.titel}",
        ):
            st.switch_page(karte.seitenpfad)


def main() -> None:
    """Rendert das Dashboard und bindet die fachlichen Inhalte ein."""
    anzeige_name = hole_anzeige_name(st.session_state)

    show_header(title="Dashboard")

    st.caption(DASHBOARD_UNTERTITEL)
    st.write(f"Willkommen, **{anzeige_name}**.")
    st.info(DASHBOARD_HINWEIS)

    hauptaktionen = hole_hauptaktionskarten()
    if hauptaktionen:
        st.markdown("### Hauptaktionen")
        hauptaktions_spalten = st.columns(2)

        for spalte, karte in zip(hauptaktions_spalten, hauptaktionen):
            with spalte:
                zeige_hauptaktionskarte(karte)

    nebenaktionen = hole_nebenaktionskarten()
    if nebenaktionen:
        st.markdown("### Weitere Aktionen")
        nebenaktions_spalten = st.columns(len(nebenaktionen))

        for spalte, karte in zip(nebenaktions_spalten, nebenaktionen):
            with spalte:
                zeige_nebenaktionskarte(karte)


main()
