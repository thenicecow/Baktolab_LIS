from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LookupWert:
    code: str
    label: str


MATERIALTYPEN: tuple[LookupWert, ...] = (
    LookupWert(code="urin", label="Urin"),
    LookupWert(code="blutkultur", label="Blutkultur"),
    LookupWert(code="vaginalabstrich", label="Vaginalabstrich"),
)

ERLAUBTE_MATERIALTYP_CODES: frozenset[str] = frozenset(
    eintrag.code for eintrag in MATERIALTYPEN
)

MATERIALTYPEN_NACH_CODE: dict[str, LookupWert] = {
    eintrag.code: eintrag for eintrag in MATERIALTYPEN
}

ANALYSEN: tuple[LookupWert, ...] = (
    LookupWert(code="allgemeine_bakteriologie", label="Allgemeine Bakteriologie"),
    LookupWert(code="hefen", label="Hefen"),
    LookupWert(code="gardnerella_vaginalis", label="Gardnerella vaginalis"),
)

ERLAUBTE_ANALYSE_CODES: frozenset[str] = frozenset(
    eintrag.code for eintrag in ANALYSEN
)

ANALYSEN_NACH_CODE: dict[str, LookupWert] = {
    eintrag.code: eintrag for eintrag in ANALYSEN
}

KLINISCHE_FRAGESTELLUNGEN: tuple[LookupWert, ...] = ANALYSEN
KLINISCHE_FRAGESTELLUNGEN_NACH_CODE: dict[str, LookupWert] = ANALYSEN_NACH_CODE

_MATERIALTYP_CODES_NACH_NORMALFORM: dict[str, str] = {
    "urin": "urin",
    "blutkultur": "blutkultur",
    "vaginalabstrich": "vaginalabstrich",
    "vaginalabstriche": "vaginalabstrich",
}


def ist_gueltiger_materialtyp_code(materialtyp_code: str | None) -> bool:
    return normalisiere_materialtyp_code(materialtyp_code) is not None


def ist_gueltiger_analyse_code(analyse_code: str | None) -> bool:
    if not isinstance(analyse_code, str):
        return False

    return analyse_code.strip() in ERLAUBTE_ANALYSE_CODES


def normalisiere_materialtyp_code(materialtyp_code: str | None) -> str | None:
    if not isinstance(materialtyp_code, str):
        return None

    bereinigt = materialtyp_code.strip()
    if not bereinigt:
        return None

    normalform = _normalisiere_lookup_text(bereinigt)
    return _MATERIALTYP_CODES_NACH_NORMALFORM.get(normalform)


def _normalisiere_lookup_text(wert: str) -> str:
    normalisiert = wert.strip().casefold()

    for zeichen in (" ", "-", "_"):
        normalisiert = normalisiert.replace(zeichen, "")

    return normalisiert
