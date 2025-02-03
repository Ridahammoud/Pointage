import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Fonction pour calculer la durée de travail
def calculer_duree_travail(entree, sortie):
    if pd.isnull(entree) or pd.isnull(sortie):
        return None
    debut = datetime.strptime(entree, "%Y-%m-%d %H:%M")
    fin = datetime.strptime(sortie, "%Y-%m-%d %H:%M")
    if fin < debut:
        fin += timedelta(days=1)
    duree = (fin - debut).total_seconds() / 60
    return duree

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('donnees_pointage.csv', parse_dates=['Date et heure'])
    df['Date'] = df['Date et heure'].dt.date
    return df

df = load_data()

st.title("Analyse des pointages - Janvier 2025")

# Filtrer les données pour janvier 2025
df_janvier = df[df['Date et heure'].dt.month == 1]

# Opérateurs ayant pointé correctement
st.header("Opérateurs ayant pointé correctement")
entrees = df_janvier[df_janvier['Action'] == 'Pointer entrée'].groupby('Prénom et nom').last()
sorties = df_janvier[df_janvier['Action'] == 'Pointer sortie'].groupby('Prénom et nom').first()
operateurs_corrects = entrees.join(sorties, lsuffix='_entree', rsuffix='_sortie', how='inner')

if not operateurs_corrects.empty:
    st.write(operateurs_corrects[['Date et heure_entree', 'Date et heure_sortie']])
else:
    st.write("Aucun opérateur n'a pointé correctement l'entrée et la sortie.")

# Calcul de la durée de travail
st.header("Durée de travail")
operateurs_corrects['Durée (minutes)'] = operateurs_corrects.apply(lambda row: calculer_duree_travail(row['Date et heure_entree'], row['Date et heure_sortie']), axis=1)
st.write(operateurs_corrects[['Date et heure_entree', 'Date et heure_sortie', 'Durée (minutes)']])

# Nombre total de pointages par jour
st.header("Nombre total de pointages par jour")
pointages_par_jour = df_janvier.groupby('Date').size()
st.bar_chart(pointages_par_jour)

# Taux de succès
st.header("Taux de succès")
taux_succes = (df_janvier['Statut'] == 'Succès').mean() * 100
st.metric("Taux de succès", f"{taux_succes:.2f}%")

# Observations particulières
st.header("Observations particulières")
observations = [
    f"Nombre total d'enregistrements en janvier : {len(df_janvier)}",
    f"Nombre d'opérateurs uniques : {df_janvier['Prénom et nom'].nunique()}",
    f"Jour avec le plus de pointages : {pointages_par_jour.idxmax()} ({pointages_par_jour.max()} pointages)",
    f"Jour avec le moins de pointages : {pointages_par_jour.idxmin()} ({pointages_par_jour.min()} pointages)",
    "Certains opérateurs ont des pointages incomplets (entrée sans sortie ou vice versa)",
    "Il y a des cas de pointages multiples pour certains opérateurs dans la même journée"
]
for obs in observations:
    st.write("- " + obs)

# Affichage des données brutes
if st.checkbox("Afficher les données brutes de janvier"):
    st.subheader("Données brutes de janvier 2025")
    st.write(df_janvier)
