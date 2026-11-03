import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
import gspread

st.title("📈 Mon Suivi Boursier - Holding")

# 1. Connexion au Google Sheet (en utilisant les secrets Streamlit pour la sécurité)
# Si ton fichier est totalement public en lecture, gspread peut parfois s'y connecter via l'URL :
SHEET_URL = "https://docs.google.com/spreadsheets/d/1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc/edit?usp=sharing"

@st.cache_data(ttl=600)
def load_holding_data():
    gc = gspread.oauth() # Ou via les credentials de service
    # Alternative simple sans clé de service si le fichier a le partage "Tous les disposant du lien peuvent lire" :
    import gspread
    gc = gspread.anonymous()
    sh = gc.open_by_url(SHEET_URL)
    
    # Cible explicitement l'onglet "holding" par son nom exact
    worksheet = sh.worksheet("holding")
    
    # Convertit les données de l'onglet en DataFrame Pandas
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

try:
    df = load_holding_data()
    st.success("Onglet 'holding' chargé avec succès !")
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération de l'onglet holding : {e}")
