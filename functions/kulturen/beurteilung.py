"""Fachliche Beurteilungslogik fuer Urin und Allgemeine Bakteriologie."""

from __future__ import annotations

from dataclasses import dataclass, field

from domaene import Kulturdaten, KulturKeim, Material

UNTERSTUETZTER_MATERIALTYP_CODE = "urin"
UNTERSTUETZTER_ANALYSE_CODE = "allgemeine_bakteriologie"

ERGEBNIS_KEIN_WACHSTUM = "kw"
ERGEBNIS_ID_RESI = "ID + Resi"
ERGEBNIS_KEIMFLORA = "kf"
ERGEBNIS_KEIMFLORA_ZUSAETZLICH = "kfzus"
ERGEBNIS_URIFLOR = "uriflor"
ERGEBNIS_URIKONT = "urikont"

ROLLE_PATHOGEN = "pathogen"
ROLLE_KONTAMINANTE = "kontaminante"

KEIMGRUPPE_GRAMNEGATIVE_STAEBCHEN = "gramnegative_staebchen"

KEIMZAHL_RANG: dict[str, int] = {
    "k4": 1,
    "p4": 2,
    "p5": 3,
    "g5": 4,
}

SONDERKEIME_NUR_BEDINGT_PATHOGEN: tuple[str, ...] = (
    "enterococcus spp.",
    "aerococcus spp.",
    "actinotignum schaalii",
)


@dataclass(slots=True, frozen=True)
class BeurteilterKeim:
    """Beschreibt die fachliche Einordnung eines einzelnen Keims."""

    keim_id: str
    keimzahl_code: str
    rolle: str
    keimgruppe: str
    effektive_rolle: str
    ergebnis: str | None
    begruendung: str
    ignoriert: bool = False


@dataclass(slots=True, frozen=True)
class UrinBeurteilung:
    """Beschreibt das strukturierte Ergebnis der Urinbeurteilung."""

    gesamtbeurteilung: str | None
    ist_gueltig: bool
    keimbeurteilungen: list[BeurteilterKeim] = field(default_factory=list)
    hinweise: list[str] = field(default_factory=list)


def ist_material_fuer_urinbeurteilung_unterstuetzt(material: Material) -> bool:
    """Prueft, ob ein Material fachlich fuer diese Urinbeurteilung passt."""
    return (
        material.materialtyp_code == UNTERSTUETZTER_MATERIALTYP_CODE
        and material.klinische_frage_code == UNTERSTUETZTER_ANALYSE_CODE
    )


def beurteile_urin_allgemeine_bakteriologie(kulturdaten: Kulturdaten) -> UrinBeurteilung:
    """Beurteilt gespeicherte Kulturdaten fachlich fuer Urin und Allgemeine Bakteriologie."""
    if kulturdaten.wachstum is False:
        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_KEIN_WACHSTUM,
            ist_gueltig=True,
            hinweise=["Kein Wachstum wurde explizit angegeben."],
        )

    if kulturdaten.wachstum is not True:
        return UrinBeurteilung(
            gesamtbeurteilung=None,
            ist_gueltig=False,
            hinweise=["Das Feld 'wachstum' ist nicht eindeutig gesetzt."],
        )

    validierung = _validiere_keime(kulturdaten.keime)
    if not validierung.ist_gueltig:
        return validierung

    keime = _normalisiere_keime(kulturdaten.keime)
    if not keime:
        return UrinBeurteilung(
            gesamtbeurteilung=None,
            ist_gueltig=False,
            hinweise=["Bei Wachstum wurde kein vollstaendiger Keimeintrag gefunden."],
        )

    relevante_keime, ignorierte_k4_keime = _trenne_relevante_keime(keime)
    hinweise = list(ignorierte_k4_keime)

    if not relevante_keime:
        return UrinBeurteilung(
            gesamtbeurteilung=None,
            ist_gueltig=False,
            hinweise=["Es konnten keine fachlich verwertbaren Keime bestimmt werden."],
        )

    if all(keim.keimzahl_code == "k4" for keim in relevante_keime):
        return _beurteile_reine_k4_konstellation(relevante_keime, hinweise)

    keime_mit_effektiver_rolle = _bestimme_effektive_rollen(relevante_keime)
    return _beurteile_relevante_keime_ab_p4(keime_mit_effektiver_rolle, hinweise)


