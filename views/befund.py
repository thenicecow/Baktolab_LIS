"""Interne Befundansicht fuer validierte Kulturdaten im Stil eines Mikrobiologie-Befunds."""

from __future__ import annotations

from datetime import date

import streamlit as st

from domaene import Material, Patient
from functions.gemeinsam.anzeige_hilfen import (
    baue_technische_fehlernachricht,
    formatiere_datum,
    formatiere_text,
    hole_aktuellen_user_id,
    loese_analyse_label_auf,
    loese_materialtyp_label_auf,
)
from functions.kulturen.ablesen import (
    hole_kulturdaten_oder_standard,
    lade_materialkontext_fuer_kulturen_ablesen,
)
from functions.kulturen.beurteilung import (
    BeurteilterKeim,
    ROLLE_KONTAMINANTE,
    UrinBeurteilung,
    beurteile_urin_allgemeine_bakteriologie,
)
from functions.kulturen.navigation import (
    deaktiviere_befund,
    deaktiviere_kulturen_ablesen,
    hat_gueltige_befund_route,
    hole_material_id_fuer_befund,
)


ABKUERZUNGEN: tuple[tuple[str, str], ...] = (
    ("kw", "Kein Wachstum"),
    ("ID + Resi", "Identifikation und Resistenztestung durchfuehren"),
    ("kf", "Keimflora"),
    ("kfzus", "Zusaetzlicher Keim im Sinne von Keimflora"),
    ("uriflor", "Urinflora beziehungsweise Kontaminationsflora"),
    ("urikont", "Hinweis auf Urinkontamination"),
)

KEIMZAHL_BESCHREIBUNGEN: dict[str, str] = {
    "k4": "<10'000 koloniebildende Einheiten pro Milliliter",
    "p4": "10'000 koloniebildende Einheiten pro Milliliter",
    "p5": "100'000 koloniebildende Einheiten pro Milliliter",
    "g5": ">100'000 koloniebildende Einheiten pro Milliliter",
}

ZUSATZFLORA_CODES: frozenset[str] = frozenset({"kf", "kfzus", "uriflor", "urikont"})


def kehre_zu_kulturen_ablesen_zurueck() -> None:
    """Beendet nur die Befundansicht und zeigt wieder die Kulturseite an."""
    deaktiviere_befund()
    st.switch_page("views/kulturen_ablesen.py")


def kehre_zur_patientendetailansicht_zurueck() -> None:
    """Beendet Kultur- und Befundansicht und wechselt zur Patientenuebersicht."""
    deaktiviere_kulturen_ablesen()
    st.switch_page("views/patientenuebersicht.py")


def zeige_aktionsleiste() -> None:
    """Rendert die wichtigsten Ruecksprung- und Navigationsaktionen der Befundansicht."""
    linke_spalte, mittlere_spalte, rechte_spalte = st.columns(3)

    with linke_spalte:
        if st.button(
            "Zurueck zu Kulturen ablesen",
            use_container_width=True,
        ):
            kehre_zu_kulturen_ablesen_zurueck()

    with mittlere_spalte:
        st.page_link(
            "views/patientenuebersicht.py",
            label="Zurueck zur Patientenuebersicht",
            icon=":material/groups:",
        )

    with rechte_spalte:
        st.page_link(
            "views/dashboard.py",
            label="Zurueck zum Dashboard",
            icon=":material/dashboard:",
        )


def loese_abkuerzung_auf(kuerzel: str | None) -> str:
    """Loest ein im Befund verwendetes Kuerzel in eine verstaendliche Bedeutung auf."""
    if kuerzel is None:
        return "-"

    bereinigt = kuerzel.strip()
    if not bereinigt:
        return "-"

    for code, bedeutung in ABKUERZUNGEN:
        if code == bereinigt:
            return bedeutung

    return "Keine hinterlegte Erklaerung vorhanden."


