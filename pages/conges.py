import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

# Configuration de la page Streamlit
st.set_page_config(page_title="Congés 2025", layout="wide")
st.title("Calendrier des Congés 2025")

# Fonction pour charger les données depuis le fichier texte
@st.cache_data
def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()

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


# Chemin vers le fichier texte (à remplacer par votre chemin réel)
file_path = "paste.txt"
df = load_data(file_path)

# Convertir les colonnes 'Début' et 'Fin' en datetime
df['Début'] = pd.to_datetime(df['Début'], errors='coerce')
df['Fin'] = pd.to_datetime(df['Fin'], errors='coerce')

# Filtrer les congés pour l'année 2025
df = df[df['Début'].dt.year == 2025]

# Fonction pour créer le calendrier mensuel
def create_monthly_calendar(year, month, data):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    st.subheader(f"{month_name} {year}")

    # Créer un DataFrame pour le calendrier
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append("")
            else:
                date = datetime(year, month, day)
                day_events = data[(data['Début'] <= date) & (data['Fin'] >= date)]
                events_text = "<br>".join([f"{row['Prénom et nom']} ({row['Type de congé']}): {row['Justification']}" for _, row in day_events.iterrows()])
                week_data.append(f"{day}<br>{events_text}")
        calendar_data.append(week_data)

    calendar_df = pd.DataFrame(calendar_data, columns=['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'])

    # Afficher le calendrier avec style
    st.dataframe(
        calendar_df,
        column_config={
            "Lundi": st.column_config.DataColumn(width="medium"),
            "Mardi": st.column_config.DataColumn(width="medium"),
            "Mercredi": st.column_config.DataColumn(width="medium"),
            "Jeudi": st.column_config.DataColumn(width="medium"),
            "Vendredi": st.column_config.DataColumn(width="medium"),
            "Samedi": st.column_config.DataColumn(width="medium"),
            "Dimanche": st.column_config.DataColumn(width="medium"),
        },
        height=(len(cal) + 1) * 80,  # Ajuster la hauteur en fonction du nombre de semaines
    )


# Afficher les calendriers mensuels pour toute l'année 2025
for month in range(1, 13):
    create_monthly_calendar(2025, month, df)
