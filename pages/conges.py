import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Configuration de la page Streamlit
st.set_page_config(page_title="Calendrier des Congés 2025", layout="wide")
st.title("Calendrier des Congés 2025")

# Fonction pour charger les données depuis le fichier texte
@st.cache_data
def load_data(file_path):
    # Utiliser pandas pour lire le fichier Excel
    try:
        data = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        return None

    # Diviser les données en blocs pour chaque employé
    employee_blocks = data.split('\n\n')

    # Initialiser une liste pour stocker les données
    data_list = []

    # Parcourir chaque bloc d'employé
    for block in employee_blocks:
        # Ignorer les blocs vides
        if not block.strip():
            continue

        # Extraire le nom de l'employé (première ligne)
        lines = block.splitlines()
        employee_name = lines[0].strip()

        # Trouver la ligne d'en-tête du tableau
        header_line = next((line for line in lines if 'Type' in line and 'Début' in line and 'Fin' in line), None)
        if not header_line:
            continue

        header = [h.strip() for h in header_line.split('\t')]
        header = [h for h in header if h]  # Nettoyer les en-têtes vides

        # Extraire les données des congés
        for line in lines[lines.index(header_line) + 1:]:
            if 'Total' in line:
                continue
            values = [v.strip() for v in line.split('\t')]
            values = [v for v in values if v]  # Nettoyer les valeurs vides
            
            # S'assurer que le nombre de valeurs correspond au nombre d'en-têtes
            if len(values) == len(header):
                entry = dict(zip(header, values))
                entry['Prénom et nom'] = employee_name  # Ajouter le nom de l'employé
                data_list.append(entry)

    # Créer le DataFrame
    df = pd.DataFrame(data_list)
    return df

# Charger les données depuis le fichier Excel
file_path = "https://docs.google.com/spreadsheets/d/1IO_1-v5i0IZQSF6UUfYEuKlTn6i-3hSI/export?format=xlsx"
df = load_data(file_path)

# Vérifier si le DataFrame a été chargé correctement
if df is None or df.empty:
    st.warning("Aucune donnée à afficher.")
    st.stop()

# Convertir les colonnes 'Début' et 'Fin' en datetime
df['Début'] = pd.to_datetime(df['Début'], errors='coerce')
df['Fin'] = pd.to_datetime(df['Fin'], errors='coerce')

# Filtrer les congés pour l'année 2025
df = df[df['Début'].dt.year == 2025]

# Function to create a monthly calendar with event counts
def create_monthly_calendar(year, month, data):
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_days = [n for n in cal.itermonthdays(year, month)]
    
    # Count events per day
    day_events = {}
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        date = datetime(year, month, day).date()
        day_events[day] = len(data[(data['Début'].dt.date <= date) & (data['Fin'].dt.date >= date)])
    
    # Setup the plot
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_aspect('equal')

    # Month and Year title
    month_name = calendar.month_name[month]
    ax.set_title(f"{month_name} {year}", fontsize=16, fontweight='bold')

    # Hide spines and ticks
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Add day labels
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for i, day in enumerate(day_names):
        ax.text((i/7) + (1/14), 0.9, day, ha='center', va='center', fontsize=12, color='dimgray')
    
    # Add the calendar days
    start_day = month_days[0]
    weeks = [month_days[i:i+7] for i in range(0, len(month_days), 7)]
    
    for i, week in enumerate(weeks):
        for j, day in enumerate(week):
            if day != 0:
                date = datetime(year, month, day).date()
                
                # Determine the color based on the event count
                event_count = day_events[day]
                if event_count > 3:
                    color = 'red'
                elif 1 <= event_count <= 3:
                    color = 'forestgreen'
                else:
                    color = 'lightgray'
                    
                # Add a circle for each day
                circle = plt.Circle((j/7 + 1/14), 0.1, color=color, linewidth=1, edgecolor='black', alpha=0.7, transform=ax.transAxes)
                ax.add_patch(circle)
                
                # Add the day number
                ax.text((j/7 + 1/14), (0.8 - (i/7 + 0.07)), str(day), ha='center', va='center', fontsize=10, color='black', transform=ax.transAxes)

    st.pyplot(fig)  # Display the Matplotlib figure in Streamlit

# Afficher les calendriers mensuels pour toute l'année 2025
for month in range(1, 13):
    create_monthly_calendar(2025, month, df)
