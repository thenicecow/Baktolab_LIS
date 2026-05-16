"""Fachliche Inhalte und Kontexte für das Dashboard."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal


ButtonTyp = Literal["primary", "secondary"]
Aktionsgroesse = Literal["gross", "klein"]


@dataclass(frozen=True, slots=True)
class DashboardAktionskarte:
    """Beschreibt eine fachliche Aktionskarte des Dashboards."""

    titel: str
    beschreibung: str
    button_text: str
    seitenpfad: str
    button_typ: ButtonTyp = "secondary"
    groesse: Aktionsgroesse = "klein"
    icon: str | None = None
    color: str | None = None


AKZENTFARBEN_NACH_TITEL: dict[str, str] = {
    "Patient erfassen": "#8B5CF6",
    "Material erfassen": "#14B8A6",
    "Patientenuebersicht": "#64748B",
    "Resistenzmonitoring": "#F59E0B",
    "Kulturen ablesen": "#22C55E",
    "Befund": "#16A34A",
}

ANZEIGETEXTE_NACH_TITEL: dict[str, str] = {
    "Patientenuebersicht": "Patientenübersicht",
}

DASHBOARD_UNTERTITEL = (
    "Zentrale Startseite für das Laborinformationssystem im Modul "
    "Biomedizinische Labordiagnostik."
)

DASHBOARD_HINWEIS = (
    "Empfohlener Ablauf: zuerst Patienten erfassen, danach Material erfassen "
    "und anschliessend in der Patientenübersicht weiterarbeiten. "
    "Der durchgängige Demo-Workflow mit Kulturen, Beurteilung und Befund "
    "ist aktuell auf Urin mit der Analyse 'Allgemeine Bakteriologie' begrenzt."
)


def hole_akzentfarbe_fuer_titel(titel: str | None) -> str | None:
    """Liefert die definierte Akzentfarbe für Dashboard-Karten und Unterseiten."""
    if titel is None:
        return None

    bereinigt = titel.strip()
    if not bereinigt:
        return None

    return AKZENTFARBEN_NACH_TITEL.get(bereinigt)


def hole_anzeigetext_fuer_titel(titel: str | None) -> str | None:
    """Liefert einen sprachlich formatierten Anzeigetext für Seitentitel."""
    if titel is None:
        return None

    bereinigt = titel.strip()
    if not bereinigt:
        return None

    return ANZEIGETEXTE_NACH_TITEL.get(bereinigt, bereinigt)


_DASHBOARD_AKTIONSKARTEN: tuple[DashboardAktionskarte, ...] = (
    DashboardAktionskarte(
        titel="Patient erfassen",
        beschreibung="Neue Patienten anlegen und Stammdaten erfassen.",
        button_text="Patientenerfassung öffnen",
        seitenpfad="views/patienten_erfassen.py",
        button_typ="primary",
        groesse="gross",
        icon=":material/person_add:",
        color=hole_akzentfarbe_fuer_titel("Patient erfassen"),
    ),
    DashboardAktionskarte(
        titel="Material erfassen",
        beschreibung="Neues Material für einen bestehenden Patienten erfassen.",
        button_text="Materialerfassung öffnen",
        seitenpfad="views/material_erfassen.py",
        button_typ="primary",
        groesse="gross",
        icon=":material/science:",
        color=hole_akzentfarbe_fuer_titel("Material erfassen"),
    ),
    DashboardAktionskarte(
        titel="Patientenuebersicht",
        beschreibung="Alle bereits erfassten Patienten anzeigen und durchsuchen.",
        button_text="Patientenübersicht öffnen",
        seitenpfad="views/patientenuebersicht.py",
        groesse="klein",
        icon=":material/groups:",
        color=hole_akzentfarbe_fuer_titel("Patientenuebersicht"),
    ),
    DashboardAktionskarte(
        titel="Resistenzmonitoring",
        beschreibung=(
            "Einfaches Demo-Modul für ausgewählte Keime und Antibiotika "
            "mit Verlaufsgrafik."
        ),
        button_text="Resistenzmonitoring öffnen",
        seitenpfad="views/resistenzmonitoring.py",
        groesse="klein",
        icon=":material/functions:",
        color=hole_akzentfarbe_fuer_titel("Resistenzmonitoring"),
    ),
    DashboardAktionskarte(
        titel="Kulturen ablesen",
        beschreibung=(
            "Kulturdaten erfassen und eine Beurteilung nur für Urin mit der "
            "Analyse 'Allgemeine Bakteriologie' berechnen."
        ),
        button_text="Kulturen ablesen öffnen",
        seitenpfad="views/kulturen_ablesen.py",
        groesse="klein",
        icon=":material/biotech:",
        color=hole_akzentfarbe_fuer_titel("Kulturen ablesen"),
    ),
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
    """Liefert alle fachlichen Aktionskarten für das Dashboard."""
    return _DASHBOARD_AKTIONSKARTEN


def hole_hauptaktionskarten() -> tuple[DashboardAktionskarte, ...]:
    """Liefert die gross dargestellten Hauptaktionen des Dashboards."""
    return tuple(
        karte for karte in _DASHBOARD_AKTIONSKARTEN if karte.groesse == "gross"
    )


def hole_nebenaktionskarten() -> tuple[DashboardAktionskarte, ...]:
    """Liefert die kleiner dargestellten Nebenaktionen des Dashboards."""
    return tuple(
        karte for karte in _DASHBOARD_AKTIONSKARTEN if karte.groesse == "klein"
    )
