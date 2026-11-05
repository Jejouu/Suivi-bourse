import pandas as pd
import numpy as np
import streamlit as st
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

def get_sharpe_ratio() -> str:
    try:
        val = get_cell_value("Valeurs", "B4")
        return str(val) if val is not None else "N/A"
    except Exception:
        return "N/A"

def get_sortino_ratio() -> float:
    """Récupère le ratio de Sortino (B5) depuis l'onglet 'Valeurs'."""
    try:
        df = load_sheet_data("Valeurs")
        val = df.iloc[4, 1]  # Ligne 5, Colonne B
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, str):
            val = val.replace(",", ".").strip()
        return float(val)
    except Exception:
        return 0.0

def get_beta() -> float:
    """Récupère le Béta (B6) depuis l'onglet 'Valeurs'."""
    try:
        df = load_sheet_data("Valeurs")
        val = df.iloc[5, 1]  # Ligne 6, Colonne B
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, str):
            val = val.replace(",", ".").strip()
        return float(val)
    except Exception:
        return 0.0

def render_ratio_slider(label, value, min_val=-1.0, max_val=3.0, ratio_type="sharpe"):
    """Affiche un ratio avec sa jauge personnalisée sans texte d'appréciation."""
    percent = max(0.0, min(100.0, ((value - min_val) / (max_val - min_val)) * 100))
    
    # Choix du dégradé selon le type de ratio
    if ratio_type in ["sharpe", "sortino"]:
        gradient = "linear-gradient(to right, #ff4b4b, #ffa500, #ffeb3b, #00FF7F, #00FF7F, #00FF7F)"
    else:  # Bêta (Bleu -> Orange -> Jaune -> Vert -> Orange -> Rouge)
        gradient = "linear-gradient(to right, #00bfff, #ffa500, #ffeb3b,#00FF7F, #ffa500, #ff4b4b)"

    st.markdown(f"""
        <div style="font-size: 20px; color: rgb(163, 168, 184); margin-bottom: 4px;">
            <b>{label}</b> : <span style="color: #FFFFFF;">{value:.2f}</span>
        </div>
        <div style="position: relative; width: 100%; height: 10px; background: {gradient}; border-radius: 5px; margin-bottom: 4px;">
            <div style="position: absolute; top: -5px; left: calc({percent}% - 8px); width: 18px; height: 18px; background-color: #f0f2f6; border: 2px solid #31333F; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: rgb(128, 128, 128);">
            <span>{min_val}</span>
            <span>{max_val}</span>
        </div>
    """, unsafe_allow_html=True)
