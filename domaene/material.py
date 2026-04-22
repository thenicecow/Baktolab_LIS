"""Domaenenmodelle fuer Materialien und vorbereitete Kulturdaten."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from domaene.basis import BasisModell


ERLAUBTE_KEIMZAHL_CODES: frozenset[str] = frozenset({"k4", "p4", "p5", "g5"})


def ist_gueltiger_keimzahl_code(keimzahl_code: str | None) -> bool:
    """Prueft, ob ein Keimzahl-Code zur vorbereiteten Kulturstruktur passt."""
    if not isinstance(keimzahl_code, str):
        return False

    return keimzahl_code.strip() in ERLAUBTE_KEIMZAHL_CODES


@dataclass(slots=True)
class KulturKeim:
    """Beschreibt einen einzelnen Keimeintrag innerhalb vorbereiteter Kulturdaten."""

    keim_id: str
    keimzahl_code: str
    rolle: str
    keimgruppe: str


@dataclass(slots=True)
class Kulturdaten:
    """Beschreibt vorbereitete Kulturdaten zu einem Material."""

    wachstum: bool | None = None
    keime: list[KulturKeim] = field(default_factory=list)
    beurteilung: str | None = None


@dataclass(slots=True)
class Material(BasisModell):
    """Beschreibt ein Labor-Material eines Patienten."""

    id: str
    patient_id: str
    materialtyp_code: str
    klinische_frage_code: str
    abnahmedatum: date
    eingangsdatum: date
    kulturdaten: Kulturdaten = field(default_factory=Kulturdaten)
