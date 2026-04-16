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


def ist_gueltiger_materialtyp_code(materialtyp_code: str | None) -> bool:
    if not isinstance(materialtyp_code, str):
        return False

    return materialtyp_code.strip() in ERLAUBTE_MATERIALTYP_CODES


def ist_gueltiger_analyse_code(analyse_code: str | None) -> bool:
    if not isinstance(analyse_code, str):
        return False

    return analyse_code.strip() in ERLAUBTE_ANALYSE_CODES

