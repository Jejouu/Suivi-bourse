import streamlit as st
import pandas as pd

st.title("Mon Suivi Boursier")

# Remplace ton lien ci-dessous par ton vrai lien Google Sheet partagé
sheet_url = "https://docs.google.com/spreadsheets/d/1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc/edit?usp=sharing"

# Cette ligne transforme automatiquement ton lien de partage Google Sheets en lien de téléchargement CSV direct
if "/edit" in sheet_url:
    url_csv = sheet_url.split("/edit")[0] + "/export?format=csv"
else:
    url_csv = sheet_url

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(url_csv)
    st.success("Données chargées avec succès !")
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
