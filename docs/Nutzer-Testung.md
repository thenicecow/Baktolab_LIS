# Nutzertest Mikrobiologie LIS

## Einordnung

Dieser Test ist ein Nutzertest mit einer erfahrenen mikrobiologie BMA auf Basis des vorhandenen Wireframes.

---

## 1. Hypothesenbildung

### Was wir zu wissen glauben

* Das Produkt dient der **Erfassung und Verarbeitung von Patienten-, Proben- und Laborinformationen**.
* Die wichtigsten Aufgaben sind:

  * neues Konto erstellen
  * neuen Patienten anlegen
  * Material zu einer Probe erfassen
  * Keime und Resultate erfassen
  * Auswertungen oder Übersichten aufrufen
* Das **Dashboard** ist der zentrale Einstiegspunkt nach dem Login.

### Was wir nicht wissen

* Ob die **Registrierung** überhaupt Teil des realen Alltags ist oder nur ein technischer Einstieg.
* Welche Felder **Pflichtfelder** sind.
* Ob die Reihenfolge **Patient zuerst, dann Material, dann Resultat** der echten Arbeitslogik entspricht.
* Ob Begriffe wie **Fragestellung**, **Plattenanzahl**, **Resistenzrechner**, **Wachstum / Keimzahl** und **Ergebnisse / Befund** für die Zielgruppe unmittelbar klar sind.
* Wie der Nutzer nach dem Speichern erkennt, dass ein Schritt erfolgreich abgeschlossen wurde.

### Was wir testen wollen

* Versteht die Testperson ohne Erklärung, **wo sie beginnen muss**?
* Findet sie die richtige Funktion, um einen **neuen Patienten anzulegen**?
* Versteht sie die Felder zur **Materialaufnahme**?
* Versteht sie die Seite zur **Keim- bzw. Resultaterfassung**?
* Erkennt sie die **primären Aktionen** wie Speichern, Weitergehen oder Abbrechen?
* Ist der Ablauf für die Testperson **selbsterklärend genug**, um ohne Hilfe voranzukommen?

### Wie wir den Test bewerten

Wir bewerten den Test danach,

* ob die Testperson die Aufgabe **ohne Erklärung** starten kann,
* ob sie die **richtigen Klickziele** findet,
* ob die Begriffe und Felder **verständlich** sind,
* ob Unsicherheiten oder Fehlinterpretationen auftreten,
* ob sie den Ablauf als **logisch** erlebt.

### Was ein Erfolg ist

Ein Test ist aus Produktsicht erfolgreich, wenn eine Testperson:

* den Einstieg versteht,
* die Kernaufgaben ohne viel Hilfe findet,
* die Formulare logisch einordnen kann,
* die wichtigsten Begriffe richtig interpretiert,
* und ohne grössere Unsicherheit von einem Schritt zum nächsten kommt.

---

## 2. Testsetup für diesen Test

### Testperson

**Rolle:** langjärige Mitarbeiterin, BMA
**Digitales Niveau:** durchschnittlich
**Domänenwissen:** teilweise vorhanden, aber nicht tief projektspezifisch
**Ziel:** möglichst rasch Patient, Probe und Ergebnis korrekt erfassen

### Testaufgaben

1. Ein neues Konto erstellen
2. Auf dem Dashboard die richtige Funktion für einen neuen Patienten finden
3. Einen neuen Patienten anlegen
4. Material zu einer Probe erfassen
5. Eine Keim- bzw. Resultaterfassung für eine Probe verstehen und ausfüllen

---

## 3. Grundregeln für die Durchführung

Diese Regeln sollen beim Test eingehalten werden:

1. Den Prototyp nicht erklären
2. Der Prototyp muss selbsterklärend sein
3. So früh und so oft wie möglich scheitern
4. Kill-your-Darling-Mindset
5. Den Prototyp niemals verteidigen
6. Fragen mit Fragen beantworten
7. Es braucht nicht viele Testpersonen

