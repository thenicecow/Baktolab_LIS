# Laborinformationssystem (LIS) mit Resistenzanalyse

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

### Patientenaufnahme
- Erfassung von Patientendaten (Name, Geburtsdatum, Geschlecht etc.)

### Materialaufnahme
- Verwaltung von Probenmaterialien (z. B. Blut, Urin, Agarplatten)

### Resistenzrechner
- Eingabe von Hemmhofdurchmessern  
- Interpretation nach EUCAST (Sensibel / Resistenz / Intermediär)  

### Plattenansatz & Inkubation (Übersicht)
- Anzeige von:
  - Medium (z. B. Agarplatte)  
  - Temperatur  
  - Inkubationsdauer  
  - Atmosphäre  

### Wachstum/ Keimzahl Resultierung
- Eingabe von:
  - Identifikationsnummer
  - Anzahl der verschiedenen Kolonien
  - Gesamtkeimzahl
  - Keimzahl einzelner Resultate
- Anzeige von:
  - MALDI-TOF Eingabefelderen entsprechend verschiedener Kolonien

### Ergebnisse / Befund
- Übersicht der Analyseergebnisse  
- Darstellung von Resistenzprofilen  

### Dashboard
- Übersicht über aktuelle Aktivitäten und Schnellzugriff auf Funktionen  

---

## 🚀 Nutzungshinweise

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