def _validiere_keime(keime: list[KulturKeim]) -> UrinBeurteilung:
    """Validiert die vorhandenen Keime defensiv vor der Beurteilung."""
    if not isinstance(keime, list):
        return UrinBeurteilung(
            gesamtbeurteilung=None,
            ist_gueltig=False,
            hinweise=["Die Kulturdaten enthalten keine gueltige Keimliste."],
        )

    fehler: list[str] = []

    for index, keim in enumerate(keime, start=1):
        if not isinstance(keim, KulturKeim):
            fehler.append(f"Keim {index} ist kein gueltiger KulturKeim-Eintrag.")
            continue

        if not keim.keim_id.strip():
            fehler.append(f"Keim {index} hat keine Keim-ID.")
        if keim.keimzahl_code not in KEIMZAHL_RANG:
            fehler.append(
                f"Keim {index} hat einen ungueltigen Keimzahl-Code: {keim.keimzahl_code}."
            )
        if keim.rolle not in {ROLLE_PATHOGEN, ROLLE_KONTAMINANTE}:
            fehler.append(f"Keim {index} hat eine ungueltige Rolle: {keim.rolle}.")
        if not keim.keimgruppe.strip():
            fehler.append(f"Keim {index} hat keine Keimgruppe.")

    if fehler:
        return UrinBeurteilung(
            gesamtbeurteilung=None,
            ist_gueltig=False,
            hinweise=fehler,
        )

    return UrinBeurteilung(
        gesamtbeurteilung=None,
        ist_gueltig=True,
        hinweise=[],
    )


def _normalisiere_keime(keime: list[KulturKeim]) -> list[KulturKeim]:
    """Bereinigt Keime defensiv fuer die fachliche Auswertung."""
    normalisierte_keime: list[KulturKeim] = []

    for keim in keime:
        if not isinstance(keim, KulturKeim):
            continue

        keim_id = keim.keim_id.strip()
        keimgruppe = keim.keimgruppe.strip()
        rolle = keim.rolle.strip()
        keimzahl_code = keim.keimzahl_code.strip()

        if not keim_id or not keimgruppe or rolle not in {ROLLE_PATHOGEN, ROLLE_KONTAMINANTE}:
            continue

        if keimzahl_code not in KEIMZAHL_RANG:
            continue

        normalisierte_keime.append(
            KulturKeim(
                keim_id=keim_id,
                keimzahl_code=keimzahl_code,
                rolle=rolle,
                keimgruppe=keimgruppe,
            )
        )

    return normalisierte_keime


def _trenne_relevante_keime(keime: list[KulturKeim]) -> tuple[list[KulturKeim], list[str]]:
    """Ignoriert k4-Keime, wenn gleichzeitig p4, p5 oder g5 vorhanden sind."""
    hohe_keime = [keim for keim in keime if keim.keimzahl_code in {"p4", "p5", "g5"}]
    k4_keime = [keim for keim in keime if keim.keimzahl_code == "k4"]

    if not hohe_keime:
        return keime, []

    hinweise = []
    if k4_keime:
        hinweise.append(
            "Keime mit 'k4' wurden nicht mitbeurteilt, weil gleichzeitig p4, p5 oder g5 vorliegen."
        )

    return hohe_keime, hinweise