### Beispiel für Moderationsverhalten

Wenn die Testperson fragt:
**„Was bedeutet das hier?“**

Nicht antworten mit:
**„Das ist für die Resistenzangabe.“**

Sondern zurückfragen:
**„Was würdest du darunter verstehen?“**
oder
**„Was würdest du als Nächstes tun?“**

---

## 4. Testdurchlauf

## Aufgabe 1: Konto erstellen

### Erwartung

Die Testperson erkennt sofort, dass sie ein neues Konto anlegen kann und welche Angaben nötig sind.

### Beobachtung als Testnutzer

* Die Seite ist klar als **Registrierung / Neues Konto erstellen** erkennbar.
* Die Felder **Name**, **Benutzername**, **Passwort** und **Passwort bestätigen** sind grundsätzlich verständlich.
* Der Button **Konto erstellen** ist als Hauptaktion erkennbar.
* Der Link **zurück zum Login** ist sinnvoll.

### Probleme

* Es ist nicht ersichtlich, welche Felder **Pflichtfelder** sind.
* Es fehlen Hinweise zu Passwortregeln.
* Es fehlt jede Form von Fehler- oder Erfolgskommunikation.
* Es ist unklar, ob mit **Name** der Klarname oder etwas anderes gemeint ist.

### Bewertung

**Grundsätzlich verständlich**, aber noch zu roh für einen sicheren und selbsterklärenden Produktfluss.

---

## Aufgabe 2: Auf dem Dashboard die richtige Funktion finden

### Erwartung

Die Testperson erkennt, wo sie als Erstes klicken muss, wenn sie einen neuen Fall erfassen will.

### Beobachtung als Testnutzer

* Das Dashboard vermittelt klar: Hier gibt es mehrere Hauptfunktionen.
* **Patientenaufnahme** und **Materialaufnahme** springen als erste sinnvolle Arbeitsbereiche ins Auge.
* Die Kachelstruktur ist leicht erfassbar.
* Suche, Profil und Logout sind grundsätzlich als globale Navigation erkennbar.

### Probleme

* Es ist nicht klar, **was der empfohlene Startpunkt** im Alltag ist.
* Einige Begriffe wirken fachlich, aber nicht selbsterklärend, z. B.:

  * Übersicht Plattenanzahl
  * Resistenzrechner
  * Wachstum / Keimzahl
  * Ergebnisse / Befund
* Die Zeile links oben mit dem Namen bzw. Nutzereintrag wirkt unklar.
* Die Suchfunktion ist sichtbar, aber ihr Zweck bleibt offen.

### Bewertung

**Orientierung okay**, aber die Informationsarchitektur wirkt noch **modulartig statt prozessorientiert**.

---

## Aufgabe 3: Neuen Patienten anlegen

### Erwartung

Die Testperson kann einen neuen Patienten vollständig erfassen und speichern.

### Beobachtung als Testnutzer

* Der Titel **Patientenaufnahme** ist klar.
* **Neuen Patienten anlegen** macht den Zweck eindeutig.
* Die Felder **Proben-ID**, **Name**, **Geb. Dat.**, **Geschlecht** und **Station** sind grundsätzlich plausibel.
* Das Datumsfeld und das Dropdown signalisieren den Eingabetyp gut.

### Probleme

* Es gibt **keinen klar sichtbaren Speichern- oder Erstellen-Button**.
* Damit ist die Aufgabe faktisch **nicht sauber abschliessbar**.
* Es ist unklar, ob **Proben-ID** hier manuell vergeben wird oder aus einem anderen Schritt stammt.
* Es ist unklar, ob der Nutzer zuerst den Patienten oder zuerst die Probe anlegen soll.
* Die kleine Karte oben rechts ist in ihrer Funktion nicht selbsterklärend.
* **Zurück** ist sichtbar, aber eine primäre Abschlussaktion fehlt.

### Bewertung

**Inhaltlich teilweise verständlich, aber funktional unvollständig.**

