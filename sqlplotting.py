import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def histogram_table_feature(db, table, feature, label="name"):
    """
    Balkendiagramm für diskrete Werte in einem numerischen Feature,
    sortiert nach Häufigkeit (absteigend).
    """
    df = pd.DataFrame(db[table])
    df_selected = df[[feature, label]].dropna()

    # Gruppieren nach Feature-Wert und zählen
    counts = df_selected.groupby(feature).size().reset_index(name='count')
    counts = counts.sort_values(by='count', ascending=False)

    # Optional: Hovertext pro Balken zusammensetzen
    hover_map = df_selected.groupby(feature)[label].apply(lambda names: "<br>".join(names.unique()))
    counts["hover"] = counts[feature].map(hover_map)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=counts[feature],
            y=counts["count"],
            hovertext=counts["hover"],
            marker_color="black",
            showlegend=False
        )
    )

    fig.update_layout(
        title_text=f"{feature}_histo",
        xaxis=dict(showticklabels=False),  # Keine X-Ticks oder Labels
        yaxis_title="Anzahl",
        width=40*len(counts),
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    filename = f"{table}_{feature}_histo.html"
    fig.write_html(filename)
    fig.show()


def histogram_table_features(db, table, features, label="name"):
    df = pd.DataFrame(db[table])
    df_selected = df[features + [label]]

    
    name = table
    for f in features:
        name += f"_{f}"
        
    n = len(features)
    fig = make_subplots(
        rows=1, cols=n,
        subplot_titles=[f.capitalize() for f in features]
    )

    for i, feat in enumerate(features):
        fig.add_trace(
            go.Histogram(
                x=df_selected[feat],
                name=name+"_histograms",
                hovertext=df_selected[label],
                marker_color='black',
                showlegend=False
            ),
            row=1, col=i+1
        )

    fig.update_layout(
        title_text=name+"_histograms",
        width=300 * n,
        height=400,
    )
    
    name += "_histos.html"
    fig.write_html(name)
    fig.show()

def compare_table_features(db, table, features, label="name"):
    df = pd.DataFrame(db[table])
    df_selected = df[features + [label]]

    name = table
    for i in features:
        name += f"_{i}"
    
    fig = px.scatter_matrix(
        df_selected,
        dimensions=features,
        labels={col: col.capitalize() for col in features},
        title=name+"_comparison",
        color_discrete_sequence=["black"],
        hover_name=label 
    )
    
    # Achsenbeschriftungen anzeigen
    fig.update_traces(diagonal_visible=True)  # Histogramme auf Diagonale zeigen
    fig.update_layout(
        dragmode='select',
        width=800,
        height=800
    )
    
    name += "_comparison.html"
    fig.write_html(name)
    fig.show()