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

KLINISCHE_FRAGESTELLUNGEN: tuple[LookupWert, ...] = (
    LookupWert(code="ERSTABKLAERUNG", label="Erstabklaerung"),
    LookupWert(code="VERLAUFSKONTROLLE", label="Verlaufskontrolle"),
    LookupWert(code="THERAPIEKONTROLLE", label="Therapiekontrolle"),
    LookupWert(code="AUSSCHLUSS_INFEKTION", label="Ausschluss Infektion"),
    LookupWert(code="RESISTENZABKLAERUNG", label="Resistenzabklaerung"),
)

KLINISCHE_FRAGESTELLUNGEN_NACH_CODE: dict[str, LookupWert] = {
    eintrag.code: eintrag for eintrag in KLINISCHE_FRAGESTELLUNGEN
}


def ist_gueltiger_materialtyp_code(materialtyp_code: str | None) -> bool:
    if not isinstance(materialtyp_code, str):
        return False

    return materialtyp_code.strip() in ERLAUBTE_MATERIALTYP_CODES
