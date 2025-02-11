import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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

# Fonction pour créer un calendrier mensuel avec les événements
def create_monthly_calendar(year, month, data):
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    days_in_month = [day for day in cal.itermonthdays(year, month) if day != 0]
    
    # Préparer les données par jour
    day_events = {day: 0 for day in days_in_month}
    for _, row in data.iterrows():
        start_date = max(row['Début'].date(), datetime(year, month, 1).date())
        end_date = min(row['Fin'].date(), datetime(year, month, calendar.monthrange(year, month)[1]).date())
        for day in range((end_date - start_date).days + 1):
            current_day = (start_date + timedelta(days=day)).day
            if current_day in day_events:
                day_events[current_day] += 1

    # Créer le graphique du calendrier
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 7)
    ax.set_ylim(0, (len(days_in_month) // 7) + 1)

    # Afficher les semaines du mois
    week_days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    for i, day_name in enumerate(week_days):
        ax.text(i + 0.5, 0.95, day_name, ha='center', va='center', fontsize=12, weight='bold')

    # Afficher les jours du mois
    for i, week in enumerate(cal.monthdayscalendar(year, month)):
        for j, day in enumerate(week):
            if day != 0:  # Ignorer les jours vides
                ax.add_patch(plt.Rectangle((j, (i + 1) * 0.9), 1, 1, facecolor='lightgray', edgecolor='black'))
                ax.text(j + 0.5, (i + 1) * 0.9 + 0.5, str(day), ha='center', va='center', fontsize=10)
                
                # Afficher le nombre d'événements
                if day in day_events and day_events[day] > 0:
                    ax.text(j + 0.5, (i + 1) * 0.9 + 0.2, f'{day_events[day]}', ha='center', va='center', fontsize=8, color='red')

    # Ajuster l'aspect
    ax.set_aspect('equal', 'box')
    plt.axis('off')
    st.pyplot(fig)

# Sélectionner le mois à afficher
month = st.selectbox("Choisissez le mois", list(calendar.month_name[1:]), index=0)
month_number = list(calendar.month_name).index(month)

# Afficher le calendrier pour le mois choisi
create_monthly_calendar(2025, month_number, df)
