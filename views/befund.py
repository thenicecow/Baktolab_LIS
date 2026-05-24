"""Interne Befundansicht fuer validierte Kulturdaten im Stil eines Mikrobiologie-Befunds."""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path

import streamlit as st

from domaene import Material, Patient
from functions.befund_pdf import (
    BefundPdfDaten,
    BefundPdfKeimblock,
    erstelle_befund_pdf,
)
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
from ui.header import show_header


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
PROJEKTWURZEL = Path(__file__).resolve().parent.parent
BAKTOLOGO_PFAD = PROJEKTWURZEL / "docs" / "images" / "BAKTOLABLOGO.jpeg"


def zeige_design_css() -> None:
    """Ergaenzt kleine lokale Styles fuer eine ruhigere Befundansicht."""
    st.markdown(
        """
        <style>
        .befund-hinweis {
            background: linear-gradient(135deg, #eff6ff 0%, #ffffff 100%);
            border: 1px solid #bfdbfe;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }

        .befund-hinweis-titel {
            color: #1d4ed8;
            font-weight: 800;
            font-size: 1.05rem;
            margin-bottom: 0.2rem;
        }

        .befund-hinweis-text {
            color: #475569;
            font-size: 0.9rem;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dbeafe;
            border-radius: 14px;
            padding: 0.75rem 0.9rem;
            box-shadow: 0 3px 10px rgba(37, 99, 235, 0.05);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def zeige_seitenhinweis(titel: str, text: str) -> None:
    """Zeigt einen rein dekorativen Hinweisbereich ohne fachliche Logik."""
    st.markdown(
        f"""
        <div class="befund-hinweis">
            <div class="befund-hinweis-titel">{titel}</div>
            <div class="befund-hinweis-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    with st.container(border=True):
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
        return "In diesem Material sind keine Bakterien gewachsen."

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
        return "Keine zusaetzliche Flora. In diesem Material sind keine Bakterien gewachsen."

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


def hole_keimstatus(material: Material) -> str | None:
    """Liefert denselben Keimstatus wie in der sichtbaren Befundansicht."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False:
        return "In diesem Material sind keine Bakterien gewachsen."

    if not kulturdaten.keime:
        return "Noch keine Keime erfasst"

    return None


def hole_logo_pfad_fuer_pdf() -> Path | None:
    """Liefert das vorhandene Baktolab-Logo oder ``None`` als stabilen Fallback."""
    if BAKTOLOGO_PFAD.exists():
        return BAKTOLOGO_PFAD

    return None


def bereinige_dateiname_segment(text: str) -> str:
    """Bereinigt einen Text fuer die Verwendung in einem Dateinamen."""
    normalisiert = unicodedata.normalize("NFKD", text)
    ascii_text = normalisiert.encode("ascii", "ignore").decode("ascii")
    bereinigt = re.sub(r"[^a-zA-Z0-9_-]+", "-", ascii_text.strip().lower())
    bereinigt = bereinigt.strip("-")
    return bereinigt or "befund"


def baue_pdf_dateiname(patient: Patient) -> str:
    """Erzeugt einen sinnvollen Dateinamen fuer den Download des aktuellen Befunds."""
    datum_segment = date.today().isoformat()
    nachname = bereinige_dateiname_segment(patient.nachname)
    vorname = bereinige_dateiname_segment(patient.vorname)
    return f"befund_{datum_segment}_{nachname}_{vorname}.pdf"


def baue_befund_pdf_daten(
    patient: Patient,
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> BefundPdfDaten:
    """Baut die PDF-Daten direkt aus denselben fachlichen Bausteinen wie die Befundansicht."""
    keimbloecke = [
        BefundPdfKeimblock(
            ueberschrift=str(keimblock["ueberschrift"]),
            keim=str(keimblock["keim"]),
            keimzahl=str(keimblock["keimzahl"]),
            resistenzempfehlung=(
                str(keimblock["resistenzempfehlung"])
                if keimblock["resistenzempfehlung"]
                else None
            ),
            rolle=str(keimblock["rolle"]) if keimblock["rolle"] else None,
        )
        for keimblock in baue_keimbloecke(material, beurteilung)
    ]

    return BefundPdfDaten(
        titel="Mikrobiologischer Befund",
        datum=hole_befunddatum(),
        patientenzeilen=[
            f"Vorname: {formatiere_text(patient.vorname)}",
            f"Nachname: {formatiere_text(patient.nachname)}",
            f"Geburtsdatum: {formatiere_datum(patient.geburtsdatum)}",
            f"Geschlecht: {formatiere_text(patient.geschlecht)}",
        ],
        befundzeilen=[
            f"Datum: {hole_befunddatum()}",
            f"Material: {loese_materialtyp_label_auf(material.materialtyp_code)}",
            f"Analyse: {loese_analyse_label_auf(material.klinische_frage_code)}",
        ],
        einleitung=baue_einleitungssatz(material),
        keimstatus=hole_keimstatus(material),
        keimbloecke=keimbloecke,
        zusaetzliche_flora=baue_zusaetzliche_flora(material, beurteilung),
        validiert_durch=hole_aktuellen_user_id() or "Nicht verfuegbar",
        hinweise=list(beurteilung.hinweise) if beurteilung is not None else [],
        ausgeschriebene_abkuerzungen=list(ABKUERZUNGEN),
        logo_pfad=hole_logo_pfad_fuer_pdf(),
    )


def baue_befund_pdf_bytes(
    patient: Patient,
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> bytes | None:
    """Erzeugt den aktuellen Befund defensiv als PDF-Bytes fuer den Download."""
    try:
        pdf_daten = baue_befund_pdf_daten(patient, material, beurteilung)
        return erstelle_befund_pdf(pdf_daten)
    except Exception:
        return None


def zeige_pdf_downloadbereich(
    patient: Patient,
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> None:
    """Zeigt eine klar sichtbare Download-Aktion fuer den aktuellen PDF-Befund."""
    pdf_bytes = baue_befund_pdf_bytes(patient, material, beurteilung)

    with st.container(border=True):
        st.markdown("### PDF-Download")
        st.caption(
            "Der aktuell angezeigte Befund kann als professionell formatierte PDF-Datei heruntergeladen werden."
        )

        if pdf_bytes is None:
            st.info(
                "Der Befund konnte aktuell nicht als PDF vorbereitet werden. "
                "Die sichtbare Befundansicht bleibt verfuegbar."
            )
            return

        st.download_button(
            "Befund als PDF herunterladen",
            data=pdf_bytes,
            file_name=baue_pdf_dateiname(patient),
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )


def zeige_befundkopf(patient: Patient, material: Material) -> None:
    """Zeigt den Kopfbereich mit Patientenangaben und Datum."""
    material_label = loese_materialtyp_label_auf(material.materialtyp_code)
    analyse_label = loese_analyse_label_auf(material.klinische_frage_code)

    st.markdown("### Patientenangaben")
    st.caption("Stammdaten und Untersuchungsinformationen")

    patient_spalte, geburt_spalte, befund_spalte = st.columns(3)

    with patient_spalte:
        with st.container(border=True):
            st.markdown("**Vorname**")
            st.write(formatiere_text(patient.vorname))

            st.markdown("**Nachname**")
            st.write(formatiere_text(patient.nachname))

    with geburt_spalte:
        with st.container(border=True):
            st.markdown("**Geburtsdatum**")
            st.write(formatiere_datum(patient.geburtsdatum))

            st.markdown("**Geschlecht**")
            st.write(formatiere_text(patient.geschlecht))

    with befund_spalte:
        with st.container(border=True):
            st.markdown("**Befunddatum**")
            st.write(hole_befunddatum())

            st.markdown("**Material**")
            st.write(material_label)

            st.markdown("**Analyse**")
            st.write(analyse_label)


def zeige_keimdarstellung(material: Material, beurteilung: UrinBeurteilung | None) -> None:
    """Zeigt die Keime als klar getrennte Bloecke untereinander an."""
    kulturdaten = hole_kulturdaten_oder_standard(material)

    if kulturdaten.wachstum is False:
        with st.container(border=True):
            st.markdown("**Befundlage**")
            st.success("In diesem Material sind keine Bakterien gewachsen.")
        return

    keimbloecke = baue_keimbloecke(material, beurteilung)

    if not keimbloecke:
        with st.container(border=True):
            st.markdown("**Keimstatus**")
            st.info("Noch keine Keime erfasst.")
        return

    for keimblock in keimbloecke:
        resistenzempfehlung = keimblock.get("resistenzempfehlung")

        with st.container(border=True):
            st.markdown(f"### {keimblock['ueberschrift']}")

            keim_spalte, keimzahl_spalte, rolle_spalte = st.columns(3)

            with keim_spalte:
                st.markdown("**Keim**")
                st.write(keimblock["keim"])

            with keimzahl_spalte:
                st.markdown("**Keimzahl**")
                st.write(keimblock["keimzahl"])

            with rolle_spalte:
                st.markdown("**Rolle**")
                st.write(keimblock["rolle"])

            if isinstance(resistenzempfehlung, str) and resistenzempfehlung.strip():
                st.info(f"**Resistenzempfehlung:** {resistenzempfehlung}")


def zeige_befundinhalt(
    patient: Patient,
    material: Material,
    beurteilung: UrinBeurteilung | None,
) -> None:
    """Rendert den eigentlichen Befund im Stil eines Mikrobiologie-Befunds."""
    material_label = loese_materialtyp_label_auf(material.materialtyp_code)
    flora_text = baue_zusaetzliche_flora(material, beurteilung)
    validiert_durch = hole_aktuellen_user_id() or "Nicht verfuegbar"

    with st.container(border=True):
        zeige_befundkopf(patient, material)

        st.divider()

        st.markdown("## Mikrobiologischer Befund")

        with st.container(border=True):
            st.markdown("**Befundtext**")
            st.write(baue_einleitungssatz(material))

            st.markdown("**Material**")
            st.write(material_label)

        zeige_keimdarstellung(material, beurteilung)

        with st.container(border=True):
            st.markdown("**Zusaetzliche Flora**")
            st.write(flora_text)

        if beurteilung is not None and beurteilung.hinweise:
            for hinweis in beurteilung.hinweise:
                st.warning(hinweis)

        st.success(f"**Validiert durch:** {validiert_durch}")


def zeige_ausgeschriebene_abkuerzungen() -> None:
    """Zeigt die im Befund verwendeten Abkuerzungen in einem dezenten Zusatzbereich an."""
    with st.expander("Ausgeschriebene Abkuerzungen anzeigen"):
        for code, bedeutung in ABKUERZUNGEN:
            st.markdown(f"**`{code}`**: {bedeutung}")


def main() -> None:
    """Rendert die interne Befundansicht fuer das aktuell validierte Material."""
    zeige_design_css()

    show_header("Befund")

    zeige_seitenhinweis(
        titel="Mikrobiologischer Befund",
        text="Validierte Kulturdaten werden hier strukturiert angezeigt und koennen als PDF heruntergeladen werden.",
    )

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

    zeige_pdf_downloadbereich(patient, material, beurteilung)
    zeige_befundinhalt(patient, material, beurteilung)
    zeige_ausgeschriebene_abkuerzungen()


if __name__ == "__main__":
    main()