def _beurteile_reine_k4_konstellation(
    keime: list[KulturKeim],
    hinweise: list[str],
) -> UrinBeurteilung:
    """Beurteilt Konstellationen, in denen ausschliesslich k4 vorliegt."""
    if len(keime) == 1:
        keim = keime[0]
        if keim.keimgruppe == KEIMGRUPPE_GRAMNEGATIVE_STAEBCHEN:
            return UrinBeurteilung(
                gesamtbeurteilung=ERGEBNIS_ID_RESI,
                ist_gueltig=True,
                keimbeurteilungen=[
                    BeurteilterKeim(
                        keim_id=keim.keim_id,
                        keimzahl_code=keim.keimzahl_code,
                        rolle=keim.rolle,
                        keimgruppe=keim.keimgruppe,
                        effektive_rolle=keim.rolle,
                        ergebnis=ERGEBNIS_ID_RESI,
                        begruendung="Ein einzelner k4-Keim aus gramnegativen Staebchen wird weiterverarbeitet.",
                    )
                ],
                hinweise=hinweise,
            )

        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_KEIMFLORA,
            ist_gueltig=True,
            keimbeurteilungen=[
                BeurteilterKeim(
                    keim_id=keim.keim_id,
                    keimzahl_code=keim.keimzahl_code,
                    rolle=keim.rolle,
                    keimgruppe=keim.keimgruppe,
                    effektive_rolle=keim.rolle,
                    ergebnis=ERGEBNIS_KEIMFLORA,
                    begruendung="Ein einzelner k4-Keim ausserhalb gramnegativer Staebchen wird als Keimflora beurteilt.",
                )
            ],
            hinweise=hinweise,
        )

    return UrinBeurteilung(
        gesamtbeurteilung=ERGEBNIS_KEIMFLORA,
        ist_gueltig=True,
        keimbeurteilungen=[
            BeurteilterKeim(
                keim_id=keim.keim_id,
                keimzahl_code=keim.keimzahl_code,
                rolle=keim.rolle,
                keimgruppe=keim.keimgruppe,
                effektive_rolle=keim.rolle,
                ergebnis=ERGEBNIS_KEIMFLORA,
                begruendung="Mehrere Keime im Bereich k4 werden insgesamt als Keimflora beurteilt.",
            )
            for keim in keime
        ],
        hinweise=hinweise,
    )


def _bestimme_effektive_rollen(keime: list[KulturKeim]) -> list[tuple[KulturKeim, str]]:
    """Bestimmt die fachlich wirksame Rolle eines Keims inklusive Sonderregel."""
    vorlaeufig_pathogene = [keim for keim in keime if keim.rolle == ROLLE_PATHOGEN]
    ergebnisse: list[tuple[KulturKeim, str]] = []

    for keim in keime:
        effektive_rolle = keim.rolle

        if keim.rolle == ROLLE_PATHOGEN and _ist_bedingt_pathogener_keim(keim):
            if not _darf_als_pathogen_gelten(keim, keime, vorlaeufig_pathogene):
                effektive_rolle = ROLLE_KONTAMINANTE

        ergebnisse.append((keim, effektive_rolle))

    return ergebnisse


def _ist_bedingt_pathogener_keim(keim: KulturKeim) -> bool:
    """Prueft, ob ein Keim nur unter Zusatzbedingungen als pathogen gelten soll."""
    keimname = keim.keim_id.casefold()
    return any(sonderkeim in keimname for sonderkeim in SONDERKEIME_NUR_BEDINGT_PATHOGEN)


def _darf_als_pathogen_gelten(
    keim: KulturKeim,
    alle_keime: list[KulturKeim],
    vorlaeufig_pathogene: list[KulturKeim],
) -> bool:
    """Prueft die Sonderregel fuer Enterococcus, Aerococcus und Actinotignum."""
    if len(alle_keime) == 1:
        return True

    if len(vorlaeufig_pathogene) == 1:
        return True

    rang = KEIMZAHL_RANG[keim.keimzahl_code]
    max_rang = max(KEIMZAHL_RANG[eintrag.keimzahl_code] for eintrag in alle_keime)

    return rang == max_rang and sum(
        1 for eintrag in alle_keime if KEIMZAHL_RANG[eintrag.keimzahl_code] == max_rang
    ) <= 2


def _beurteile_relevante_keime_ab_p4(
    keime_mit_rollen: list[tuple[KulturKeim, str]],
    hinweise: list[str],
) -> UrinBeurteilung:
    """Beurteilt Konstellationen mit p4, p5 oder g5."""
    anzahl_keime = len(keime_mit_rollen)

    if anzahl_keime == 1:
        return _beurteile_einzelkeim_ab_p4(keime_mit_rollen[0], hinweise)

    if anzahl_keime == 2:
        return _beurteile_zwei_keime_ab_p4(keime_mit_rollen, hinweise)

    return _beurteile_mehrere_keime_ab_p4(keime_mit_rollen, hinweise)


