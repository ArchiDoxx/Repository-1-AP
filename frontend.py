# streamlit installieren
# streamlit app "Hello World" erstellen und testen
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

from ast import Name

import requests
import streamlit as st

URL = "https://naas.isalman.dev/no"                         # Initiativ den API Endpoint angeben 
def request_no():                                           # request_no sendet get Anfrage mit requests.get(URL) an die URL  
    response = requests.get(URL)                            # und bekommt eine response zurück         
    response_json = response.json()                         # response.json() konvertiert die response in ein JSON-Format,
    return response_json["reason"]                          # Die Funktion gibt anschließend response_json["reason"] zurück.
 
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


# Bau eiens Textfeldes, man kann Namen eingeben und er wird dann angezeigt. 
# st.text_input() benötigt ein Label, das über dem Textfeld angezeigt wird (hier der Wert in der Klammer) 
# ohne das "Name" in der Klammer würde es nur Error ausgeben.


name = st.text_input("Name")
st.write(name)