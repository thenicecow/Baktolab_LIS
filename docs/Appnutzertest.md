# Nutzertest – BactoLab-App

## Ziel des Tests

Wir möchten herausfinden, ob die BactoLab-App intuitiv und selbsterklärend bedienbar ist. Im Zentrum steht der vollständige Ablauf von der Registrierung bis zur Validierung eines Befunds.

Folgende Fragen stehen dabei im Fokus:

- Ist die App ohne zusätzliche Erklärung verständlich bedienbar?
- Ist die Navigation zwischen Dashboard, Patientenerfassung, Materialerfassung, Kulturen ablesen und Validierung logisch?
- Sind die wichtigsten Arbeitsschritte eindeutig erkennbar?
- Gibt es technische oder gestalterische Hürden, zum Beispiel bei Tab-Reihenfolge, Fehlermeldungen, Buttons oder Darstellung?
- Können Nutzer:innen die Kernfunktionen korrekt ausführen, ohne unsicher zu werden oder falsche Aktionen auszuführen?

---

## Hypothese

### Was wissen wir? Was wissen wir nicht?

**Was wir wissen:**

Die App bildet zentrale Arbeitsschritte aus dem Laborprozess ab:

- Registrierung und Login
- Patient:innen erfassen und bearbeiten
- Material erfassen
- Kulturen ablesen
- Befund validieren

Die App soll Nutzer:innen Schritt für Schritt durch diese Abläufe führen und dabei möglichst selbsterklärend sein.

**Was wir nicht wissen:**

- Ob die Nutzer:innen die Reihenfolge der Arbeitsschritte ohne Anleitung verstehen.
- Ob die Navigation über Dashboard, Detailseiten und Funktionsseiten eindeutig genug ist.
- Ob die Seite «Kulturen ablesen» verständlich genug ist, um mehrere Keime korrekt zu erfassen.
- Ob Fehlermeldungen, Buttons und Speicherlogik klar genug formuliert und dargestellt sind.
- Ob technische Details wie Tab-Reihenfolge und Layout die Bedienung stören.

### Was möchten wir testen?

Wir möchten testen, ob eine Testperson die App ohne zusätzliche Erklärung bedienen kann. Besonders wichtig ist, ob die Testperson:

- sich registrieren und einloggen kann,
- Patient:innen erfassen, suchen und bearbeiten kann,
- Material erfassen kann,
- Kulturen korrekt ablesen und mehrere Keime erfassen kann,
- den Befund validieren kann,
- jederzeit versteht, was als nächstes zu tun ist.

### Wie bewerten wir den Test?

Der Test wird anhand des Test-Rasters ausgewertet:

- **Was war gut?** Welche Funktionen wurden verstanden und ohne Probleme genutzt?
- **Was war schlecht?** Wo war die Bedienung unklar, fehleranfällig oder technisch unsauber?
- **Neue Ideen?** Welche Anpassungen könnten die Bedienung verbessern?
- **Neue Probleme?** Welche zusätzlichen Risiken oder Herausforderungen wurden sichtbar?

### Was ist ein Erfolg?

Der Test ist erfolgreich, wenn die Testperson den Kernprozess ohne Anleitung versteht und die wichtigsten Funktionen selbstständig bedienen kann.

Ein besonders wichtiger Erfolgsfaktor ist, dass die Seite «Kulturen ablesen» verständlich ist, weil dort fachlich relevante Daten erfasst werden. Wenn die Testperson dort nicht versteht, wie mehrere Keime erfasst oder gespeichert werden, ist die App an einer zentralen Stelle noch nicht ausreichend selbsterklärend.

---

## Durchführung des Nutzertests

Der Nutzertest wurde mit Schaufi als Testperson durchgeführt. Schaufi hat noch nie in einem Labor gearbeitet und hört diese Begriffe zum ersten Mal. Die Testperson sollte die App möglichst selbstständig bedienen. Der Prototyp beziehungsweise die App wurde nicht im Detail erklärt, damit sichtbar wird, ob die Bedienung aus sich selbst heraus verständlich ist.

Getestet wurden folgende Bereiche:

1. Registrierung
2. Login
3. Dashboard
4. Patient erfassen
5. Patientenübersicht
6. Patientendetail
7. Material erfassen
8. Kulturen ablesen
9. Validieren

Während des Tests wurden Beobachtungen direkt notiert. Besonders beachtet wurde, ob die Testperson ohne Rückfragen weiterkommt, ob die Navigation nachvollziehbar ist und ob Bedienelemente klar erkennbar sind.

---

## Bewertungskriterien und Testergebnisse

### 1. Ist Registrierung und Login verständlich?

