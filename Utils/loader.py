import requests
import streamlit as st
import pandas as pd

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwzF5FIEhFyefDF1cfvRLhUpyNyRzcUTbogVZZDvHxxuA-LSy0Dd4UQAdvTH4jsspiU/exec"

ONGLETS_NAMES = {
    "valeurs": "Valeurs",
    "donnees": "Donnees",
    "holding": "Holding",
    "transaction": "Transaction",
    "histporte": "Histporte"
}

@st.cache_data(ttl=600)
def load_sheet_data(onglet_name: str, update_counter: int = 0) -> pd.DataFrame:
    """
    Charge chaque onglet Google Sheet selon sa structure spécifique :
    - 'donnees' et 'valeurs' : matrice brute avec la 1ère ligne en en-tête pour préserver les indexations (iloc).
    - 'holding', 'transaction', 'histporte' : tableaux structurés avec noms de colonnes et nettoyage des lignes vides.
    """
    key = onglet_name.lower()
    nom_exact_onglet = ONGLETS_NAMES.get(key)
    if not nom_exact_onglet:
        raise ValueError(f"L'onglet '{onglet_name}' n'est pas répertorié dans ONGLETS_NAMES.")
    
    url = f"{WEB_APP_URL}?sheet={nom_exact_onglet}"
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    if not data:
        return pd.DataFrame()
        
    # 1. Onglets à structure matricielle ou clé/valeur sans en-tête standard
    # On reproduit exactement pd.read_csv() : ligne 0 en colonnes, ligne 1 en index 0
    if key in ["donnees", "valeurs"]:
        if len(data) <= 1:
            return pd.DataFrame(data)
        return pd.DataFrame(data[1:], columns=data[0])
    
    # 2. Onglets tabulaires classiques (Holding, Transaction, Histporte)
    if len(data) <= 1:
        return pd.DataFrame()
        
    df = pd.DataFrame(data[1:], columns=data[0])
    
    # Supprime les lignes entièrement vides (notamment les 990 lignes vides de l'onglet Transaction)
    df = df.replace("", pd.NA).dropna(how="all").fillna("")
    
    return df
    
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
    """
    Récupère la valeur brute d'une cellule spécifique (ex: 'B4') 
    dans un onglet donné via l'export CSV et le DataFrame pandas.
    """
    try:
        # 1. Chargement du DataFrame de l'onglet demandé via son nom (dans GIDS)
        df = load_sheet_data(sheet_name)
        if df.empty:
            return None

        # 2. Séparation de la lettre de colonne et du numéro de ligne (ex: 'B4' -> col 'B', row 4)
        import re
        match = re.match(r"([A-Za-z]+)([0-9]+)", cell_coordinates)
        if not match:
            return None
        
        col_letter, row_num = match.groups()
        
        # 3. Conversion de la lettre de colonne en index (A=0, B=1, C=2...)
        col_idx = 0
        for char in col_letter.upper():
            col_idx = col_idx * 26 + (ord(char) - ord('A'))
            
        # 4. Conversion de la ligne Excel/Sheet en index pandas (Ligne 4 Excel = index 2 en DataFrame CSV sans entête)
        # Remarque : La première ligne du CSV devient l'en-tête (header), donc la ligne Excel B4 correspond à l'index df.iloc[2, 1]
        row_idx = int(row_num) - 2 

        if row_idx < 0 or row_idx >= len(df) or col_idx >= df.shape[1]:
            return None

        val = df.iloc[row_idx, col_idx]
        return val
    except Exception:
        return None

def clean_str_to_float(val) -> float:
    """Convertit proprement une chaîne ou un nombre en float en gérant les virgules et les espaces."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    
    try:
        # Nettoyage : conversion en string, suppression des espaces, remplacement de la virgule par un point
        val_str = str(val).replace("\u202f", "").replace(" ", "").replace(",", ".").strip()
        if val_str == "" or val_str.lower() == "nan":
            return 0.0
        return float(val_str)
    except Exception:
        return 0.0
