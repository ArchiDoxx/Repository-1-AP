# streamlit installieren
# streamlit app "HEllo World" erstellen und testen
# "say no" - app als ersten Teste rstellen
# API: https://github.com/hotheadhacker/no-as-a-service
# API Endpoint: https://naas.isalman.dev/no
# button in streamlit der bei klick eine anfrage an die API endpoint sendet und die Antwort anzeigt

# Todos am nachmittag:
# - Streamlit App mit 2 Funktionen von Notitzen API
# - Funktion 1: Alle Notitzen anzeigen (Liste von Notitzen mit Titel und Inhalt dynamisch anzeigen)
#   -> Liste von titeln von Notitzen anzeigen.
#   -> Möglichket zu einem Titel den INhalt, Tags, Kateegorie, etc anzuzeigen.
# - Funktion 2: Neue Notiz erstellen (Formular mit Titel, Inhalt, und Button)
#     -> Neu erstellte Notiz soll in der Liste der Notitzen angezeigt werden.

import requests
import streamlit as st

URL = "https://naas.isalman.dev/no"

def request_no():
    response = requests.get(URL)
    response_json = response.json()
    return response_json["reason"]

#Initialisierung
if "text1" not in st.session_state:
    st.session_state["text1"] = request_no()

if "text" not in st.session_state:
    st.session_state["text"] = request_no()


if st.button("Neuer Text 1"):
    st.session_state["text1"] = request_no()

st.write(st.session_state["text1"])
   

if st.button("Neuer Text"):
    st.session_state["text"] = request_no()

st.write(st.session_state["text"])

with st.expander("session state"):
    st.write(st.session_state)
