import plotly.graph_objects as go
import pandas as pd

def get_asset_data(df, asset_name, duree):
    # Mapping des colonnes (Date, Valeur) selon l'asset
    mapping_colonnes = {
        "S&P 500": (11, 12) if duree in ["Semaine", "Mois"] else (25, 26),   # M / N ou AA / AB
        "CAC 40":  (13, 14) if duree in ["Semaine", "Mois"] else (27, 28),   # O / P ou AC / AD
        "VINCI":   (15, 16) if duree in ["Semaine", "Mois"] else (29, 30),   # Q / R ou AE / AF
        "SP5C":    (17, 18) if duree in ["Semaine", "Mois"] else (31, 32),   # S / T ou AG / AH
        "AEME":    (19, 20) if duree in ["Semaine", "Mois"] else (33, 34),   # U / V ou AI / AJ
        "IWDA":    (21, 22) if duree in ["Semaine", "Mois"] else (35, 36)    # W / X ou AK / AL
    }
    
    col_date, col_val = mapping_colonnes.get(asset_name, (11, 12))
    
    # Définition de la plage de lignes selon la durée
    fin_ligne = 24 if duree in ["Semaine", "Mois"] else 105
    
    debut_lignes = {
    "Semaine": 16,
    "Mois": 2,
    "Trimestre": 90,
    "Semestre": 77,
    "Au 1er J": 59,
    "Année": 51
    }
    debut_ligne = debut_lignes.get(duree, 2)
    
    # Extraction et nettoyage
    df_subset = df.iloc[debut_ligne:fin_ligne, [col_date, col_val]].copy()
    df_subset.columns = ['Date', 'Close']
    df_subset['Close'] = pd.to_numeric(df_subset['Close'].astype(str).str.replace(',', '.'), errors='coerce')
    df_subset = df_subset.dropna()
    
    return df_subset

import plotly.graph_objects as go

def tracer_graphique_evolution(df_subset, asset_name, duree):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_subset['Date'],
        y=df_subset['Close'],
        mode='lines',
        line=dict(color='#00FF7F', width=2),
        hoverinfo='x+y'
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Évolution - {asset_name} ({duree})",
            font=dict(size=18, color="white"),
            x=0.5,
            xanchor='center'
        ),
        margin=dict(t=50, b=30, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        showlegend=False,
        height=350
    )
    return fig
