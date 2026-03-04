import streamlit as st
from functions.addition import add

st.title("Addition Calculator")

st.write("hier kannst du zwei Zahlen addieren")

with st.form("addition_form"):
    num1 = st.number_input("num1")
    num2 = st.number_input("num2")
    submit_button = st.form_submit_button("Addieren")

if submit_button:
    result = add(num1, num2)
    st.write("Das Ergebnis ist:", result)


st.title("Unterseite A")

st.write("Diese Seite ist eine Unterseite der Startseite.")
