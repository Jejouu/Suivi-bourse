import streamlit as st
import pandas as pd
from Utils.loader import load_sheet_data, clean_financial_column

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
    try:
        # Chargement des onglets nécessaires
        df_holding = load_sheet_data("holding")
        df_hist = load_sheet_data("histporte")
        
        st.success("Données du portefeuille chargées avec succès !")
        
        # --- Section KPI ---
        col1, col2, col3 = st.columns(3)
        
        if df_holding.shape[1] > 4:
            col_e = clean_financial_column(df_holding.iloc[:, 4])
            total_holding = col_e.sum()
            col1.metric(label="Valeur Totale du Portefeuille", value=f"{total_holding:,.2f} €")
        else:
            col1.metric(label="Valeur Totale du Portefeuille", value="N/A")
            
         if df_holding.shape[1] > 7:
            col_h = clean_financial_column(df_holding.iloc[:, 7])
            total_holding = col_h.sum()
            col2.metric(label="Plus value latente", value=f"{total_holding:,.2f} €")
        else:
            col2.metric(label="Plus value latente", value="N/A")
            
        col3.metric(label="Statut Données", value="Synchronisé 🟢")
        
        st.markdown("---")
        
     # --- Section Graphique Camembert (Répartition par Actif) ---
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
        
        # Affichage du tableau brut 'Holding' dans un expander
        with st.expander("Afficher le tableau brut 'Holding'"):
            st.dataframe(df_holding)
            
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
