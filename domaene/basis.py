from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BasisModell:
    """Gemeinsame Basis für spätere Fachmodelle."""

    erstellt_am: Optional[datetime] = None
    erstellt_von_user_id: Optional[str] = None
