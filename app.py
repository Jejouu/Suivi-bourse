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
if page == "📊 Dashboard Global":
    st.header("📊 Dashboard Global du Portefeuille")
    try:
        # Chargement des onglets nécessaires
        df_holding = load_sheet_data("holding")
        df_hist = load_sheet_data("histporte")
        
        st.success("Données du portefeuille chargées avec succès !")
        
        # Intégration de la colonne H (Total Holding)
        if df_holding.shape[1] > 7:
            col_h = clean_financial_column(df_holding.iloc[:, 7])
            total_holding = col_h.sum()
            st.metric(label="Valeur Totale du Portefeuille (Col H)", value=f"{total_holding:,.2f} €")
        
        # Affichage du tableau brut 'Holding'
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
        
        st.info("Aperçu de l'onglet 'Donnees' (filtré jusqu'à la colonne J) :")
        
        # Filtrage pour n'afficher que les colonnes de 0 à J (soit les 10 premières colonnes, index 0 à 9)
        df_donnees_limite = df_donnees.iloc[:, :10]
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
