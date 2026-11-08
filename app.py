import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
    col1, col2, col3 = st.columns([3,2,1])
    
    with col1:st.header("📊 Dashboard Global du Portefeuille")

    with col3:
        if st.button("🔄 Actualiser les données"):
            st.cache_data.clear()
            st.rerun()
    try:
        # 1. Chargement des onglets nécessaires
        df_holding = load_sheet_data("holding")
        df_hist = load_sheet_data("histporte")

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
                
        st.markdown("---")
        
        afficher_investissement = st.checkbox("Afficher la courbe d'investissement", value=True)
        
        if 'selected_duree_global' not in st.session_state:
            st.session_state.selected_duree_global = "Depuis le début"
        
        # 1. Détection automatique des colonnes si nécessaire
        col_date = 'A' if 'A' in df_hist.columns else df_hist.columns[0]
        col_val = 'B' if 'B' in df_hist.columns else df_hist.columns[1]
        col_inv = 'J' if 'J' in df_hist.columns else df_hist.columns[min(9, len(df_hist.columns)-1)]
        
        # 2. Conversion sécurisée des dates et nettoyage
        df_hist[col_date] = pd.to_datetime(df_hist[col_date], format='mixed', dayfirst=True)
        today = pd.Timestamp.today()
        df_hist = df_hist[(df_hist[col_date].notna()) & (df_hist[col_date] <= today)]
        
        col_g, col_d = st.columns([6, 1])
            
        with col_g:
            if st.session_state.selected_duree_global == "1 mois":
                target_date = today - pd.DateOffset(months=1)
            elif st.session_state.selected_duree_global == "3 mois":
                target_date = today - pd.DateOffset(months=3)
            elif st.session_state.selected_duree_global == "6 mois":
                target_date = today - pd.DateOffset(months=6)
            elif st.session_state.selected_duree_global == "1 an":
                target_date = today - pd.DateOffset(years=1)
            elif st.session_state.selected_duree_global == "Au 1er J":
                target_date = pd.Timestamp(today.year, 1, 1)
            else:
                target_date = df_hist[col_date].min()
        
            min_dispo = df_hist[col_date].min()
            if target_date < min_dispo:
                target_date = min_dispo
        
            df_hist_filtre = df_hist[(df_hist[col_date] >= target_date) & (df_hist[col_date] <= today)]
        
            dates = df_hist_filtre[col_date]
            valeur_portfolio = pd.to_numeric(df_hist_filtre[col_val].astype(str).str.replace(',', '.'), errors='coerce')
            investissement = pd.to_numeric(df_hist_filtre[col_inv].astype(str).str.replace(',', '.'), errors='coerce')
        
            fig = go.Figure()
        
            fig.add_trace(go.Scatter(
                x=dates,
                y=valeur_portfolio,
                mode='lines',
                name='Valeur du portefeuille',
                line=dict(color='#4169E1', width=2)
            ))
        
            if afficher_investissement:
                fig.add_trace(go.Scatter(
                    x=dates,
                    y=investissement,
                    mode='lines',
                    name='Investissement',
                    line=dict(color='#F3B530', width=2, dash='dash')
                ))
        
            fig.update_layout(
                template='plotly_dark',
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
        
            st.plotly_chart(fig, use_container_width=True)
        with col_d:
            durees_global = ["1 mois", "3 mois", "6 mois", "1 an", "Au 1er J", "Depuis le début"]
            for d in durees_global:
                btn_type = "primary" if st.session_state.selected_duree_global == d else "secondary"
                if st.button(d, key=f"btn_global_{d}", type=btn_type, use_container_width=True):
                    st.session_state.selected_duree_global = d
                    st.rerun()

            if not df_hist_filtre.empty:
                val_initiale = pd.to_numeric(str(df_hist_filtre[col_val].iloc[0]).replace(',', '.'), errors='coerce')
                inv_initiale = pd.to_numeric(str(df_hist_filtre[col_inv].iloc[0]).replace(',', '.'), errors='coerce')
                
                val_finale = pd.to_numeric(str(df_hist_filtre[col_val].iloc[-1]).replace(',', '.'), errors='coerce')
                inv_finale = pd.to_numeric(str(df_hist_filtre[col_inv].iloc[-1]).replace(',', '.'), errors='coerce')
                
                gain_initial = val_initiale - inv_initiale
                gain_final = val_finale - inv_finale
                
                diff = gain_final - gain_initial
                pct = (diff / val_initiale) * 100 if val_initiale != 0 else 0
                
                color = "#00FF00" if diff >= 0 else "#FF4B4B"
                arrow = "▲" if diff >= 0 else "▼"
                sign = "+" if diff >= 0 else ""
            
                st.markdown(f"""
                <style>
                .metric-card-global {{
                    background-color: #2E3239;
                    border: 2px solid #383C4A;
                    border-radius: 15px;
                    padding: 15px 20px;
                    margin-top: 15px;
                    font-family: sans-serif;
                }}
                .metric-title-global {{
                    color: #FFFFFF;
                    font-weight: bold;
                    font-size: 15px;
                    margin-bottom: 10px;
                }}
                .metric-row-global {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-top: 8px;
                }}
                .metric-label-global {{
                    color: #A0A0A0;
                    font-size: 13px;
                }}
                .metric-value-global {{
                    color: {color};
                    font-weight: bold;
                    font-size: 18px;
                }}
                </style>
            
                <div class="metric-card-global">
                    <div class="metric-title-global">Performance de la période</div>
                    <div class="metric-row-global">
                        <span class="metric-label-global">Variation absolue</span>
                        <span class="metric-value-global">{arrow} {sign}{diff:,.2f}</span>
                    </div>
                    <div class="metric-row-global">
                        <span class="metric-label-global">Pourcentage</span>
                        <span class="metric-value-global">{arrow} {sign}{pct:.2f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Une erreur est survenue sur le Dashboard Global : {e}")
    
elif page == "📈 Vue Détaillée par Actif":

    col1, col2, col3 = st.columns([3,2,1])
    
    with col1:st.header("📈 Vue Détaillée par Actif")

    with col3:
        if st.button("🔄 Actualiser les données"):
            st.cache_data.clear()
            st.rerun()

    try:
        df_holding = load_sheet_data("holding")
        df_valeurs = load_sheet_data("valeurs")
        df_donnees = load_sheet_data("donnees")
        
        df_donnees = df_donnees.replace(r'^\s*$', pd.NA, regex=True)
        df_donnees_propre = df_donnees.dropna(how='all').dropna(how='all', axis=1)
        df_donnees_limite = df_donnees_propre.iloc[:, :10]

        with st.expander("Watchlist"):
            st.dataframe(df_donnees_limite)
            
    except Exception as e:
        st.error(f"Une erreur est survenue sur la vue détaillée : {e}")

    if "selected_asset" not in st.session_state:
        st.session_state.selected_asset = "S&P 500"
    if "selected_duree" not in st.session_state:
        st.session_state.selected_duree = "Semaine"
    
    col_graph, col_assets = st.columns([4, 0.5])
    
    with col_graph:
        df_filtre = get_asset_data(df_donnees, st.session_state.selected_asset, st.session_state.selected_duree)
        fig_ev = tracer_graphique_evolution(df_filtre, st.session_state.selected_asset, st.session_state.selected_duree)
        st.plotly_chart(fig_ev, use_container_width=True)
        
        cols_duree = st.columns(6)
        durees = ["Semaine", "Mois", "Trimestre", "Semestre", "Au 1er J", "Année"]
        for i, d in enumerate(durees):
            btn_type = "primary" if st.session_state.selected_duree == d else "secondary"
            if cols_duree[i].button(d, key=f"btn_dur_{d}", type=btn_type, use_container_width=True):
                st.session_state.selected_duree = d
                st.rerun()
    
    with col_assets:
        assets = ["S&P 500", "CAC 40", "VINCI", "SP5C", "AEME", "IWDA"]
        for a in assets:
            btn_type_ast = "primary" if st.session_state.selected_asset == a else "secondary"
            if st.button(a, key=f"btn_ast_{a}", type=btn_type_ast, use_container_width=True):
                st.session_state.selected_asset = a
                st.rerun()
    
    col_valeur = 'Valeur' if 'Valeur' in df_filtre.columns else df_filtre.select_dtypes(include='number').columns[-1]

    if not df_filtre.empty and col_valeur in df_filtre.columns:
        val_initiale = df_filtre[col_valeur].iloc[0]
        val_finale = df_filtre[col_valeur].iloc[-1]
            
        diff = val_finale - val_initiale
        pct = (diff / val_initiale) * 100 if val_initiale != 0 else 0
        
        color = "#00FF00" if diff >= 0 else "#FF4B4B"
        arrow = "▲" if diff >= 0 else "▼"
        sign = "+" if diff >= 0 else ""
    
        st.markdown(f"""
        <style>
        .metric-container {{
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }}
        .metric-card {{
            background-color: #2E3239;
            border: 3.5px solid #747474;
            border-radius: 15px;
            padding: 15px 20px;
            flex: 0 0 20%;
            font-family: sans-serif;
        }}
        .metric-title {{
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 4px;
        }}
        .metric-value {{
            color: {color};
            font-weight: bold;
            font-size: 20px;
        }}
        </style>
    
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-title">Variation absolue</div>
                <div class="metric-value">{arrow} {sign}{diff:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Pourcentage</div>
                <div class="metric-value">{arrow} {sign}{pct:.2f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("Données insuffisantes pour afficher les métriques.")

elif page == "📝 Journal des Transactions":
    st.header("📝 Journal des Transactions")
    try:
        df_trans = load_sheet_data("transaction")
        
        st.success("Historique des transactions chargé avec succès !")
        st.dataframe(df_trans)
        
    except Exception as e:
        st.error(f"Une erreur est survenue sur le journal des transactions : {e}")
