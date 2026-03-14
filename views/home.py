import streamlit as st

st.title("Rechner Resistenzmonitoring")

st.markdown("""
Diese App berechnet die Antibiotika-Resistenzrate ausgewählter bakterieller Erreger anhand der Anzahl getesteter und resistenter Isolate einer Asuwertungsperiode (bspw. April 2023). 

Die Resistenzrate wird in Prozent dargestellt und mit einem einfachen Ampelsystem bewertet. 
             
Zusätzlich werden bei bestimmten Kombinationen von Erreger und Antibiotikaklasse Hinweise zu möglichen multiresistenten Erregern angezeigt. 
Es können mehrere Auswertungen durchgeführt und in einer Tabelle gespeichert werden, um Trends über die Zeit zu verfolgen mittels eines Liniendiagramms.

Bitte beachte, dass die Visuelle Darstellung immer mit neuem Datum gefüttert werden muss, damit der Verlauf angezeigt wird. ein mehrfaches Klicken auf Berechnen ohne Änderung der Daten zeigt keine Veränderung der Werte an, da die Daten nicht verändert wurden.

Es wurde ein Passwort vergessen hinzufügt falls der Nutzer sein Passwort vergessen hat. Es wird ein neues zufälliges Passwort erzeugt, welches der Nutzter direkt nach erneutem Einloggen geändert werden sollte. Es wird empfohlen, das neue Passwort sicher zu speichern, da es nicht erneut angezeigt wird.
""")

st.markdown("""
Diese App wurde von folgender Person entwickelt:
- Kevin Engehausen (engehkev@students.zhaw.ch) 


Autor: Samuel Wehrli (wehs@zhaw.ch)
""")
