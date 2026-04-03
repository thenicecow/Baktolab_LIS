import streamlit as st

st.title("Laborinformationssystem (LIS)")

st.markdown("""
Diese App dient der Erfassung und Verwaltung mikrobiologischer Labordaten.

Sie unterstützt Laborpersonal bei der Aufnahme von Patientendaten, der Erfassung von Materialien sowie bei der Dokumentation und Auswertung von Analyseergebnissen.

Zusätzlich können Resistenzdaten und MALDI-TOF Resultate eingegeben und übersichtlich dargestellt werden.

Mehrere Einträge können gespeichert werden, um Resultate strukturiert zu verwalten und Laborabläufe digital abzubilden.

---

## Hinweise zur Nutzung

- Neue Daten können über die einzelnen Eingabemasken erfasst werden  
- Ergebnisse und Analysen werden nach dem Speichern in der Übersicht angezeigt  

---

## Benutzerfunktionen

- Login-System mit Benutzername und Passwort  
- „Passwort vergessen“-Funktion:
  - Generiert ein neues zufälliges Passwort  
  - Passwort sollte nach dem Login direkt geändert werden  
""")

st.markdown("""
Diese App wurde von folgenden Personen entwickelt:
- Kevin Engehausen (engehkev@students.zhaw.ch)
- David Hascher (haschdav@students.zhaw.ch)
- Léa Grandchamp (grandlea@students.zhaw.ch)
- Brigit Marxer (marxebri@students.zhaw.ch)

Autor: Samuel Wehrli (wehs@zhaw.ch)
""")