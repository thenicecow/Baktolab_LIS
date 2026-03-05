import streamlit as st

st.title("Rechner Resistenzmonitoring")

st.markdown("""
Diese App berechnet die Antibiotika-Resistenzrate ausgewählter bakterieller Erreger anhand der Anzahl getesteter und resistenter Isolate einer Asuwertungsperiode (bspw. April 2023).  
Die Resistenzrate wird in Prozent dargestellt und mit einem einfachen Ampelsystem bewertet.  
Zusätzlich werden bei bestimmten Kombinationen von Erreger und Antibiotikaklasse Hinweise zu möglichen multiresistenten Erregern angezeigt. 
Es können mehrere Auswertungen durchgeführt und in einer Tabelle gespeichert werden, um Trends über die Zeit zu verfolgen.
""")

st.markdown("""
Diese App wurde von folgenden Personen entwickelt:
- Kevin Engehausen (engehkev@students.zhaw.ch) 
- Melina Kraus (krausme1@students.zhaw.ch)


Autor: Samuel Wehrli (wehs@zhaw.ch)
""")
