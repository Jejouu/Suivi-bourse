import streamlit as st
import pandas as pd

# ID unique de ton Google Sheet
SHEET_ID = "1D4_pyAh-2wYrsjrqVJuF8K7Jn5FtC8hlnfJ6J3TSsSc"

# Dictionnaire centralisé des GIDs pour tes 5 onglets
GIDS = {
    "valeurs": "1782863735",
    "donnees": "0",
    "holding": "575574311",
    "transaction": "1217721347",
    "histporte": "773348969"
}

@st.cache_data(ttl=600)
def load_sheet_data(onglet_name: str) -> pd.DataFrame:
    """
    Charge un onglet Google Sheet au format CSV via son nom (clé du dictionnaire GIDS).
    Mise en cache Streamlit de 10 minutes et gestion des lignes mal formées.
    """
    gid = GIDS.get(onglet_name.lower())
    if not gid:
        raise ValueError(f"L'onglet '{onglet_name}' n'est pas répertorié dans les GIDs.")
    
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url, on_bad_lines='skip')

def clean_financial_column(series: pd.Series) -> pd.Series:
    """
    Nettoie une colonne de type monétaire ou numérique textuelle :
    - Supprime le symbole '€' et les espaces (normaux et insécables).
    - Remplace les virgules par des points pour la compatibilité décimale.
    - Convertit le tout en float/numérique (les en-têtes de colonnes deviennent NaN).
    """
    col_cleaned = (
        series.astype(str)
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(col_cleaned, errors='coerce')
