from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domaene.basis import BasisModell


@dataclass(slots=True)
class Patient(BasisModell):
    id: str
    vorname: str
    nachname: str
    geburtsdatum: date
    geschlecht: str