def loese_keimzahl_auf(keimzahl_code: str | None) -> str:
    """Loest einen internen Keimzahl-Code in die fachlich ausgeschriebene Darstellung auf."""
    if keimzahl_code is None:
        return "-"

    bereinigt = keimzahl_code.strip().casefold()
    if not bereinigt:
        return "-"

    return KEIMZAHL_BESCHREIBUNGEN.get(bereinigt, bereinigt)


def hole_befunddatum() -> str:
    """Liefert das anzuzeigende Befunddatum."""
    return formatiere_datum(date.today())


def baue_beurteilung_fuer_befund(material: Material) -> UrinBeurteilung | None:
    """Liefert eine darstellbare Beurteilung fuer den Befund."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if not kulturdaten.beurteilung:
        return None

    beurteilung = beurteile_urin_allgemeine_bakteriologie(kulturdaten)

    if beurteilung.ist_gueltig and beurteilung.gesamtbeurteilung:
        return beurteilung

    return UrinBeurteilung(
        gesamtbeurteilung=kulturdaten.beurteilung,
        ist_gueltig=True,
        keimbeurteilungen=[],
        hinweise=["Die gespeicherte Gesamtbeurteilung konnte nur vereinfacht angezeigt werden."],
    )


def baue_keimschluessel(
    keim_id: str,
    keimzahl_code: str,
    rolle: str,
) -> tuple[str, str, str]:
    """Erzeugt einen stabilen Vergleichsschluessel fuer Keime und Keimbeurteilungen."""
    return (
        keim_id.strip(),
        keimzahl_code.strip(),
        rolle.strip(),
    )


def baue_beurteilungsindex(
    beurteilung: UrinBeurteilung | None,
) -> dict[tuple[str, str, str], list[BeurteilterKeim]]:
    """Indexiert vorhandene Keimbeurteilungen fuer die Befunddarstellung."""
    index: dict[tuple[str, str, str], list[BeurteilterKeim]] = {}

    if beurteilung is None:
        return index

    for keimbeurteilung in beurteilung.keimbeurteilungen:
        schluessel = baue_keimschluessel(
            keimbeurteilung.keim_id,
            keimbeurteilung.keimzahl_code,
            keimbeurteilung.rolle,
        )
        index.setdefault(schluessel, []).append(keimbeurteilung)

    return index


def baue_einleitungssatz(material: Material) -> str:
    """Liefert den zur Befundlage passenden Einleitungssatz."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False:
        return "Aus dem von Ihnen eingesandten Material wurde kein Wachstum dokumentiert."

    return "Aus dem von Ihnen eingesandten Material wurden folgende Keime identifiziert:"


def ist_kontaminantenrolle(rolle: str | None) -> bool:
    """Prueft, ob eine uebergebene Rollenangabe einer Kontaminante entspricht."""
    if rolle is None:
        return False

    return rolle.strip().casefold() == ROLLE_KONTAMINANTE.casefold()


def ist_keim_fachlich_mitbeurteilt(keimbeurteilung: BeurteilterKeim | None) -> bool:
    """Leitet aus der vorhandenen Keimbeurteilung ab, ob ein Keim fachlich mitbeurteilt wurde."""
    return keimbeurteilung is not None


def soll_resistenzempfehlung_ausgeblendet_werden(
    rolle: str,
    keimbeurteilung: BeurteilterKeim | None,
) -> bool:
    """Prueft, ob fuer einen Keim keine sichtbare Resistenzempfehlung erscheinen soll."""
    if ist_kontaminantenrolle(rolle):
        return True

    if not ist_keim_fachlich_mitbeurteilt(keimbeurteilung):
        return True

    assert keimbeurteilung is not None
    return ist_kontaminantenrolle(keimbeurteilung.rolle) or ist_kontaminantenrolle(
        keimbeurteilung.effektive_rolle
    )


