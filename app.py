import streamlit as st
import pandas as pd

st.title("📈 Mon Suivi Boursier - Holding")

# 1. ID de ton Google Sheet
SHEET_ID = "1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc"

# 2. GID de ton onglet "holding"
GID_HOLDING = "575574311"

# Construction de l'URL d'export CSV spécifique à cet onglet
url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_HOLDING}"

@st.cache_data(ttl=600)
def load_data(url):
    # Charge le CSV en ignorant d'éventuelles lignes mal formatées
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(url_csv)
    st.success("Onglet 'holding' chargé avec succès !")

    # --- Calcul du total de la colonne H ---
    # En Python (index 0) : A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7
    if df.shape[1] > 7:
        # iloc[:, 7] prend la 8ème colonne (H). 
        # pd.to_numeric avec errors='coerce' convertit l'en-tête/texte en NaN, 
        # ce qui permet de faire la somme uniquement sur les cellules numériques.
        colonne_h = pd.to_numeric(df.iloc[:, 7], errors='coerce')
        total_h = colonne_h.sum()

        # Affichage du KPI sous forme de carte/métrique
        st.metric(label="Total Holding (Colonne H)", value=f"{total_h:,.2f} €")
    else:
        st.warning("La colonne H n'a pas été trouvée dans le fichier d'origine.")

    # Affichage du tableau complet
    st.dataframe(df)

except Exception as e:
    st.error(f"Erreur de chargement : {e}")
