from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


SCHWEIZER_ZEITZONE = ZoneInfo("Europe/Zurich")


def aktuelle_zeit() -> datetime:
    return datetime.now(SCHWEIZER_ZEITZONE).replace(microsecond=0)


@dataclass(kw_only=True, slots=True)
class BasisModell:
    erstellt_am: datetime | None = None
    erstellt_von_user_id: str | None = None

    def setze_erstellinformationen_wenn_fehlend(self) -> None:
        if self.erstellt_am is None:
            self.erstellt_am = aktuelle_zeit()
