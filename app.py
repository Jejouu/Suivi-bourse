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
    metric_colored
)

import streamlit as st

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
        with st.expander("Afficher le tableau brut 'Holding'"):
            st.dataframe(df_holding)
        
        # 2. Récupération des valeurs via les fonctions modulaires
        total_valeur = get_total_portfolio_value(df_holding)
        plus_value_nette = get_net_pnl(df_holding)
        plus_value_latente = get_unrealized_pnl(df_holding)
        sharpe = clean_str_to_float(get_cell_value("valeurs", "B4"))
        sortino = clean_str_to_float(get_cell_value("valeurs", "B5"))
        beta = clean_str_to_float(get_cell_value("valeurs", "B6"))
        
        # --- 1ère Ligne : Indicateurs Financiers ---
        st.subheader("💶 Valeur du portefeuille")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Valeur Totale", f"{total_valeur:,.2f} €")
        
        with col2:
            metric_colored("Plus-Value Nette", f"{plus_value_nette:+,.2f} €", plus_value_nette)

        with col3:
            metric_colored("Plus-Value Latente", f"{plus_value_latente:+,.2f} €", plus_value_latente)

        st.markdown("---")

        # --- 2ème Ligne : Titre et Indicateurs de Risque ---
        st.subheader("🔍 Analyse")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            render_ratio_slider("Ratio de Sharpe", sharpe, min_val=-1.0, max_val=3.0, ratio_type="sharpe")
            
        with col5:
            render_ratio_slider("Ratio de Sortino", sortino, min_val=0.0, max_val=5.0, ratio_type="sortino")
            
        with col6:
            render_ratio_slider("Bêta (S&P 500)", beta, min_val=-1.0, max_val=2.0, ratio_type="beta")

        st.markdown("---")

      # --- Section Graphique : Plus-Value du Jour par Actif (1/3 de la largeur) ---
        st.subheader("📈 +/- Value du jour par actif")
        
        col_graphe, col_vide = st.columns([1, 2])
        
        with col_graphe:
            if not df_holding.empty and df_holding.shape[1] >= 10:
                import plotly.express as px
                
                df_pv_jour = pd.DataFrame({
                    "Actif": df_holding.iloc[:, 0],
                    "PV_Jour": clean_financial_column(df_holding.iloc[:, 9])
                }).dropna(subset=["Actif", "PV_Jour"])
                
                if not df_pv_jour.empty:
                    # Formatage explicite du texte pour inclure le symbole €
                    df_pv_jour["Texte_Affiche"] = df_pv_jour["PV_Jour"].apply(lambda x: f"{x:,.2f} €")
                    
                    fig_pv = px.bar(
                        df_pv_jour,
                        x="Actif",
                        y="PV_Jour",
                        text="Texte_Affiche",
                        title=""
                    )
                    
                    # Barres plus fines et texte agrandi au-dessus
                    fig_pv.update_traces(
                        marker_color="#808080",
                        textfont=dict(size=16, color="white"),  # Taille du texte augmentée (16px)
                        textposition="outside",                # Positionné au-dessus de la barre
                        textangle=0,
                        width=0.15                             # Épaisseur des barres réduite
                    )
                    
                    fig_pv.update_layout(
                        cliponaxis=False,                      # Empêche le texte de se faire couper en haut
                        margin=dict(t=50, b=20, l=10, r=10),   # Marge haute élargie pour laisser de la place au texte
                        xaxis_title="",
                        yaxis_title="",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="white")
                    )
                    
                    st.plotly_chart(fig_pv, use_container_width=True)
                else:
                    st.warning("Aucune donnée valide trouvée dans la colonne J.")
            else:
                st.info("Colonnes insuffisantes pour accéder à la colonne J.")
                
        with col_vide:
            st.info("Espace réservé pour le prochain graphique (2/3)")
        
        # 4. Section Graphique Camembert (Répartition par Actif)
        st.subheader("🥧 Répartition du Portefeuille par Actif")
        
        if not df_holding.empty and df_holding.shape[1] > 4:
            import plotly.express as px
            
            df_pie = pd.DataFrame({
                "Actif": df_holding.iloc[:, 0],
                "Valeur": clean_financial_column(df_holding.iloc[:, 4])
            }).dropna(subset=["Actif", "Valeur"])
            
            # Filtrer les valeurs strictement positives
            df_pie = df_pie[df_pie["Valeur"] > 0]
            
            if not df_pie.empty:
                fig = px.pie(
                    df_pie, 
                    names="Actif", 
                    values="Valeur", 
                    hole=0.4, 
                    title=""
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Aucune donnée numérique valide trouvée pour afficher le camembert.")
        else:
            st.info("Colonnes insuffisantes dans l'onglet holding pour afficher la répartition.")

    except Exception as e:
        st.error(f"Une erreur est survenue sur le Dashboard Global : {e}")
elif page == "📈 Vue Détaillée par Actif":
    st.header("📈 Vue Détaillée par Actif")
    try:
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

elif page == "📝 Journal des Transactions":
    st.header("📝 Journal des Transactions")
    try:
        df_trans = load_sheet_data("transaction")
        
        st.success("Historique des transactions chargé avec succès !")
        st.dataframe(df_trans)
        
    except Exception as e:
        st.error(f"Une erreur est survenue sur le journal des transactions : {e}")
