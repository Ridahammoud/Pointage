import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta
import plotly.express as px

# Configuration de la page Streamlit
st.set_page_config(page_title="Calendrier des Congés 2025", layout="wide")
st.title("Calendrier des Congés 2025")

# Fonction pour charger les données depuis le fichier Excel
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        return None

    # Vérifier et renommer les colonnes si nécessaire
    expected_columns = ['Prénom et nom', 'Type', 'Type de congé', 'Début', 'Fin',
                        'Succursale', 'Position', 'Ressources', 'Total (h)', 'Note',
                        '# de la demande', 'Créée le', 'Approuvé à', 'Approbateur', 'Justification']
    if not all(col in df.columns for col in expected_columns):
        st.error("Les colonnes du fichier ne correspondent pas au format attendu.")
        return None

    return df

# URL du fichier Excel (Google Sheets exporté en .xlsx)
file_path = "https://docs.google.com/spreadsheets/d/1IO_1-v5i0IZQSF6UUfYEuKlTn6i-3hSI/export?format=xlsx"
df = load_data(file_path)

# Vérifier si le DataFrame a été chargé correctement
if df is None or df.empty:
    st.warning("Aucune donnée à afficher.")
    st.stop()

# Convertir les colonnes 'Début' et 'Fin' en format datetime
df['Début'] = pd.to_datetime(df['Début'], errors='coerce')
df['Fin'] = pd.to_datetime(df['Fin'], errors='coerce')

# Filtrer les congés pour l'année 2025
df = df[(df['Début'].dt.year == 2025) | (df['Fin'].dt.year == 2025)]

# Fonction pour créer un calendrier interactif
def create_interactive_calendar(year, data):
    # On crée un tableau de données avec chaque jour de l'année
    days = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='D')
    day_events = {day.date(): 0 for day in days}  # Initialiser day_events avec des dates de type datetime.date
    
    # Comptabiliser les congés par jour
    for _, row in data.iterrows():
        start_date = row['Début']
        end_date = row['Fin']
        
        for day in pd.date_range(start=start_date, end=end_date, freq='D'):
            if day.year == year:
                day_events[day.date()] += 1  # Utiliser .date() pour garantir que day est de type datetime.date

    # Créer les couleurs pour chaque jour
    colors = []
    for day in days:
        day_key = day.date()  # Utiliser .date() pour le comparer avec les clés dans day_events
        if day_events[day_key] > 3:
            colors.append('red')
        elif day_events[day_key] > 0:
            colors.append('green')
        else:
            colors.append('gray')

    # Création de la figure Plotly
    fig = go.Figure()

    # Ajout des jours au calendrier
    fig.add_trace(go.Scatter(
        x=days, y=[0] * len(days),
        mode='markers',
        marker=dict(color=colors, size=15),
        hovertext=[f"{day.strftime('%Y-%m-%d')}: {day_events[day.date()]} congé(s)" for day in days],
        hoverinfo="text"
    ))

    # Mise en forme du calendrier
    fig.update_layout(
        title=f"Calendrier des Congés {year}",
        xaxis=dict(
            tickvals=pd.to_datetime([f"{year}-{i:02d}-01" for i in range(1, 13)]),
            ticktext=[calendar.month_name[i] for i in range(1, 13)],
            title="Mois",
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            title="Jours"
        ),
        showlegend=False,
        plot_bgcolor="white",
        height=600
    )

    return fig

# Créer un calendrier interactif pour l'année 2025
fig = create_interactive_calendar(2025, df)

# Afficher le graphique interactif
st.plotly_chart(fig)

# Détails du congé sélectionné
st.subheader("Détails des Congés")
selected_date = st.date_input("Sélectionner une date", min_value=datetime(2025, 1, 1), max_value=datetime(2025, 12, 31))
selected_day_conges = df[(df['Début'].dt.date <= selected_date) & (df['Fin'].dt.date >= selected_date)]

if selected_day_conges.empty:
    st.write(f"Aucun congé programmé pour le {selected_date}.")
else:
    for _, row in selected_day_conges.iterrows():
        st.write(f"**Nom**: {row['Prénom et nom']}")
        st.write(f"**Type de congé**: {row['Type de congé']}")
        st.write(f"**Justification**: {row['Justification']}")
        st.write(f"**Période**: {row['Début'].strftime('%Y-%m-%d')} à {row['Fin'].strftime('%Y-%m-%d')}")
        st.write("---")
