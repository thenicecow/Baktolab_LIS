# Laborinformationssystem (LIS) Baktolab

Diese Applikation dient der digitalen Erfassung, Verwaltung und Analyse mikrobiologischer Labordaten im Rahmen eines Studienprojekts.  
Sie richtet sich an Laborpersonal (z. B. in der Mikrobiologie) und unterstützt dabei, Arbeitsprozesse effizient zu dokumentieren und Resistenzanalysen strukturiert durchzuführen.

---

## ✨ Ziel der App

Ziel ist die Entwicklung eines benutzerfreundlichen und praxisnahen Laborinformationssystems, das:

- Patientendaten, Materialien und Laboranalysen systematisch erfasst  
- mikrobiologische Prozesse wie Identifikation und Resistenzbestimmung unterstützt  
- komplexe Informationen verständlich und strukturiert darstellt  
- Laborpersonal im Arbeitsalltag entlastet und Fehler reduziert  

Die Anwendung ist bewusst einfach gestaltet, um auch bei neuen Technologien eine intuitive Nutzung zu ermöglichen – insbesondere für erfahrenes Laborpersonal mit geringer technischer Affinität.

---

## 🧭 Funktionen der App

### Login & Registrierung(V0)
- Anmeldung bestehender Benutzer  
- Erstellung eines neuen Benutzerkontos  

### Dashboard(V0)
- Zentrale Startseite der Anwendung  
- Navigation zu allen Hauptfunktionen (Patienten, Material, Auswertung)  

### Patientenaufnahme(V0)
- Eingabemaske zur Erfassung von Patientendaten (ID, Name, Geburtsdatum, Geschlecht, Station)  

### Materialaufnahme(V0)
- Formular zur Aufnahme und Verwaltung von Probenmaterialien (z. B. Blut, Urin, Agarplatten)  

### Wachstum / Keimzahl-Auswertung(V0)
- Eingabemaske zur Auswertung der Platten:
  - Identifikationsnummer  
  - Anzahl Kolonien  
  - Wachstum / Keimzahl  
- Strukturierte Erfassung mehrerer Proben gleichzeitig  

### Plattenansatz & Inkubation (V1)
- Übersicht über angesetzte Proben  
- Anzeige von Medium, Datum und Inkubationsbedingungen  

### Resistenzrechner (V2)
- Eingabe von Keim, Antibiotikum und Hemmhofdurchmesser  
- Interpretation nach EUCAST (Sensibel / Resistenz / Intermediär)  

### Ergebnisse / Befund (V2)
- Übersicht der erfassten und berechneten Resultate  
- Zusammenführung von Keimzahl, Identifikation und Resistenzdaten  

---

## 🚀 Nutzungshinweise (Geplant noch nicht verfügbar)

- Öffne die Anwendung (lokal oder im Deployment)

- Wähle im Dashboard den gewünschten Bereich:
  - **Patientenaufnahme** → neuen Patienten erfassen  
  - **Materialaufnahme** → Material oder Probe erfassen  
  - **Resistenzrechner** → Antibiogramm berechnen  
  - **MALDI-TOF** → Identifikationsergebnis eingeben  

- Gib die Daten über die Eingabemasken ein  

- Klicke auf **„Speichern“** oder **„Berechnen“**, um die Eingaben zu verarbeiten  

- Wechsel zur **Ergebnis-/Übersichtsseite**, um Resultate und Analysen einzusehen  

---

## 🧪 Technische Umsetzung (optional)

- Entwicklung mit **Python & Streamlit**  
- Modulare Struktur:
  - `pages/` → einzelne Funktionsbereiche (Patient, Material, Analyse etc.)  
  - `utils/` → Datenverarbeitung, Berechnungen (z. B. EUCAST), UI-Komponenten  

---

## 👥 Autoren

- Kevin Engehausen (engehkev@students.zhaw.ch)
- David Hascher (haschdav@students.zhaw.ch)
- Léa Grandchamnp (grandlea@students.zhaw.ch)
- Brigit Marxer (marxebri@students.zhaw.ch)


---

## 🧾 Projektkontext

Dieses Projekt entstand im Rahmen eines Studienprojekts und dient der praktischen Umsetzung eines digitalen Laborinformationssystems mit Fokus auf mikrobiologische Diagnostik und Resistenzanalyse.