### Kritischer Befund

Dies ist aus Nutzersicht ein **kritisches Problem**, weil der wichtigste Use Case nicht sauber zu Ende geführt werden kann.

---

## Aufgabe 4: Material zu einer Probe erfassen

### Erwartung

Die Testperson versteht, welches Material zu welcher Probe gehört und kann den Datensatz speichern.

### Beobachtung als Testnutzer

* Der Titel **Materialaufnahme** ist verständlich.
* Die Eingabefelder wirken wie ein klassisches Erfassungsformular.
* **Abnahmedatum** und **Eingangsdatum** sind fachlich nachvollziehbar.
* Der Button **Speichern** ist vorhanden und als Hauptaktion erkennbar.

### Probleme

* Es ist unklar, ob diese Seite an einen **bereits angelegten Patienten** gekoppelt ist oder unabhängig funktioniert.
* Die Felder **Proben-ID** und **Name** wirken redundant oder zumindest potenziell fehleranfällig, wenn der Kontext nicht automatisch übernommen wird.
* **Fragestellung** könnte für Fachnutzer verständlich sein, für neue Nutzer aber erklärungsbedürftig bleiben.
* **Dashboard** und **Abbruch** stehen optisch relativ nahe bei **Speichern**. Das erhöht das Risiko eines Fehlklicks.
* Es fehlt Feedback nach dem Speichern.

### Bewertung

**Brauchbar, aber kontextschwach.**
Die Seite ist verständlicher als die Patientenaufnahme, aber die Zuordnung zwischen Patient, Probe und Material ist nicht robust genug sichtbar.

---

## Aufgabe 5: Keim- bzw. Resultaterfassung verstehen und ausfüllen

### Erwartung

Die Testperson versteht schnell, wie viele Keime erfasst werden, was pro Keim einzutragen ist und was die Resistenzoptionen bedeuten.

### Beobachtung als Testnutzer

* Es ist erkennbar, dass sich die Seite um **Keime** und um mehrere Keim-Einträge dreht.
* Die Spalten **Keim 1**, **Keim 2**, **Keim 3** deuten auf mehrere zu erfassende Ergebnisse hin.
* **Proben-ID** oben links schafft grundsätzlich Kontext.

### Probleme

* Dies ist die **am wenigsten selbsterklärende Seite** des gesamten Wireframes.
* Es bleibt unklar:

  * was das Feld mit der **3** bedeutet
  * was genau mit **Gesamtkeimzahl** gemeint ist
  * wie sich **Gesamtkeimzahl** zu **Keim 1 bis 3** verhält
  * was die einzelnen Eingabefelder pro Keim genau bedeuten
  * was **mit Resi** und **ohne Resi** konkret auslöst
  * ob **Medi** und **Mischflora** die korrekten Begriffe sind oder nur Platzhalter
* Die visuelle Hierarchie hilft nicht genug, um den Ablauf zu verstehen.
* Die Seite setzt offensichtlich **starkes Vorwissen** voraus.

### Bewertung

**Nicht selbsterklärend.**
Für einen Nutzertest ist genau diese Seite sehr wertvoll, weil hier mit hoher Wahrscheinlichkeit die meisten Missverständnisse sichtbar werden.

---

## 5. Testprotokoll pro Screen

| Screen            | Eindruck / Beobachtung                                                              |
| ----------------- | ----------------------------------------------------------------------------------- |
| Registrierung     | Grundsätzlich verständlich, aber ohne Feldlogik, Validierung und Rückmeldung        |
| Dashboard         | Module sichtbar, aber nicht klar prozessorientiert aufgebaut                        |
| Patientenaufnahme | Felder verständlich, aber ohne klare Abschlussaktion                                |
| Materialaufnahme  | Besser verständlich als Patientenaufnahme, aber Kontext zu Patient und Probe unklar |
| Keime / Resultat  | Fachlich und visuell am wenigsten verständlich, stark erklärungsbedürftig           |

