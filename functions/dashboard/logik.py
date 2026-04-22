"""Fachliche Inhalte und Kontexte fuer das Dashboard."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal


ButtonTyp = Literal["primary", "secondary"]


@dataclass(frozen=True, slots=True)
class DashboardAktionskarte:
    """Beschreibt eine fachliche Aktionskarte des Dashboards."""

    titel: str
    beschreibung: str
    button_text: str
    seitenpfad: str
    button_typ: ButtonTyp = "secondary"


DASHBOARD_UNTERTITEL = (
    "Zentrale Startseite fuer das Laborinformationssystem im Modul "
    "Biomedizinische Labordiagnostik."
)

DASHBOARD_HINWEIS = (
    "Empfohlener Ablauf: zuerst Patient erfassen, danach Material erfassen "
    "und anschliessend in der Patientenuebersicht weiterarbeiten."
)

DASHBOARD_STANDPUNKTE: tuple[str, ...] = (
    "Dashboard und Kernnavigation sind vorbereitet.",
    "Die Bereiche Patienten, Material und Uebersicht sind bewusst als Platzhalter angelegt.",
    "Domaenenmodell und Persistenz sind strukturell vorbereitet, aber noch ohne Fachlogik.",
)


def hole_anzeige_name(session_state: Mapping[str, object]) -> str:
    """Ermittelt den bevorzugten Anzeigenamen des angemeldeten Benutzers."""
    name = session_state.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()

    username = session_state.get("username")
    if isinstance(username, str) and username.strip():
        return username.strip()

    return "Benutzer"


def hole_dashboard_aktionskarten() -> tuple[DashboardAktionskarte, ...]:
    """Liefert die fachlichen Aktionskarten fuer das Dashboard."""
    return (
        DashboardAktionskarte(
            titel="Patienten erfassen",
            beschreibung=(
                "Neue Patienten anlegen. Die eigentliche Eingabemaske wird in einem "
                "spaeteren Schritt ergaenzt."
            ),
            button_text="Patienten erfassen oeffnen",
            seitenpfad="views/patienten_erfassen.py",
            button_typ="primary",
        ),
        DashboardAktionskarte(
            titel="Material erfassen",
            beschreibung=(
                "Neue Materialien und Proben erfassen. Die fachliche Erfassung "
                "folgt in einem spaeteren Schritt."
            ),
            button_text="Material erfassen oeffnen",
            seitenpfad="views/material_erfassen.py",
        ),
        DashboardAktionskarte(
            titel="Patientenuebersicht",
            beschreibung=(
                "Zukuenftige Uebersicht ueber alle Patienten. Dieser Bereich ist so "
                "vorbereitet, dass spaeter alle Benutzer denselben Bestand sehen."
            ),
            button_text="Patientenuebersicht oeffnen",
            seitenpfad="views/patientenuebersicht.py",
        ),
    )
