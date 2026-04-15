from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class DateiAblageDefinition:
    """Beschreibt die spätere dateibasierte Ablage in Switchdrive oder WebDAV."""

    ordner: str
    dateiname: str

    @property
    def relativer_pfad(self) -> str:
        return str(PurePosixPath(self.ordner) / self.dateiname)


DATEI_PATIENTEN = DateiAblageDefinition(
    ordner="patienten",
    dateiname="patienten.json",
)

DATEI_MATERIALIEN = DateiAblageDefinition(
    ordner="materialien",
    dateiname="materialien.json",
)
