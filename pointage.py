import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io

# Fonction pour calculer la durée de travail
def calculer_duree_travail(entree, sortie):
    if pd.isnull(entree) or pd.isnull(sortie):
        return None
    debut = datetime.strptime(entree, "%Y-%m-%d %H:%M")
    fin = datetime.strptime(sortie, "%Y-%m-%d %H:%M")
    if fin < debut:
        fin += timedelta(days=1)
    duree = (fin - debut)
    return duree

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('donnees_pointage.csv', parse_dates=['Date et heure'])
    df['Date'] = df['Date et heure'].dt.date
    return df

def get_correct_and_incorrect_pointages(df):
    entrees = df[df['Action'] == 'Pointer entrée'].groupby('Prénom et nom').last()
    sorties = df[df['Action'] == 'Pointer sortie'].groupby('Prénom et nom').first()
    
    tous_les_operateurs = set(df['Prénom et nom'].unique())
    operateurs_corrects = set(entrees.index) & set(sorties.index)
    operateurs_incorrects = tous_les_operateurs - operateurs_corrects
    
    return list(operateurs_corrects), list(operateurs_incorrects)
                       
# Dans la partie principale de votre application Streamlit
st.title("Analyse des pointages")

# Ajouter un widget pour télécharger le fichier Excel
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type="xlsx")

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        st.success("Données chargées avec succès !")
        
st.title("Analyse des pointages - Janvier 2025")

operateurs_corrects, operateurs_incorrects = get_correct_and_incorrect_pointages(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Opérateurs ayant pointé correctement")
    for operateur in operateurs_corrects:
        st.write(f"- {operateur}")

with col2:
    st.subheader("Opérateurs n'ayant pas pointé correctement")
    for operateur in operateurs_incorrects:
        st.write(f"- {operateur}")
        
# Filtrer les données pour janvier 2025
df_janvier = df[df['Date et heure'].dt.month == 1]

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
