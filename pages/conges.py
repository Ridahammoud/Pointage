import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

# Configuration de la page Streamlit
st.set_page_config(page_title="Congés 2025", layout="wide")
st.title("Calendrier des Congés 2025")

# Fonction pour charger les données depuis le fichier Excel
@st.cache_data
def load_data(file_path):
    # Utiliser pandas pour lire le fichier Excel
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        return None

    # Renommer les colonnes pour correspondre aux noms attendus
    df.rename(columns={
        'Type': 'Type',
        'Type de congé': 'Type de congé',
        'Début': 'Début',
        'Fin': 'Fin',
        'Justification': 'Justification'
    }, inplace=True)

    return df


# Charger les données depuis le fichier Excel
file_path = pd.read_excel("https://docs.google.com/spreadsheets/d/1zdp_Ub3RHTF9m9WYkddnwQrOz4woWjly/export?format=xlsx")
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
