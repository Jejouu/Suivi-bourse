import streamlit as st
import pandas as pd

st.title("📈 Mon Suivi Boursier")

# Lien vers ton Google Sheet brut (format CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc/edit?usp=sharing"
url_csv = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

# Fonction pour charger les données (avec mise en cache)
@st.cache_data(ttl=600)
def load_data(url):
    return pd.read_csv(url)

# --- BOUTON D'ACTUALISATION ---
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🔄 Actualiser"):
        # Efface le cache pour forcer le rechargement immédiat
        st.cache_data.clear()
        st.success("Données rechargées !")

try:
    # Chargement des données
    df = load_data(url_csv)
    
    # Affichage de ton tableau ou de tes indicateurs
    st.dataframe(df)
    
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
