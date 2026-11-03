import streamlit as st
import pandas as pd
import gspread

st.title("📈 Mon Suivi Boursier - Holding")

# Remplace par ton lien complet de Google Sheet (partagé en lecture publique)
SHEET_URL = "TON_LIEN_COMPLET_DU_GOOGLE_SHEET"

@st.cache_data(ttl=600)
def load_holding_data():
    # gspread est bien importé globalement, il est accessible ici
    gc = gspread.anonymous()
    sh = gc.open_by_url(SHEET_URL)
    
    # Cible explicitement l'onglet "holding"
    worksheet = sh.worksheet("holding")
    
    # Récupération des données
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

try:
    df = load_holding_data()
    st.success("Onglet 'holding' chargé avec succès !")
    st.dataframe(df)
except Exception as e:
    st.error(f"Erreur lors de la récupération de l'onglet holding : {e}")
