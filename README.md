# Laborinformationssystem (LIS) Baktolab

Diese Applikation dient der digitalen Erfassung, Verwaltung und Auswertung mikrobiologischer Labordaten im Rahmen eines Studienprojekts.
Sie richtet sich an Laborpersonal und unterstützt dabei, Patientendaten, Materialien und erste Auswertungsschritte strukturiert zu dokumentieren.

---

## Ziel der App

Ziel ist die Entwicklung eines verständlichen und praxisnahen Laborinformationssystems, das:

- Patientendaten zentral erfasst
- Materialien patientenbezogen dokumentiert
- Kulturdaten für ausgewählte Materialien speicherbar macht
- ein einfaches Resistenzmonitoring mit Verlauf und Visualisierung unterstützt
- den geplanten Laborablauf in einer klaren Benutzerführung abbildet

Die Anwendung ist bewusst einfach gestaltet, damit auch Nutzerinnen und Nutzer mit geringer technischer Affinität sicher damit arbeiten können.

---

## Aktueller Funktionsstand

### Login und Benutzerkonto
- Anmeldung bestehender Benutzer
- Erstellung eines neuen Benutzerkontos
- Passwort-Zurücksetzen mit temporärem Passwort

### Dashboard
- Zentrale Startseite der Anwendung
- Direkter Einstieg in die wichtigsten Arbeitsbereiche

### Patienten erfassen
- Erfassung neuer Patienten
- Automatische Vergabe einer Patienten-ID

### Patientenübersicht
- Übersicht aller erfassten Patienten
- Suche nach Vorname oder Nachname
- Öffnen der Patientendetails
- Bearbeiten und Löschen von Patienten

### Patientendetails
- Anzeige der Stammdaten
- Übersicht der zugehörigen Materialien
- Filter nach Materialtyp und Analyse
- Anzeige von Ansatzhinweisen

### Material erfassen
- Erfassung neuer Materialien für bestehende Patienten
- Auswahl von Materialtyp, Analyse, Abnahmedatum und Eingangsdatum

### Kulturen ablesen
- Erfassung von Kulturdaten für unterstützte Materialien
- Aktuell unterstützt für Urin mit der Analyse "Allgemeine Bakteriologie"
- Speicherung und Berechnung einer materialbezogenen Beurteilung

### Resistenzmonitoring
- Eingabe von Keim, Antibiotikum und Fallzahlen
- Berechnung der Resistenzrate
- Speicherung benutzerspezifischer Verlaufsdaten
- Tabellarische und grafische Darstellung

---

## Nutzung

1. Anwendung starten und anmelden.
2. Im Dashboard einen Bereich auswählen.
3. Zuerst einen Patienten erfassen.
4. Danach Material für diesen Patienten erfassen.
5. In den Patientendetails weiterarbeiten.
6. Bei unterstützten Materialien optional die Seite **Kulturen ablesen** öffnen.
7. Für Resistenzauswertungen die Seite **Resistenzmonitoring** verwenden.

---

## Technische Umsetzung

- Entwicklung mit `Python` und `Streamlit`
- Dateibasierte Datenablage über WebDAV in Switchdrive
- Modulare Struktur mit getrennten Bereichen für:
  - `views/` für Seiten
  - `functions/` für Fachlogik
  - `persistenz/` für Datenzugriff
  - `domaene/` für Modelle und Lookup-Werte
  - `ui/` für wiederverwendbare Oberflächenelemente

---

## Dokumentation im Repository

Zusätzliche Projektartefakte befinden sich im Ordner `docs/`, unter anderem:

- Persona
- Produkt-Roadmap
- Wireframes
- Reflexion zum MVP
- Dokumentation eines frühen Wireframe-Nutzertests

Diese Dokumente zeigen den Entwicklungsprozess. Nicht alle dort beschriebenen Ideen sind im aktuellen Projektstand umgesetzt.

---

## Autorinnen und Autoren

- Kevin Engehausen (`engehkev@students.zhaw.ch`)
- David Hascher (`haschdav@students.zhaw.ch`)
- Léa Grandchamp (`grandlea@students.zhaw.ch`)
- Brigit Marxer (`marxebri@students.zhaw.ch`)

---

## Projektkontext

Dieses Projekt entstand im Rahmen eines Informatik-Moduls im Studiengang Biomedizinische Labordiagnostik und verfolgt das Ziel, einen praxisnahen Laborworkflow digital und verständlich abzubilden.
