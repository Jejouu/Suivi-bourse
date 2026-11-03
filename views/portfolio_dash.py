import pandas as pd
import numpy as np
from Utils.loader import clean_financial_column

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

def get_sharpe_ratio(df_hist: pd.DataFrame, risk_free_rate: float = 0.03) -> float:
    """
    Calcule le Ratio de Sharpe du portefeuille à partir de l'historique des rendements.
    """
    if df_hist.empty:
        return 0.0
    # Logique de calcul basée sur les rendements journaliers/mensuels
    # rendements = df_hist['Valeur'].pct_change().dropna()
    # excess_returns = rendements - (risk_free_rate / 252)
    # return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    return 0.0

def get_sortino_ratio(df_hist: pd.DataFrame, risk_free_rate: float = 0.03) -> float:
    """
    Calcule le Ratio de Sortino (ne prend en compte que la volatilité négative).
    """
    if df_hist.empty:
        return 0.0
    # rendements = df_hist['Valeur'].pct_change().dropna()
    # negative_returns = rendements[rendements < 0]
    # downside_std = negative_returns.std() * np.sqrt(252)
    # return (rendements.mean() * 252 - risk_free_rate) / downside_std if downside_std != 0 else 0.0
    return 0.0

def get_beta(df_hist: pd.DataFrame, df_benchmark: pd.DataFrame) -> float:
    """Calcule le Béta par rapport à un indice de référence (ex: S&P 500 / MSCI World)."""
    if df_hist.empty or df_benchmark.empty:
        return 0.0
    # Covariance(Portefeuille, Indice) / Variance(Indice)
    return 1.0


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
