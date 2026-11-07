


def get_asset_data(df, asset_name, duree):
    # Mapping des colonnes (Date, Valeur) selon l'asset
    mapping_colonnes = {
        "S&P 500": (12, 13) if duree in ["Semaine", "Mois"] else (26, 27),   # M / N ou AA / AB
        "CAC 40":  (14, 15) if duree in ["Semaine", "Mois"] else (28, 29),   # O / P ou AC / AD
        "VINCI":   (16, 17) if duree in ["Semaine", "Mois"] else (30, 31),   # Q / R ou AE / AF
        "SP5C":    (18, 19) if duree in ["Semaine", "Mois"] else (32, 33),   # S / T ou AG / AH
        "AEME":    (20, 21) if duree in ["Semaine", "Mois"] else (34, 35),   # U / V ou AI / AJ
        "IWDA":    (22, 23) if duree in ["Semaine", "Mois"] else (36, 37)    # W / X ou AK / AL
    }
    
    col_date, col_val = mapping_colonnes.get(asset_name, (12, 13))
    
    # Définition de la plage de lignes selon la durée
    fin_ligne = 24 if duree in ["Semaine", "Mois"] else 105
    
    # Extraction et nettoyage
    df_subset = df.iloc[2:fin_ligne, [col_date, col_val]].copy()
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
