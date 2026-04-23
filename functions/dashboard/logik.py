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


DASHBOARD_UNTERTITEL = (
    "Zentrale Startseite für das Laborinformationssystem im Modul "
    "Biomedizinische Labordiagnostik."
)

DASHBOARD_HINWEIS = (
    "Empfohlener Ablauf: zuerst Patienten erfassen, danach Material erfassen "
    "und anschliessend in der Patientenübersicht weiterarbeiten."
)


_DASHBOARD_AKTIONSKARTEN: tuple[DashboardAktionskarte, ...] = (
    DashboardAktionskarte(
        titel="Patienten erfassen",
        beschreibung="Neue Patienten anlegen und Stammdaten erfassen.",
        button_text="Patientenerfassung öffnen",
        seitenpfad="views/patienten_erfassen.py",
        button_typ="primary",
        groesse="gross",
    ),
    DashboardAktionskarte(
        titel="Material erfassen",
        beschreibung="Neues Material für einen bestehenden Patienten erfassen.",
        button_text="Materialerfassung öffnen",
        seitenpfad="views/material_erfassen.py",
        button_typ="primary",
        groesse="gross",
    ),
    DashboardAktionskarte(
        titel="Patientenübersicht",
        beschreibung="Alle bereits erfassten Patienten anzeigen und durchsuchen.",
        button_text="Patientenübersicht öffnen",
        seitenpfad="views/patientenuebersicht.py",
        groesse="klein",
    ),
    DashboardAktionskarte(
        titel="Resistenzmonitoring",
        beschreibung="Resistenzraten erfassen, speichern und grafisch darstellen.",
        button_text="Resistenzmonitoring öffnen",
        seitenpfad="views/addition_calculator.py",
        groesse="klein",
    ),
    DashboardAktionskarte(
        titel="Kulturen ablesen",
        beschreibung="Kulturdaten erfassen und eine Beurteilung für unterstützte Materialien berechnen.",
        button_text="Kulturen ablesen öffnen",
        seitenpfad="views/kulturen_ablesen.py",
        groesse="klein",
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