def _beurteile_einzelkeim_ab_p4(
    keim_mit_rolle: tuple[KulturKeim, str],
    hinweise: list[str],
) -> UrinBeurteilung:
    """Beurteilt genau einen relevanten Keim."""
    keim, effektive_rolle = keim_mit_rolle

    if effektive_rolle == ROLLE_PATHOGEN:
        ergebnis = ERGEBNIS_ID_RESI
        begruendung = "Ein einzelner relevanter pathogener Keim wird weiterverarbeitet."
    else:
        ergebnis = ERGEBNIS_URIFLOR
        begruendung = (
            "Ein einzelner relevanter Kontaminationskeim wird als Kontaminationsflora beurteilt."
        )

    return UrinBeurteilung(
        gesamtbeurteilung=ergebnis,
        ist_gueltig=True,
        keimbeurteilungen=[
            BeurteilterKeim(
                keim_id=keim.keim_id,
                keimzahl_code=keim.keimzahl_code,
                rolle=keim.rolle,
                keimgruppe=keim.keimgruppe,
                effektive_rolle=effektive_rolle,
                ergebnis=ergebnis,
                begruendung=begruendung,
            )
        ],
        hinweise=hinweise,
    )


def _beurteile_zwei_keime_ab_p4(
    keime_mit_rollen: list[tuple[KulturKeim, str]],
    hinweise: list[str],
) -> UrinBeurteilung:
    """Beurteilt genau zwei relevante Keime."""
    pathogene = [eintrag for eintrag in keime_mit_rollen if eintrag[1] == ROLLE_PATHOGEN]
    kontaminanten = [eintrag for eintrag in keime_mit_rollen if eintrag[1] == ROLLE_KONTAMINANTE]

    if len(pathogene) == 2:
        codes = {pathogene[0][0].keimzahl_code, pathogene[1][0].keimzahl_code}

        if codes == {"p4", "g5"}:
            dominanter_keim = next(
                eintrag for eintrag in pathogene if eintrag[0].keimzahl_code == "g5"
            )
            zweiter_keim = next(
                eintrag for eintrag in pathogene if eintrag[0].keimzahl_code == "p4"
            )

            return UrinBeurteilung(
                gesamtbeurteilung=ERGEBNIS_ID_RESI,
                ist_gueltig=True,
                keimbeurteilungen=[
                    _baue_beurteilten_keim(
                        dominanter_keim,
                        ERGEBNIS_ID_RESI,
                        "Bei p4 und g5 wird nur der g5-Keim weiterverarbeitet.",
                    ),
                    _baue_beurteilten_keim(
                        zweiter_keim,
                        ERGEBNIS_KEIMFLORA_ZUSAETZLICH,
                        "Der zweite pathogene Keim faellt in dieser Spezialregel in kfzus.",
                    ),
                ],
                hinweise=hinweise,
            )

        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_ID_RESI,
            ist_gueltig=True,
            keimbeurteilungen=[
                _baue_beurteilten_keim(
                    eintrag,
                    ERGEBNIS_ID_RESI,
                    "Zwei pathogene Keime werden grundsaetzlich weiterverarbeitet.",
                )
                for eintrag in pathogene
            ],
            hinweise=hinweise,
        )

    if len(pathogene) == 1 and len(kontaminanten) == 1:
        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_ID_RESI,
            ist_gueltig=True,
            keimbeurteilungen=[
                _baue_beurteilten_keim(
                    pathogene[0],
                    ERGEBNIS_ID_RESI,
                    "Der pathogene Keim wird weiterverarbeitet.",
                ),
                _baue_beurteilten_keim(
                    kontaminanten[0],
                    ERGEBNIS_KEIMFLORA_ZUSAETZLICH,
                    "Der zusaetzliche Kontaminationskeim faellt in kfzus.",
                ),
            ],
            hinweise=hinweise,
        )

    return UrinBeurteilung(
        gesamtbeurteilung=ERGEBNIS_KEIMFLORA,
        ist_gueltig=True,
        keimbeurteilungen=[
            _baue_beurteilten_keim(
                eintrag,
                ERGEBNIS_KEIMFLORA,
                "Zwei Kontaminationskeime werden als Keimflora beurteilt.",
            )
            for eintrag in kontaminanten
        ],
        hinweise=hinweise,
    )


