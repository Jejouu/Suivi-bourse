import streamlit as st
import pandas as pd
from Utils.loader import (
    load_sheet_data,
    clean_financial_column,
    clean_str_to_float,
    get_cell_value
)
from views.portfolio_dash import (
    get_total_portfolio_value, 
    get_net_pnl,
    get_unrealized_pnl,
    get_sharpe_ratio,
    get_sortino_ratio,
    get_beta,
    render_ratio_slider,
    metric_colored,
    tracer_graphique_pv,
    tracer_graphique_latente,
    tracer_graphique_pie
)
from views.asset_detail import (
    get_asset_data,
    tracer_graphique_evolution
)

def check_password():
    """Vérifie si le code d'accès est correct."""
    # Tu peux changer le code ici ou le stocker dans st.secrets["PASSWORD"]
    CODE_SECRET = "1234"  

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    # Interface de saisie du code
    st.header("🔒 Accès restreint")
    password = st.text_input("Veuillez entrer le code d'accès :", type="password")
    
    if st.button("Valider"):
        if password == CODE_SECRET:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("Code incorrect.")
            
    return False

# --- APPLICATION PRINCIPALE ---
# Si le code n'est pas validé, on stoppe l'exécution de la suite de la page
if not check_password():
    st.stop()

# --- Configuration de la page ---
st.set_page_config(
    page_title="Mon Suivi Boursier",
    page_icon="📈",
    layout="wide"
)

# --- Navigation dans la barre latérale ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Choisir une vue :",
    ["📊 Dashboard Global", "📈 Vue Détaillée par Actif", "📝 Journal des Transactions"]
)

# --- Bouton global d'actualisation dans la sidebar ---
if st.sidebar.button("🔄 Actualiser les données"):
    st.cache_data.clear()
    st.rerun()

# --- Routage des pages avec isolation des erreurs ---
elif page == "📊 Dashboard Global":
    st.header("📊 Dashboard Global du Portefeuille")
    if st.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        st.rerun()
    try:
        # 1. Chargement des onglets nécessaires
        df_holding = load_sheet_data("holding")
        df_hist = load_sheet_data("histporte")
        
        st.success("Données du portefeuille chargées avec succès !")

        # 5. Affichage du tableau brut 'Holding' dans un expander
        with st.expander("Holding"):
            st.dataframe(df_holding)
        
        # 2. Récupération des valeurs via les fonctions modulaires
        total_valeur = get_total_portfolio_value(df_holding)

        total_col_g = clean_financial_column(df_holding.iloc[:, 6]).sum()
        
        plus_value_nette = get_net_pnl(df_holding)
        pourcentage_pnl = (plus_value_nette / total_col_g * 100) if total_col_g != 0 else 0.0
        
        plus_value_latente = get_unrealized_pnl(df_holding)
        pourcentage_lat = (plus_value_latente / total_col_g * 100) if total_col_g != 0 else 0.0
        
        sharpe = clean_str_to_float(get_cell_value("valeurs", "B4"))
        sortino = clean_str_to_float(get_cell_value("valeurs", "B5"))
        beta = clean_str_to_float(get_cell_value("valeurs", "B6"))
        
        # --- 1ère Ligne : Indicateurs Financiers ---
        st.subheader("💶 Valeur du portefeuille")
        col1, col2, col3 = st.columns(3)
        
        col1.markdown(f"""
            <div style="font-size: 16px; color: #FFFFFF; font-weight: 500; margin-bottom: 2px;">Valeur Totale</div>
            <div style="font-size: 3rem; font-weight: 600; color: #FFFFFF;">{total_valeur:,.2f} €</div>
        """, unsafe_allow_html=True)
        
        with col2:
            signe_pnl = "+" if plus_value_nette >  0 else ""
            signe_pct = "+" if pourcentage_pnl > 0 else ""
            valeur_formatee = f"{signe_pnl}{plus_value_nette:,.2f} € / {signe_pct}{pourcentage_pnl:.2f} %"
            metric_colored(
                label="Plus-Value Nette",
                value_str=valeur_formatee,
                val_numeric=plus_value_nette 
            )

        with col3:
            signe_pnl = "+" if plus_value_latente >  0 else ""
            signe_pct = "+" if pourcentage_lat > 0 else ""
            valeur_formatee_Lat = f"{signe_pnl}{plus_value_latente:,.2f} € / {signe_pct}{pourcentage_lat:.2f} %"
            metric_colored(
                label="Plus-Value Latnte",
                value_str=valeur_formatee_Lat,
                val_numeric=plus_value_latente
            )
        st.markdown("---")

        # --- 2ème Ligne : Titre et Indicateurs de Risque ---
        st.subheader("🔍 Analyse")
        col4, col5, col6 = st.columns([ 1, 1, 1])
        
        with col4:
            render_ratio_slider("Ratio de Sharpe", sharpe, min_val=-1.0, max_val=3.0, ratio_type="sharpe")
            
        with col5:
            render_ratio_slider("Ratio de Sortino", sortino, min_val=0.0, max_val=5.0, ratio_type="sortino")
            
        with col6:
            render_ratio_slider("Bêta (S&P 500)", beta, min_val=-1.0, max_val=2.0, ratio_type="beta")

        st.markdown("---")

      # --- Section Graphique : Plus-Value du Jour par Actif (1/3 de la largeur) ---
        st.subheader("🧩 Répartition des actifs")
        
        col_PL_jour, col_Rep, col_PL_Lat = st.columns([ 0.7, 1, 2])
        
        # --- Configuration globale du graphique ---
        config_graphique_pv = {
            "titre": "📈 Plus-Value du jour",
            "hauteur": 300,
            "largeur_barre": 0.25,
            "taille_police_texte": 14,
            "taille_police_ticker": 14,
            "couleur_ticker": "#F3B530",
            "couleur_positif": "#01d246",
            "couleur_negatif": "#ff4b4b",
            "couleur_neutre": "#808080",
            "marge_haut": 50,
            "marge_bas": 20
        }

        with col_PL_jour:
            if not df_holding.empty and df_holding.shape[1] >= 10:
                df_pv_jour = pd.DataFrame({
                    "Actif": df_holding.iloc[:, 0],
                    "PV_Jour": clean_financial_column(df_holding.iloc[:, 9])
                }).dropna(subset=["Actif", "PV_Jour"])
        
                # Appel de la fonction centralisée avec la config
                tracer_graphique_pv(df_pv_jour, config_graphique_pv)
            else:
                st.info("Colonnes insuffisantes pour accéder à la colonne J.")

        config_graphique_latente = {
            "titre": "📊 Plus-Value Latente",
            "hauteur": 300,
            "bargap": 0.4,
            "largeur_barre": 0.25,
            "taille_police_texte": 14,
            "taille_police_ticker": 14,
            "couleur_ticker": "#F3B530",
            "couleur_positif": "#00B0F0",
            "couleur_negatif": "#00B0F0",
            "couleur_neutre": "#808080",
            "marge_haut": 40,
            "marge_bas": 20,
            "marge_gauche": 10,
            "marge_droite": 50
        }
        
        with col_PL_Lat:
            if not df_holding.empty and df_holding.shape[1] >= 8:
                df_latente = pd.DataFrame({
                    "Actif": df_holding.iloc[:, 0],
                    "PV_Latente": clean_financial_column(df_holding.iloc[:, 7])  # Colonne H (index 7)
                }).dropna(subset=["Actif", "PV_Latente"])
                
                tracer_graphique_latente(df_latente, config_graphique_latente)
            else:
                st.warning("Colonnes insuffisantes pour accéder à la colonne H.")

        config_graphique_pie = {
            "titre": "🥧 Répartition des actifs",
            "hauteur": 300,
            "largeur": 300,
            "couleurs": ["#F3B530", "#01d246", "#4169E1"],  # Couleurs personnalisées pour tes 3 parts
            "trou": 0.4,                                     # Taille du trou central (effet donut)
            "marge_haut": 50,
            "marge_bas": 30,
            "marge_gauche": 60,
            "marge_droite": 60
        }
        
        with col_Rep:
            if not df_holding.empty and df_holding.shape[1] > 4:
                import plotly.express as px
                
                df_pie = pd.DataFrame({
                    "Actif": df_holding.iloc[:, 0],
                    "Valeur": clean_financial_column(df_holding.iloc[:, 4])
                }).dropna(subset=["Actif", "Valeur"])
                
                # Filtrer les valeurs strictement positives
                df_pie = df_pie[df_pie["Valeur"] > 0]
                
                # Appel de la fonction centralisée
                tracer_graphique_pie(df_pie, config_graphique_pie)
            else:
                st.info("Colonnes insuffisantes dans l'onglet holding pour afficher la répartition.")
    
    except Exception as e:
        st.error(f"Une erreur est survenue sur le Dashboard Global : {e}")
    