def baue_resistenzempfehlung(
    rolle: str,
    keimbeurteilung: BeurteilterKeim | None,
) -> str | None:
    """Erzeugt die sichtbare Resistenzempfehlung fuer einen einzelnen Keim."""
    if soll_resistenzempfehlung_ausgeblendet_werden(rolle, keimbeurteilung):
        return None

    assert keimbeurteilung is not None
    if keimbeurteilung.ergebnis:
        empfehlung = loese_abkuerzung_auf(keimbeurteilung.ergebnis)
        if keimbeurteilung.begruendung.strip():
            empfehlung = f"{empfehlung}; {keimbeurteilung.begruendung.strip()}"
        return empfehlung

    return "Keine spezifische Folgeinformation hinterlegt."


def baue_keimbloecke(
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> list[dict[str, str | None]]:
    """Erzeugt strukturierte Bloecke fuer die sichtbare Keimdarstellung im Befund."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False or not kulturdaten.keime:
        return []

    beurteilungsindex = baue_beurteilungsindex(beurteilung)
    keimbloecke: list[dict[str, str | None]] = []

    for index, keim in enumerate(kulturdaten.keime, start=1):
        schluessel = baue_keimschluessel(
            keim.keim_id,
            keim.keimzahl_code,
            keim.rolle,
        )
        passende_beurteilungen = beurteilungsindex.get(schluessel, [])
        keimbeurteilung = passende_beurteilungen.pop(0) if passende_beurteilungen else None

        keimbloecke.append(
            {
                "ueberschrift": f"Keim {index}",
                "keim": formatiere_text(keim.keim_id),
                "keimzahl": loese_keimzahl_auf(keim.keimzahl_code),
                "resistenzempfehlung": baue_resistenzempfehlung(
                    keim.rolle,
                    keimbeurteilung,
                ),
                "rolle": formatiere_text(keim.rolle),
            }
        )

    return keimbloecke


def baue_zusaetzliche_flora(material: Material, beurteilung: UrinBeurteilung | None) -> str:
    """Erzeugt eine knappe Beschreibung zusaetzlicher Flora fuer den Befund."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False:
        return "Keine zusaetzliche Flora. Es wurde kein Wachstum dokumentiert."

    beurteilungsindex = baue_beurteilungsindex(beurteilung)
    flora_beschreibungen: list[str] = []

    for keim in kulturdaten.keime:
        schluessel = baue_keimschluessel(
            keim.keim_id,
            keim.keimzahl_code,
            keim.rolle,
        )
        passende_beurteilungen = beurteilungsindex.get(schluessel, [])
        keimbeurteilung = passende_beurteilungen.pop(0) if passende_beurteilungen else None

        if keimbeurteilung is None or keimbeurteilung.ergebnis not in ZUSATZFLORA_CODES:
            continue

        flora_beschreibungen.append(
            f"{formatiere_text(keim.keim_id)} "
            f"({keimbeurteilung.ergebnis}: {loese_abkuerzung_auf(keimbeurteilung.ergebnis)})"
        )

    if flora_beschreibungen:
        return "; ".join(flora_beschreibungen)

    if beurteilung is not None and beurteilung.gesamtbeurteilung in ZUSATZFLORA_CODES:
        code = beurteilung.gesamtbeurteilung
        return f"{code}: {loese_abkuerzung_auf(code)}"

    return "Keine zusaetzliche Flora dokumentiert."


def zeige_befundkopf(patient: Patient, material: Material) -> None:
    """Zeigt den Kopfbereich mit Patientenangaben und Datum."""
    linke_spalte, rechte_spalte = st.columns((3, 1))

    with linke_spalte:
        st.markdown("**Patientenangaben**")
        patient_links, patient_rechts = st.columns(2)

        with patient_links:
            st.markdown(f"**Vorname:** {formatiere_text(patient.vorname)}")
            st.markdown(f"**Nachname:** {formatiere_text(patient.nachname)}")

        with patient_rechts:
            st.markdown(f"**Geburtsdatum:** {formatiere_datum(patient.geburtsdatum)}")
            st.markdown(f"**Geschlecht:** {formatiere_text(patient.geschlecht)}")

        st.caption(
            "Analyse: "
            f"{loese_analyse_label_auf(material.klinische_frage_code)}"
        )

    with rechte_spalte:
        st.markdown("**Datum**")
        st.write(hole_befunddatum())


def zeige_keimdarstellung(material: Material, beurteilung: UrinBeurteilung | None) -> None:
    """Zeigt die Keime als klar getrennte Bloecke untereinander an."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False:
        st.markdown("**Keimstatus:** Kein Wachstum")
        return

    keimbloecke = baue_keimbloecke(material, beurteilung)

    if not keimbloecke:
        st.markdown("**Keimstatus:** Noch keine Keime erfasst")
        return

    for keimblock in keimbloecke:
        resistenzempfehlung = keimblock.get("resistenzempfehlung")

        with st.container(border=True):
            st.markdown(f"**{keimblock['ueberschrift']}**")
            st.markdown(f"**Keim:** {keimblock['keim']}")
            st.markdown(f"**Keimzahl:** {keimblock['keimzahl']}")

            if isinstance(resistenzempfehlung, str) and resistenzempfehlung.strip():
                st.markdown(
                    f"**Resistenzempfehlung:** {resistenzempfehlung}"
                )

            st.markdown(f"**Rolle:** {keimblock['rolle']}")


def zeige_befundinhalt(
    patient: Patient,
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> None:
    """Rendert den eigentlichen Befund im Stil des Mockups."""
    material_label = loese_materialtyp_label_auf(material.materialtyp_code)
    flora_text = baue_zusaetzliche_flora(material, beurteilung)
    validiert_durch = hole_aktuellen_user_id() or "Nicht verfuegbar"

    with st.container(border=True):
        zeige_befundkopf(patient, material)
        st.divider()

        st.markdown("## Mikrobiologischer Befund")
        st.write(baue_einleitungssatz(material))
        st.markdown(f"**Material:** {material_label}")

        zeige_keimdarstellung(material, beurteilung)

        st.markdown(f"**Zusaetzliche Flora:** {flora_text}")

        if beurteilung is not None and beurteilung.hinweise:
            for hinweis in beurteilung.hinweise:
                st.caption(hinweis)

        st.divider()
        st.markdown(f"**Validiert durch:** {validiert_durch}")


def zeige_ausgeschriebene_abkuerzungen() -> None:
    """Zeigt die im Befund verwendeten Abkuerzungen in einem dezenten Zusatzbereich an."""
    with st.container(border=True):
        st.caption("Ausgeschriebene Abkuerzungen")

        for code, bedeutung in ABKUERZUNGEN:
            st.markdown(f"`{code}`: {bedeutung}")


def main() -> None:
    """Rendert die interne Befundansicht fuer das aktuell validierte Material."""
    zeige_aktionsleiste()

    materialreferenz = hole_material_id_fuer_befund()
    if materialreferenz is None:
        st.info(
            "Der Befund kann nur nach einer gueltigen Validierung aus "
            "'Kulturen ablesen' geoeffnet werden."
        )
        return

    if not hat_gueltige_befund_route():
        st.info(
            "Der Befund kann nur nach einer gueltigen Validierung aus "
            "'Kulturen ablesen' geoeffnet werden."
        )
        return

    try:
        materialkontext = lade_materialkontext_fuer_kulturen_ablesen()
    except Exception:
        st.error(
            baue_technische_fehlernachricht(
                "Der Befund konnte fuer das ausgewaehlte Material nicht geladen werden."
            )
        )
        return

    if materialkontext is None:
        st.warning(
            "Zum aktuellen Befund konnte kein gueltiger Materialkontext gefunden werden."
        )
        return

    patient, material = materialkontext
    beurteilung = baue_beurteilung_fuer_befund(material)

    zeige_befundinhalt(patient, material, beurteilung)
    zeige_ausgeschriebene_abkuerzungen()


if __name__ == "__main__":
    main()


