import streamlit as st
import pandas as pd

st.title("Mon Suivi Boursier")

# Lien vers ton Google Sheet (assure-toi qu'il est partagé en lecture publique)
sheet_url = "https://docs.google.com/spreadsheets/d/1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc/edit?gid=0#gid=0"
url_csv = sheet_url.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(url_csv)
    st.success("Données chargées avec succès !")
    
    # Affiche un aperçu de tes données
    st.dataframe(df)
    
    # Exemple pour afficher une métrique (ex: ton ratio de Sharpe ou ton Bêta si tu as une colonne dédiée)
    # st.metric(label="Ratio de Sharpe", value="1.42")
    
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
