import streamlit as st
import pandas as pd

st.title("📈 Mon Suivi Boursier - Holding")

# Remplace par l'ID de ton fichier et le gid spécifique de l'onglet "holding"
url_csv = "https://docs.google.com/spreadsheets/d/1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc/edit?usp=sharing/edit?gid=575574311#gid=575574311"

@st.cache_data(ttl=600)
def load_data(url):
    # on_bad_lines='skip' permet d'ignorer les lignes qui n'ont pas le bon nombre de colonnes
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(url_csv)
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur de chargement de l'onglet holding : {e}")