**Teilweise.** Der Login funktionierte grundsätzlich gut. Die Testperson konnte sich einloggen und wurde dabei nicht blockiert.

Bei der Registrierung gab es jedoch zwei Probleme:

- Die Tab-Reihenfolge springt nicht in der erwarteten Reihenfolge durch die Felder.
- Wenn das Passwort nicht korrekt wiederholt wird, erscheint eine unklare Fehlermeldung.

**Bewertung:**
Die Grundfunktion funktioniert, aber die Registrierung wirkt noch nicht sauber genug. Gerade bei Formularen ist eine logische Tab-Reihenfolge wichtig, weil sie Orientierung gibt und die Bedienung mit Tastatur ermöglicht.

---

### 2. Ist das Dashboard verständlich?

**Teilweise.** Das Zurücksetzen des Passworts funktionierte gut. Auch hier fiel jedoch auf, dass die Tab-Reihenfolge in einer seltsamen Reihenfolge springt.

**Bewertung:**
Das Dashboard erfüllt seine Grundfunktion, aber die Tab-Reihenfolge müsste noch angepasst werden.

---

### 3. Funktioniert der Ablauf rund um Patient:innen?

**Grösstenteils ja.** Die Testperson konnte mit der Patientenübersicht und dem Patientendetail arbeiten.

Positiv war:

- Die Testperson konnte über die Patientenübersicht auf «Detail» klicken.
- Die Suchfunktion nach Namen funktionierte.
- Die Bearbeitungsfunktion wurde gefunden und genutzt.
- Nach dem Bearbeiten konnte gespeichert werden.

Es gab aber auch eine Unklarheit: Nach dem Erfassen eines neuen Patienten erwartete die Testperson, direkt zum Patientendetail weitergeleitet zu werden. Stattdessen blieb sie auf der Seite «Patient erfassen».

Zusätzlich wurde sichtbar, dass die Testperson den direkten Weg von "Patienten erfassen" zu "Material erfassen" nicht erkannt hat. Sie ging stattdessen über das Dashboard, obwohl ein direkter Einstieg möglich gewesen wäre.

Auch wirkte die Rückkehr zum Patientendetail nach dem Speichern etwas ruckelig.

**Bewertung:**
Der Patientenbereich ist grundsätzlich verständlich. Der Ablauf nach dem Erfassen sollte aber klarer sein. Entweder sollte die App direkt zum Patientendetail weiterleiten oder sehr deutlich anzeigen, dass die Erfassung abgeschlossen ist und was als nächstes möglich ist.

---

### 4. Ist die Materialerfassung verständlich?

**Ja.** Die Testperson konnte alle Daten erfassen, ohne Fragen zu stellen.

**Bewertung:**
Die Seite «Material erfassen» ist aktuell einer der stärkeren Bereiche der App. Die Bedienung scheint klar und ausreichend selbsterklärend zu sein.

---

### 5. Ist «Kulturen ablesen» selbsterklärend?

**Nein.** Diese Seite war im Test das grösste Problem.

Beobachtete Schwierigkeiten:

- Die Seite war nicht selbsterklärend.
- Die Testperson konnte den ersten Keim erfassen.
- Als sie einen zweiten Keim erfassen wollte, bearbeitete sie versehentlich nur den ersten Keim.
- Es war unklar, ob das Speichern der Kulturdaten nötig ist.
- Die Buttons unten waren visuell nicht klar getrennt.
- Die Testperson empfand die Seite als unübersichtlich und fand sich nicht zurecht.

**Bewertung:**
Die Seite «Kulturen ablesen» muss überarbeitet werden. Das Problem ist nicht nur optisch, sondern betrifft die fachliche Bedienlogik. Wenn Nutzer:innen nicht klar erkennen, ob sie einen bestehenden Keim bearbeiten oder einen neuen Keim hinzufügen, kann es zu falschen oder unvollständigen Daten kommen.

---

### 6. Ist die Validierung des Befunds verständlich und korrekt dargestellt?

**Teilweise.** Die Validierung wurde erreicht, aber beim Befund war der obere Rand abgeschnitten.

**Bewertung:**
Das ist ein Layoutproblem, kann aber fachlich relevant werden, wenn dadurch Informationen schlecht lesbar sind oder der Befund unprofessionell wirkt.

---

### 7. Gibt es technische oder gestalterische Hürden?

**Ja.** Mehrere Beobachtungen zeigen technische oder gestalterische Schwächen:

- unlogische Tab-Reihenfolge bei Registrierung und Dashboard,
- unklare Fehlermeldung bei falscher Passwort-Wiederholung,
- unklare Weiterleitung nach Patientenerfassung,
- nicht erkennbare Direktnavigation zu «Material erfassen»,
- unübersichtliche Seite «Kulturen ablesen»,
- unklare Speicherlogik,
- visuell zu wenig getrennte Buttons,
- abgeschnittener Befundbereich.

