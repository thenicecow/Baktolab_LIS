"""Einfache Informationsseite zum Projektstand der App."""

from __future__ import annotations

import streamlit as st


st.title("Laborinformationssystem (LIS)")

st.markdown(
    """
Diese App dient der Erfassung und Verwaltung mikrobiologischer Labordaten.

Sie unterstützt Laborpersonal bei der Aufnahme von Patientendaten, der Erfassung von Materialien
sowie bei der Dokumentation und Auswertung erster Analyseergebnisse.

Aktuell umfasst der sichtbare Projektstand insbesondere die Bereiche Login, Dashboard,
Patientenerfassung, Patientenübersicht, Materialerfassung, Kulturdaten für ausgewählte Materialien
sowie Resistenzmonitoring.

---

## Hinweise zur Nutzung

- Neue Daten können über die einzelnen Eingabemasken erfasst werden.
- Patienten und Materialien werden strukturiert in der App angezeigt.
- Für unterstützte Materialien können Kulturdaten gespeichert und beurteilt werden.
- Im Resistenzmonitoring können Verlaufsdaten tabellarisch und grafisch dargestellt werden.

---

## Benutzerfunktionen

- Login mit Benutzername und Passwort
- Funktion **Passwort vergessen?**
  - erzeugt ein neues temporäres Passwort
  - das Passwort sollte nach der Anmeldung direkt geändert werden
"""
)

st.markdown(
    """
Diese App wurde von folgenden Personen entwickelt:
- Kevin Engehausen (`engehkev@students.zhaw.ch`)
- David Hascher (`haschdav@students.zhaw.ch`)
- Léa Grandchamp (`grandlea@students.zhaw.ch`)
- Brigit Marxer (`marxebri@students.zhaw.ch`)

Begleitung im Modul:
- Samuel Wehrli (`wehs@zhaw.ch`)
"""
)
