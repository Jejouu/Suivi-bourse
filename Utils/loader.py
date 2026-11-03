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

def clean_financial_column(series):
    """Nettoie une colonne financière (supprime €, espaces, gère les virgules) et la convertit en numérique."""
    if series is None:
        return series
    
    valeurs_nettoyees = (
        series.astype(str)
        .str.replace('€', '', regex=False)
        .str.replace(' ', '', regex=False)
        .str.replace('\xa0', '', regex=False)  # Espace insécable standard
        .str.replace('\u202f', '', regex=False) # Espace fin insécable
        .str.replace(',', '.', regex=False)
    )
    return pd.to_numeric(valeurs_nettoyees, errors='coerce')

def get_cell_value(sheet_name: str, cell_coordinates: str):
    """Récupère la valeur brute d'une cellule spécifique dans un onglet donné."""
    try:
        # Assure-toi que cette fonction s'adapte à ton client gspread existant
        sheet = client.open(SPREADSHEET_NAME).worksheet(sheet_name)
        val = sheet.acell(cell_coordinates).value
        return val
    except Exception:
        return None
