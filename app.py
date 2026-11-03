import streamlit as st
import pandas as pd

st.title("📈 Mon Suivi Boursier - Holding")

# 1. Mets ton ID de Google Sheet (la longue chaîne de caractères dans ton lien entre /d/ et /edit)
SHEET_ID = "1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc"

# 2. Mets le gid de ton onglet "holding" (visible dans l'URL de ton navigateur quand tu es sur l'onglet, ex: #gid=123456789)
GID_HOLDING = "575574311"

# Construction de l'URL d'export CSV spécifique à cet onglet
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_HOLDING}"

@st.cache_data(ttl=600)
def load_data(url):
    # on_bad_lines='skip' permet d'ignorer d'éventuelles lignes mal alignées dans le tableur
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(url_csv)
    st.success("Onglet 'holding' chargé avec succès !")
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
