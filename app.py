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
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(url_csv)
    st.success("Onglet 'holding' chargé avec succès !")

    if df.shape[1] > 7:
        # Récupération de la colonne H (index 7)
        col_brute = df.iloc[:, 7]
        
        # Nettoyage rigoureux : suppression de '€', des espaces normaux/insécables, et remplacement de la virgule par un point
        col_nettoyee = (
            col_brute.astype(str)
            .str.replace("€", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace("\xa0", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        
        # Conversion en nombres (l'en-tête texte et les cellules vides deviennent NaN)
        colonne_h = pd.to_numeric(col_nettoyee, errors='coerce')
        total_h = colonne_h.sum()

        # Affichage du total propre
        st.metric(label="Total Holding (Colonne H)", value=f"{total_h:,.2f} €")
    else:
        st.warning("La colonne H n'a pas été trouvée dans le fichier d'origine.")

    # Affichage du tableau complet
    st.dataframe(df)

except Exception as e:
    st.error(f"Erreur de chargement : {e}")

except Exception as e:
    st.error(f"Erreur de chargement : {e}")
