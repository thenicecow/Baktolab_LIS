# Kritische Reflexion: Entwicklung des Laborinformationssystems (LIS) „BaktoLab“

**Eingereicht bei:** Samuel Wehrli
**Projekt-URL:** https://baktolab.streamlit.app/  
**Repository:** https://github.com/thenicecow/Baktolab_LIS  

---

### 1. Zielsetzung und Design-Philosophie
Das Ziel von „BaktoLab“ war die Entwicklung eines funktionalen Laborinformationssystems (LIS) in Python und Streamlit, das den mikrobiologischen Workflow von der Probenaufnahme bis zum Befund effizient digitalisiert. 

Die App ist für Laien schwer zugänglich – dies war jedoch eine bewusste Design-Entscheidung. In der Laborwelt besteht ein dringender Bedarf an einem technologischen Wechsel weg von überladenen Systemen. Unser Fokus lag konsequent auf einer Fachanwendung für Laborpersonal. Um einen ablenkungsfreien, schnellen Workflow zu garantieren, haben wir bewusst auf illustrative Elemente verzichtet, da diese nicht in ein produktives Laborumfeld gehören.

### 2. Technische Umsetzung und erreichte Meilensteine
Entgegen der ursprünglichen Befürchtung, nur ein reines Basis-MVP (Version 01) umsetzen zu können, wurden wichtige Fachmodule der höheren Versionen erfolgreich implementiert:
*   **Visualisierung der Resistenzprüfung:** Eine programmtechnisch vollständige Aufbereitung der Testergebnisse.
*   **PDF-Export des Befundes:** Ein direkt aus der App generierbares PDF-Dokument für einen mikorbiologischen Befund

### 3. Kritische Analyse: Präsentation und Marktreife
Rückblickend müssen zwei wesentliche Schwachpunkte kritisch reflektiert werden:

1. **Zeitdruck bei der Präsentation:** Aufgrund des hohen Zeitdrucks während der Abschlusspräsentation gelang es uns nicht, alle Facetten der App effektiv zu demonstrieren. Besonders die integrierte Visualisierung der Resistenzprüfung konnte nicht live gezeigt werden. Die Funktionen sind jedoch im Code und über die bereitgestellte Web-URL vollumfänglich prüfbar.
2. **Fehlende Marktreife:** Uns ist bewusst, dass die App in diesem Stadium keinesfalls für den echten Markt bereit ist. Um eine reale Zulassung und Praxistauglichkeit zu erreichen, wären tiefgreifende Anpassungen nötig – insbesondere in den Bereichen Datensicherheit (DSGVO/Patientendatenschutz), regulatorische Compliance für Medizinprodukte, Schnittstellen-Anbindungen (HL7/LIMS) sowie eine umfassende Fehlerbehandlung (Error Handling).

### 4. Fazit
Das Projekt „BaktoLab“ zeigt, dass uns die Abbildung eines schlanken, übersichtlichen Labor-Workflows grundsätzlich gelungen ist. Neben der Vertiefung unserer Python-Kenntnisse lag der grösste Lerneffekt im professionellen Scope-Management: Der Spagat zwischen technischer Machbarkeit, fachlicher Reduktion und dem kritischen Faktor Zeit im Projekt- und Präsentationsmanagement.