**Bewertung:**
Die App funktioniert in mehreren Bereichen, ist aber noch nicht durchgehend selbsterklärend. Besonders die kritischen Laborfunktionen brauchen mehr Klarheit.

---

## Test-Raster

### Was war gut?

- Der Login funktionierte grundsätzlich.
- Das Zurücksetzen des Passworts über das Dashboard funktionierte gut.
- Die Patientenübersicht konnte genutzt werden.
- Die Suche nach Namen funktionierte.
- Das Patientendetail wurde gefunden.
- Patientendaten konnten bearbeitet und gespeichert werden.
- Die Materialerfassung wurde ohne Rückfragen ausgefüllt.
- Die Testperson konnte den ersten Keim bei «Kulturen ablesen» erfassen.

### Was war schlecht?

- Die Tab-Reihenfolge ist bei Registrierung und Dashboard unlogisch.
- Die Fehlermeldung bei nicht übereinstimmender Passwort-Wiederholung ist schlecht verständlich.
- Nach dem Erfassen eines Patienten bleibt man auf der Erfassungsseite, obwohl die Testperson das Patientendetail erwartete.
- Die direkte Navigation zu «Material erfassen» wurde nicht erkannt.
- Die Rückkehr zum Patientendetail nach dem Speichern wirkte ruckelig.
- «Kulturen ablesen» war nicht selbsterklärend.
- Beim Versuch, einen zweiten Keim zu erfassen, wurde nur der erste Keim bearbeitet.
- Die Speicherlogik bei Kulturdaten war unklar.
- Die Buttons unten bei «Kulturen ablesen» waren visuell nicht klar getrennt.
- Die Seite «Kulturen ablesen» wurde als unübersichtlich wahrgenommen.
- Beim Validieren war der obere Rand des Befunds abgeschnitten.

### Neue Ideen?

- Nach der Patientenerfassung direkt zum Patientendetail weiterleiten.
- Alternativ nach der Patientenerfassung eine klare Erfolgsmeldung anzeigen, zum Beispiel mit den Optionen «Zum Patientendetail», «Weiteres Material erfassen» oder «Neuen Patienten erfassen».
- Die Direktnavigation zu «Material erfassen» auf dem Dashboard sichtbarer machen.
- Die Tab-Reihenfolge in allen Formularen korrigieren.
- Fehlermeldungen verständlicher formulieren, insbesondere bei der Passwort-Wiederholung.
- Die Seite «Kulturen ablesen» stärker führen, zum Beispiel mit klaren Schritten.
- «Neuen Keim hinzufügen» klar von «Keim bearbeiten» trennen.
- Nach dem Speichern von Kulturdaten eine klare Bestätigung anzeigen.
- Buttons auf der Seite «Kulturen ablesen» optisch deutlicher trennen und eindeutiger beschriften.
- Den Befundbereich beim Validieren so anpassen, dass nichts abgeschnitten wird.

### Neue Probleme?

- Die Seite «Kulturen ablesen» ist nicht nur ein Darstellungsproblem, sondern ein Risiko für falsche Datenerfassung.
- Wenn das Erfassen eines zweiten Keims missverstanden wird, können Laborresultate unvollständig oder falsch dokumentiert werden.
- Die unklare Speicherlogik kann dazu führen, dass Nutzer:innen nicht wissen, ob ihre Eingaben übernommen wurden.
- Die unlogische Tab-Reihenfolge kann für Nutzer:innen problematisch sein, die stark mit Tastatur arbeiten.
- Wenn die wichtigsten Wege auf dem Dashboard nicht erkannt werden, ist die App zwar funktional vorhanden, aber im Arbeitsalltag weniger effizient.

---

## Fazit

Der Nutzertest zeigt, dass die App in mehreren Grundfunktionen bereits verständlich ist. Login, Passwort zurücksetzen, Patientensuche, Patientendetail, Bearbeiten und Materialerfassung funktionieren grundsätzlich gut.

Die App ist aber noch nicht vollständig selbsterklärend. Das grösste Problem ist die Seite «Kulturen ablesen». Dort war für die Testperson unklar, wie mehrere Keime korrekt erfasst werden, ob Kulturdaten gespeichert werden müssen und welche Buttons wofür zuständig sind.

Damit erfüllt die App das Ziel des Nutzertests nur teilweise. Die Basis funktioniert, aber für einen sicheren und intuitiven Laborprozess muss vor allem «Kulturen ablesen» klarer, geführter und visuell besser strukturiert werden.