elif page == "📈 Vue Détaillée par Actif":
    st.header("📈 Vue Détaillée par Actif")
    try:
        df_holding = load_sheet_data("holding")
        df_valeurs = load_sheet_data("valeurs")
        df_donnees = load_sheet_data("donnees")
        
        st.success("Données des actifs chargées avec succès !")
        
        st.info("Aperçu de la Watchlist (nettoyée et limitée jusqu'à la colonne J) :")
        
        # Nettoyage et limitation
        df_donnees = df_donnees.replace(r'^\s*$', pd.NA, regex=True)
        df_donnees_propre = df_donnees.dropna(how='all').dropna(how='all', axis=1)
        df_donnees_limite = df_donnees_propre.iloc[:, :10]
        
        st.dataframe(df_donnees_limite)
        
    except Exception as e:
        st.error(f"Une erreur est survenue sur la vue détaillée : {e}")
        

    # Initialisation de l'état
    if "selected_asset" not in st.session_state:
        st.session_state.selected_asset = "S&P 500"
    if "selected_duree" not in st.session_state:
        st.session_state.selected_duree = "Mois"
    
    # Ligne des 6 boutons de durée
    st.markdown("### Durée")
    cols_duree = st.columns(6)
    durees = ["Semaine", "Mois", "Trimestre", "Semestre", "Au 1er J", "Année"]
    for i, d in enumerate(durees):
        if cols_duree[i].button(d, key=f"btn_dur_{d}"):
            st.session_state.selected_duree = d
    
    # Ligne des 6 boutons d'assets
    st.markdown("### Asset")
    cols_asset = st.columns(6)
    assets = ["S&P 500", "CAC 40", "VINCI", "SP5C", "AEME", "IWDA"]
    for i, a in enumerate(assets):
        if cols_asset[i].button(a, key=f"btn_ast_{a}"):
            st.session_state.selected_asset = a
    
    # Affichage du graphique avec l'état actuel
    df_filtre = get_asset_data(df_donnees, st.session_state.selected_asset, st.session_state.selected_duree)
    fig_ev = tracer_graphique_evolution(df_filtre, st.session_state.selected_asset, st.session_state.selected_duree)
    st.write("Aperçu de df_filtre :", df_filtre)
    st.plotly_chart(fig_ev, use_container_width=True)

elif page == "📝 Journal des Transactions":
    st.header("📝 Journal des Transactions")
    try:
        df_trans = load_sheet_data("transaction")
        
        st.success("Historique des transactions chargé avec succès !")
        st.dataframe(df_trans)
        
    except Exception as e:
        st.error(f"Une erreur est survenue sur le journal des transactions : {e}")