---

## 6. Auswertung im Test-Grid

## Was war gut?

* Die wichtigsten Bereiche sind auf dem Dashboard grundsätzlich sichtbar.
* Registrierung, Patientenaufnahme und Materialaufnahme sind als Grundkonzepte erkennbar.
* Datumsfelder und Dropdowns machen die erwartete Eingabeart sichtbar.
* Das medizinisch-labornahe Setting wird deutlich.
* Die Anwendung wirkt funktional und auf reale Arbeitsschritte ausgerichtet.

## Was war schlecht?

* Die **Patientenaufnahme hat keine klare primäre Abschlussaktion**.
* Der Gesamtfluss zwischen **Patient**, **Probe**, **Material** und **Ergebnis** ist nicht klar genug.
* Mehrere Begriffe sind nicht selbsterklärend oder zu stark domänenspezifisch.
* Es fehlen **Hinweise, Validierungen, Statusmeldungen und Erfolgsfeedback**.
* Die **Keim-/Resultateseite** ist ohne Erklärung kaum verständlich.
* Das Dashboard zeigt Funktionen, aber kaum Priorisierung oder empfohlene Reihenfolge.

## Neue Ideen

* Den Hauptworkflow als **geführten Prozess** darstellen:

  1. Patient anlegen
  2. Material erfassen
  3. Resultat erfassen
* Pflichtfelder markieren.
* Patient und Probenkontext dauerhaft oben anzeigen.
* Fachbegriffe mit kurzen Hilfetexten oder Beispielen unterstützen.
* Nach dem Speichern eine klare Rückmeldung geben.
* Die Keimseite vereinfachen und in logische Abschnitte gliedern.

## Neue Probleme

* Hohes Risiko für **Fehlzuordnung von Daten**, wenn Patient und Probe nicht eindeutig verknüpft sind.
* Hohes Risiko für **unvollständige Datensätze**, wenn primäre Aktionen fehlen.
* Hohes Risiko, dass neue Nutzer nur mit Schulung statt durch UI-Verständnis arbeiten können.
* Hohes Risiko, dass Resultaterfassung falsch verstanden oder falsch ausgefüllt wird.
* Hohes Risiko, dass Dashboard-Module zwar sichtbar, aber im Alltag nicht intuitiv priorisiert werden.

---

## 7. Priorisierte Findings

## Prio 1

### 1. Patientenaufnahme ohne klare Abschlussaktion

Die Seite wirkt unvollständig, weil das Anlegen eines Patienten nicht sichtbar abgeschlossen werden kann.

### 2. Keim-/Resultateseite nicht selbsterklärend

Die Begriffe, Felder und Resistenzoptionen sind ohne Vorwissen zu unklar.

## Prio 2

### 3. Hauptworkflow nicht klar genug

Es ist nicht eindeutig, in welcher Reihenfolge Patient, Probe, Material und Resultat erfasst werden.

### 4. Fehlendes Feedback

Der Nutzer erhält keine klare Rückmeldung nach Eingaben oder nach dem Speichern.

### 5. Fachbegriffe nicht ausreichend abgesichert

Mehrere Begriffe wirken intern oder fachlich, aber nicht überall sofort verständlich.

## Prio 3

### 6. Dashboard eher modul- als aufgabenorientiert

Es zeigt Funktionen, aber lenkt neue Nutzer nicht klar genug durch den Prozess.

---

## 8. Fazit

Das Wireframe zeigt eine erkennbare fachliche Struktur, aber der Prototyp ist noch nicht selbsterklärend genug, um ohne Hilfe zuverlässig durch die wichtigsten Aufgaben zu führen.

Die grössten Schwächen liegen nicht in der Idee der Anwendung, sondern in:

* fehlender Klarheit des End-to-End-Workflows
* unklaren oder zu fachlichen Begriffen
* fehlenden Abschluss- und Feedbacksignalen
* einer besonders schwachen Verständlichkeit der Keim-/Resultateseite