def _beurteile_mehrere_keime_ab_p4(
    keime_mit_rollen: list[tuple[KulturKeim, str]],
    hinweise: list[str],
) -> UrinBeurteilung:
    """Beurteilt Konstellationen mit mindestens drei relevanten Keimen."""
    pathogene = [eintrag for eintrag in keime_mit_rollen if eintrag[1] == ROLLE_PATHOGEN]

    if not pathogene:
        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_KEIMFLORA,
            ist_gueltig=True,
            keimbeurteilungen=[
                _baue_beurteilten_keim(
                    eintrag,
                    ERGEBNIS_KEIMFLORA,
                    "Es liegen nur Kontaminationskeime vor.",
                )
                for eintrag in keime_mit_rollen
            ],
            hinweise=hinweise,
        )

    dominante_pathogene = _ermittle_dominante_pathogene(keime_mit_rollen)

    if 1 <= len(dominante_pathogene) <= 2:
        dominante_ids = {id(eintrag[0]) for eintrag in dominante_pathogene}
        keimbeurteilungen: list[BeurteilterKeim] = []

        for eintrag in keime_mit_rollen:
            if id(eintrag[0]) in dominante_ids:
                keimbeurteilungen.append(
                    _baue_beurteilten_keim(
                        eintrag,
                        ERGEBNIS_ID_RESI,
                        "Der dominante pathogene Keim wird weiterverarbeitet.",
                    )
                )
            else:
                keimbeurteilungen.append(
                    _baue_beurteilten_keim(
                        eintrag,
                        ERGEBNIS_KEIMFLORA_ZUSAETZLICH,
                        "Nicht dominante Zusatzkeime fallen in kfzus.",
                    )
                )

        return UrinBeurteilung(
            gesamtbeurteilung=ERGEBNIS_ID_RESI,
            ist_gueltig=True,
            keimbeurteilungen=keimbeurteilungen,
            hinweise=hinweise,
        )

    return UrinBeurteilung(
        gesamtbeurteilung=ERGEBNIS_URIKONT,
        ist_gueltig=True,
        keimbeurteilungen=[
            _baue_beurteilten_keim(
                eintrag,
                ERGEBNIS_URIKONT,
                "Es liegt keine klare Dominanz von einem oder zwei pathogenen Keimen vor.",
            )
            for eintrag in keime_mit_rollen
        ],
        hinweise=hinweise,
    )


def _ermittle_dominante_pathogene(
    keime_mit_rollen: list[tuple[KulturKeim, str]],
) -> list[tuple[KulturKeim, str]]:
    """Ermittelt pathogene Keime mit klar hoechster Keimzahlgruppe."""
    if len(keime_mit_rollen) < 3:
        return []

    max_rang = max(KEIMZAHL_RANG[keim.keimzahl_code] for keim, _rolle in keime_mit_rollen)
    dominante_keime = [
        eintrag
        for eintrag in keime_mit_rollen
        if KEIMZAHL_RANG[eintrag[0].keimzahl_code] == max_rang
    ]

    if len(dominante_keime) == len(keime_mit_rollen):
        return []

    if not all(effektive_rolle == ROLLE_PATHOGEN for _keim, effektive_rolle in dominante_keime):
        return []

    if len(dominante_keime) > 2:
        return []

    return dominante_keime


def _baue_beurteilten_keim(
    keim_mit_rolle: tuple[KulturKeim, str],
    ergebnis: str,
    begruendung: str,
) -> BeurteilterKeim:
    """Erzeugt einen einzelnen strukturierten Keimeintrag fuer die Rueckgabe."""
    keim, effektive_rolle = keim_mit_rolle

    return BeurteilterKeim(
        keim_id=keim.keim_id,
        keimzahl_code=keim.keimzahl_code,
        rolle=keim.rolle,
        keimgruppe=keim.keimgruppe,
        effektive_rolle=effektive_rolle,
        ergebnis=ergebnis,
        begruendung=begruendung,
    )
