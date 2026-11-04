import pandas as pd
import numpy as np
from Utils.loader import clean_financial_column, get_cell_value, load_sheet_data

def get_total_portfolio_value(df_holding: pd.DataFrame) -> float:
    """Retourne la valeur totale du portefeuille."""
    if df_holding.empty or df_holding.shape[1] <= 4:
        return 0.0
    valeurs = clean_financial_column(df_holding.iloc[:, 4])
    return float(valeurs.sum())

def get_net_pnl(df_holding: pd.DataFrame) -> float:
    """Calcule la plus-value nette globale : """
    if df_holding.empty or df_holding.shape[1] <= 6:
        return 0.0
    
    valeur_actuelle = clean_financial_column(df_holding.iloc[:, 4]).sum()
    investissement_total = clean_financial_column(df_holding.iloc[:, 6]).sum()
    
    return float(valeur_actuelle - investissement_total)

def get_unrealized_pnl(df_holding: pd.DataFrame) -> float:
    """Retourne la plus-value latente totale (Colonne H / Index 7)."""
    if df_holding.empty or df_holding.shape[1] <= 7:
        return 0.0
    plus_values = clean_financial_column(df_holding.iloc[:, 7])
    return float(plus_values.sum())

def get_sharpe_ratio() -> float:
    """Récupère le ratio de Sharpe depuis l'onglet 'Valeurs', cellule B4."""
    try:
        cleaned = clean_financial_column(pd.Series([val])).iloc[0]
        val = get_cell_value("Valeurs", "B4")
        return float(cleaned)
    except Exception:
        return 0.0

def get_sortino_ratio() -> float:
    """Récupère le ratio de Sortino depuis l'onglet 'Valeurs', cellule B5."""
    try:
        val = get_cell_value("Valeurs", "B5")
        cleaned = clean_financial_column(pd.Series([val])).iloc[0]
        return float(cleaned)
    except Exception:
        return 0.0

def get_beta() -> float:
    """Récupère le Béta depuis l'onglet 'Valeurs', cellule B6."""
    try:
        val = get_cell_value("Valeurs", "B6")
        cleaned = clean_financial_column(pd.Series([val])).iloc[0]
        return float(cleaned)
    except Exception:
        return 0.0

# ==========================================
# 📅 HISTORIQUE & ÉVOLUTION TEMPORELLE
# ==========================================

def get_portfolio_performance(df_hist: pd.DataFrame, period: str = "1M") -> pd.DataFrame:
    """
    Filtre l'historique du portefeuille selon la période souhaitée 
    ('1M', '3M', '6M', '1Y', 'ALL') pour alimenter le graphique dynamique.
    """
    if df_hist.empty or "Date" not in df_hist.columns:
        return df_hist
    
    df = df_hist.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    date_max = df['Date'].max()
    
    periods_map = {
        "1M": date_max - pd.DateOffset(months=1),
        "3M": date_max - pd.DateOffset(months=3),
        "6M": date_max - pd.DateOffset(months=6),
        "1Y": date_max - pd.DateOffset(years=1),
        "ALL": df['Date'].min()
    }
    
    start_date = periods_map.get(period, df['Date'].min())
    return df[df['Date'] >= start_date]
