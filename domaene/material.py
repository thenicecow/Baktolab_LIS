from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domaene.basis import BasisModell


@dataclass(slots=True)
class Material(BasisModell):
    id: str
    patient_id: str
    materialtyp_code: str
    klinische_frage_code: str
    abnahmedatum: date
    eingangsdatum: date
