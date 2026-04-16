from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LookupWert:
    code: str
    label: str


MATERIALTYPEN: tuple[LookupWert, ...] = (
    LookupWert(code="BLUTKULTUR", label="Blutkultur"),
    LookupWert(code="URIN", label="Urin"),
    LookupWert(code="ABSTRICH", label="Abstrich"),
    LookupWert(code="SPUTUM", label="Sputum"),
    LookupWert(code="PUNKTAT", label="Punktat"),
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
