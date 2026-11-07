import pandas as pd
import plotly.express as px
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
    # Choix du dégradé selon le type de ratio
    if ratio_type == "sharpe":
        gradient = "linear-gradient(to right, #ff4b4b, #ff4b4b,#ffa500, #ffeb3b, #00FF7F, #00FF7F)"
    elif ratio_type == "sortino":
        gradient = "linear-gradient(to right, #ff4b4b, #ffa500, #ffeb3b, #00FF7F, #00FF7F, #00FF7F)"
    else:  # Bêta (Bleu -> Orange -> Jaune -> Vert -> Orange -> Rouge)
        gradient = "linear-gradient(to right, #00bfff, #00bfff,#ffa500, #ffeb3b, #00FF7F, #ffa500, #ff4b4b)"
        
    st.markdown(f"""
        <div style="font-size: 20px; color: rgb(163, 168, 184); margin-bottom: 4px;">
            <b>{label}</b> : <span style="color: #FFFFFF;">{value:.2f}</span>
        </div>
        <div style="position: relative; width: 100%; height: 10px; background: {gradient}; border-radius: 5px; margin-bottom: 4px;">
            <div style="position: absolute; top: -5px; left: calc({percent}% - 8px); width: 18px; height: 18px; background-color: #f0f2f6; border: 2px solid #31333F; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 14px; color: rgb(128, 128, 128);">
            <span>{min_val}</span>
            <span>{max_val}</span>
        </div>
    """, unsafe_allow_html=True)

def metric_colored(label, value_str, val_numeric):
    color = "#00FF7F" if val_numeric >= 0 else "#FF4B4B"
    st.markdown(f"""
        <div style="font-size: 14px; color: #FFFFFF; font-weight: 500; margin-bottom: 2px;">{label}</div>
        <div style="font-size: 2.25rem; font-weight: 600; color: {color};">{value_str}</div>
    """, unsafe_allow_html=True)

def tracer_graphique_pv(df_pv_jour, config):
    """
    Génère et affiche le graphique de P&L journalier selon la configuration fournie.
    """
    if df_pv_jour.empty:
        st.warning("Aucune donnée valide trouvée dans la colonne J.")
        return

    # Formatage du texte affiché au-dessus des barres
    df_pv_jour["Texte_Affiche"] = df_pv_jour["PV_Jour"].apply(lambda x: f"{x:,.2f} €")
    
    # Mise en gras des tickers pour l'axe X
    df_pv_jour["Actif_Gras"] = df_pv_jour["Actif"].apply(lambda x: f"<b>{x}</b>")
    
    # Application des couleurs dynamiques selon la configuration
    df_pv_jour["Couleur"] = df_pv_jour["PV_Jour"].apply(
        lambda x: config["couleur_positif"] if x > 0 else (config["couleur_negatif"] if x < 0 else config["couleur_neutre"])
    )
    
    # Création de la figure Plotly
    fig_pv = px.bar(
        df_pv_jour,
        x="Actif_Gras",
        y="PV_Jour",
        title=""
    )
    
    # Application des paramètres visuels des barres
    fig_pv.update_traces(
        marker_color=df_pv_jour["Couleur"],
        width=config["largeur_barre"],
    )
    
    # Application de la mise en page (Layout)
    fig_pv.update_layout(
        title=dict(
            text=config["titre"], 
            font=dict(size=18, color="white"),
            x=0.5,              # Positionne le titre au milieu (0.5)
            xanchor='center'    # Ancre le centre du texte sur cette position
        ),
        margin=dict(t=config["marge_haut"], b=config["marge_bas"], l=10, r=10),
        xaxis_title="",
        xaxis=dict(
            tickfont=dict(color=config["couleur_ticker"], size=config["taille_police_ticker"]),
            showgrid=False,
        ),
        yaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=config.get("hauteur")
    )
    
    st.plotly_chart(fig_pv, width="stretch")

def tracer_graphique_latente(df_latente, config):
    """
    Génère et affiche le graphique horizontal des plus-values latentes.
    """
    if df_latente.empty:
        st.warning("Aucune donnée valide trouvée pour la plus-value latente.")
        return

    # Formatage du texte affiché au bout des barres (ex: +35,06 €)
    df_latente["Texte_Affiche"] = df_latente["PV_Latente"].apply(lambda x: f"{x:+,.2f} €")
    
    # Mise en gras des tickers pour l'axe Y
    df_latente["Actif_Gras"] = df_latente["Actif"].apply(lambda x: f"<b>{x}</b>")
    
    # Application des couleurs dynamiques (Vert > 0, Rouge < 0)
    df_latente["Couleur"] = df_latente["PV_Latente"].apply(
        lambda x: config["couleur_positif"] if x > 0 else (config["couleur_negatif"] if x < 0 else config["couleur_neutre"])
    )
    
    # Création du graphique à barres horizontales
    fig_latente = px.bar(
        df_latente,
        x="PV_Latente",
        y="Actif_Gras",
        orientation="h",
        text="Texte_Affiche",
        title=""
    )
    
    # Paramétrage des barres et du texte à l'extérieur
    fig_latente.update_traces(
        marker_color=df_latente["Couleur"],
        textfont=dict(size=config["taille_police_texte"], color="white"),
        textposition="outside",  # Place le texte au bout de la barre
        width=config["largeur_barre"],
        cliponaxis=False
    )
    
    # Mise en page (Layout)
    fig_latente.update_layout(
        height=config.get("hauteur"),
        bargap=config.get("bargap", 0.2),
        title=dict(
            text=config["titre"], 
            font=dict(size=18, color="white"),
            x=0.5,              # Positionne le titre au milieu (0.5)
            xanchor='center'    # Ancre le centre du texte sur cette position
        ),
        margin=dict(t=config["marge_haut"], b=config["marge_bas"], l=config["marge_gauche"], r=config["marge_droite"]),
        xaxis_title="",
        yaxis_title="",
        yaxis=dict(
            tickfont=dict(color=config["couleur_ticker"], size=config["taille_police_ticker"]),
            showgrid=False,
            autorange="reversed"  # Pour afficher le premier actif en haut
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=True,
            zerolinecolor="rgba(255, 255, 255, 0.3)"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    
    st.plotly_chart(fig_latente, width="stretch")

def tracer_graphique_pie(df_pie, config):
    """
    Génère et affiche le diagramme circulaire du portefeuille.
    """
    if df_pie.empty:
        st.warning("Aucune donnée numérique valide trouvée pour afficher le camembert.")
        return
        
    fig = px.pie(
        df_pie, 
        names="Actif", 
        values="Valeur", 
        hole=config["trou"], 
        title=""
    )
    
    # Application des couleurs personnalisées et du texte
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(colors=config["couleurs"])
    )
    
    # Mise en page transparente et adaptée au mode sombre
    fig.update_layout(
        height=config.get("hauteur"),
        width=config.get("largeur"),
        title=dict(
            text=config["titre"], 
            font=dict(size=18, color="white"),
            x=0.5,              # Positionne le titre au milieu (0.5)
            xanchor='center'    # Ancre le centre du texte sur cette position
        ),
        margin=dict(
            t=config["marge_haut"], 
            b=config["marge_bas"], 
            l=config["marge_gauche"], 
            r=config["marge_droite"]
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False
    )
    
    st.plotly_chart(fig, width="stretch")
