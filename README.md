# BaktoLab - Laborinformationssystem (LIS)

Ein funktionales, schlankes Laborinformationssystem zur Digitalisierung und Optimierung mikrobiologischer Labor-Workflows in der Arztpraxis und im Labor.

* **Projekt-URL:** https://baktolab.streamlit.app
* **Entwicklungsumgebung:** VS Code, Python, Streamlit

---

## Projektkontext

Dieses Projekt entstand im Rahmen eines Informatik-Moduls im Studiengang Biomedizinische Labordiagnostik und verfolgt das Ziel, einen praxisnahen Laborworkflow digital und verständlich abzubilden.

---

## Autorinnen und Autoren

* Kevin Engehausen (engehkev@students.zhaw.ch)
* David Hascher (haschdav@students.zhaw.ch)
* Léa Grandchamp (grandlea@students.zhaw.ch)
* Brigit Marxer (marxebri@students.zhaw.ch)

---

## Über das Projekt

„BaktoLab“ wurde entwickelt, um den dringenden Bedarf an einem technologischen Wechsel in der Laborinformationstechnik aufzuzeigen. Viele bestehende Systeme sind visuell überladen und unstrukturiert. 

Dieses System richtet sich konsequent als **Fachanwendung an Laborpersonal**. Um einen ablenkungsfreien, schnellen und präzisen Workflow zu garantieren, wurde bewusst auf illustrative oder rein dekorative Elemente verzichtet. Die App konzentriert sich stattdessen auf eine klare, strukturierte Datenarchitektur, die den realen Anforderungen im Laboralltag gerecht wird.

### Zentrale Features
* **Durchgängiger Workflow:** Von der Patientenaufnahme bis zur Befunderstellung.
* **Resistenzprüfung:** Visuelle Aufbereitung von Antibiotika-Resistenztests.
* **PDF-Befundexport:** Direktes Generieren und Exportieren eines validen Laborbefundes als PDF-Dokument.

---

## Dokumentation im Repository

Zusätzliche Projektartefakte befinden sich im Ordner `docs/`, unter anderem:

* App Nutzertest
* MVP_Reflexion
* Produktroadmap
* Reflexion
* Wireframe-Nutzertest
* Wirefram-Storyboard
* persona

---

## Bedienungsanleitung (App Walkthrough)

Um den digitalisierten Laborworkflow in BaktoLab Schritt für Schritt zu durchlaufen, nutze die Navigation in der Sidebar:

### Schritt 1: Authentifizierung (Login)
* Navigiere im Menü auf **Login / Registrierung**.
* Melde dich mit deinem Labor-Logindaten an 

### Schritt 2: Patientenaufnahme (Stammdaten)
* Gehe zum Bereich **Patient erfassen**.
* Erfasse die demografischen Daten des Patienten (Name, Vorname, Geburtsdatum, Geschlecht). Diese Daten bilden die Basis für die spätere Zuordnung.

### Schritt 3: Materialaufnahme (Probenbestellung)
* Wechsele zum Menüpunkt **Material erfassen**.
* Wähle den Patienten aus
* Wähle die Materialart (z. B. Urin, Abstrich, Sputum) und erfasse das Entnahmedatum (die volle Nutzung zurzeit nur mit Urin und Bakteriologie allgemein möglich).

### Schritt 4: Laboranalytik & Resistenzprüfung
* Der Bereich **Kulturen ablesen** öffnet sich automatisch.
* Keim Auswählen umd Keimzahl, k4(kleiner 10'000 Koloniebildende Einheiten),p4(10'000 Koloniebildende Einheiten),p5 (100'000 Koloniebildende Einheiten), g5 (>100'000 Koloniebildende Einheiten) --> Wachstum (Bild) Bestätigen
* Keim Rolle wird automatisch festgelegt
* Weiteren Keim hinzufügen oder Kulturdaten Speichern und Beurteilung berechnen (Es wird angezeigt was gemacht werden muss ID und Resi zum Bespiel.)
* Valdieren und Befund öffnen --> Der Befund öffnet sich automatisch

### Schritt 5: Validierung & PDF-Befundexport
* Befund als PDF Herunterladen (ganz oben) 
* Mikrobiologischer Befund wird angezeigt

### Schritt 6: Resistenzmonitoring
Diese Seite ist unabhängig für die Spüitalhygiene oder die Infektiologie gedacht.

* Keim auswählen
* Anzahl getesteter Isolate (z.b 20)
* Anzahl resistenter Isolate (z.b 1)
* Monat auswählen
* Jahr auswählen
* Berechnen und speichern
* visuelle Darstellungen werden angezeigt(es wurden schon einige Erfasst)
* CSV der Daten kann heruntergeladenb werden bei der Grafik oben rechts

### Besonderheiten
* Hilfe und Glossar, alle Fachbegriffe und wissenwertes zur APP ist dort beschrieben
* Patientendetail beachten! Unter Pateintenübersicht kann unter Detail der Workflowstatus pro Patient angezeigt werden! Weiter kann man in der Patientenübersicht unter Detals die Person auch definitv löschen es erscheint eine Warnmeldung und ein Kontrollhäckchen muss angeklickt werden. 
* Fallstatus Seite für die Überischt was noch zu tun ist
