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
def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            # Charger le fichier Excel ou CSV
            df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
            
            # Vérifier si la colonne "Date et heure" existe
            if 'Date et heure' not in df.columns:
                st.error("Le fichier ne contient pas de colonne 'Date et heure'.")
                return None
            
            # Convertir la colonne "Date et heure" en type datetime
            df['Date et heure'] = pd.to_datetime(df['Date et heure'], errors='coerce')
            
            # Vérifier les valeurs non converties (NaT)
            if df['Date et heure'].isna().any():
                st.warning("Certaines valeurs dans la colonne 'Date et heure' n'ont pas pu être converties.")
            
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {e}")
            return None
    else:
        return None

def get_correct_and_incorrect_pointages(df):
    entrees = df[df['Action'] == 'Pointer entrée'].groupby('Prénom et nom').last()
    sorties = df[df['Action'] == 'Pointer sortie'].groupby('Prénom et nom').first()
    
    tous_les_operateurs = set(df['Prénom et nom'].unique())
    operateurs_corrects = set(entrees.index) & set(sorties.index)
    operateurs_incorrects = tous_les_operateurs - operateurs_corrects
    
    return list(operateurs_corrects), list(operateurs_incorrects)

# Fonction pour créer les colonnes 'Date et heure_entree' et 'Date et heure_sortie'
def create_entry_exit_columns(df):
    # Créer des colonnes vides pour l'entrée et la sortie
    df['Date et heure_entree'] = pd.NaT
    df['Date et heure_sortie'] = pd.NaT

    # Remplir les colonnes en fonction de l'action
    mask_entree = df['Action'] == 'Pointer entrée'
    mask_sortie = df['Action'] == 'Pointer sortie'

    df.loc[mask_entree, 'Date et heure_entree'] = df.loc[mask_entree, 'Date et heure']
    df.loc[mask_sortie, 'Date et heure_sortie'] = df.loc[mask_sortie, 'Date et heure']

    # Grouper par 'Prénom et nom' pour avoir une ligne par personne avec entrée et sortie
    df_grouped = df.groupby('Prénom et nom').agg({
        'Date et heure_entree': 'first',  # Première entrée enregistrée
        'Date et heure_sortie': 'last',  # Dernière sortie enregistrée
        'PIN': 'first'  # Conserver le PIN de l'employé
    }).reset_index()

    return df_grouped

def get_entry_exit_times(df):
    # Trier le DataFrame par employé et date/heure
    df = df.sort_values(['Prénom et nom', 'Date et heure'])
    
    # Initialiser les listes pour stocker les résultats
    entries = []
    exits = []
    noms = []
    durees = []
    
    for name, group in df.groupby('Prénom et nom'):
        entry_time = None
        for _, row in group.iterrows():
            if row['Action'] == 'Pointer entrée' and entry_time is None:
                entry_time = row['Date et heure']
                prenom_nom = row['Prénom et nom']
            elif row['Action'] == 'Pointer sortie' and entry_time is not None:
                exit_time = row['Date et heure']
                if exit_time - entry_time <= timedelta(days=1):
                    entries.append(entry_time)
                    exits.append(exit_time)
                    noms.append(prenom_nom)
                    
                    # Calculer la durée en heures
                    duree = (exit_time - entry_time).total_seconds() / 3600
                    durees.append(round(duree, 2))
                    
                    entry_time = None
                else:
                    # Si la sortie est plus d'un jour après l'entrée, on l'ignore
                    entry_time = None
    
    return pd.DataFrame({'Prénom et nom': noms,'Entrée': entries,'Sortie': exits,'Durée (heures)': durees})
                       
# Dans la partie principale de votre application Streamlit
st.title("Analyse des pointages")

# Ajouter un widget pour télécharger le fichier Excel
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type="xlsx")
df = load_data(uploaded_file)

if uploaded_file is not None:
    # Charger les données depuis le fichier téléchargé
    df = load_data(uploaded_file)
    
    if df is not None:
        st.success("Données chargées avec succès !")

        # Créer les colonnes d'entrée/sortie
        df_with_entry_exit = create_entry_exit_columns(df)

        # Afficher les opérateurs avec leurs entrées/sorties
        result = get_entry_exit_times(df)
        st.subheader("Opérateurs avec entrées/sorties et durées correspondantes")
        st.write(result)
        
    else:
        st.error("Impossible de charger les données. Vérifiez le fichier.")
else:
    st.info("Veuillez télécharger un fichier Excel ou CSV pour commencer l'analyse.")
        
st.title("Analyse des pointages - Janvier 2025")

operateurs_corrects, operateurs_incorrects = get_correct_and_incorrect_pointages(df)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Opérateurs ayant pointé correctement")
    for operateur in operateurs_corrects:        
        st.write(", ".join(operateur))

with col2:
    st.subheader("Opérateurs n'ayant pas pointé correctement")
    for operateur in operateurs_incorrects:
        st.write(", ".join(operateur))
        
# Filtrer les données pour janvier 2025
df_janvier = df[df['Date et heure'].dt.month == 1]

# Nombre total de pointages par jour
st.header("Nombre total de pointages par jour")
df_janvier['Date'] = pd.to_datetime(df_janvier['Date et heure']).dt.date
pointages_par_jour = df_janvier.groupby('Date').size()
st.bar_chart(pointages_par_jour)

# Calculer le taux de succès
total_actions = len(df)
actions_succes = len(df[df['Statut'] == 'Succès'])
success_rate = (actions_succes / total_actions) * 100
failure_rate = 100 - success_rate

# Création du camembert 3D
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='3d'))

# Taux de succès
st.header("Taux de succès")
taux_succes = (df_janvier['Statut'] == 'Succès').mean() * 100
# Données du taux de succès
success_rate = taux_succes
failure_rate = 100 - success_rate

# Création du camembert
fig, ax = plt.subplots()
sizes = [success_rate, failure_rate]
labels = ['Succès', 'Échec']
colors = ['#4CAF50', '#F44336']
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

# Titre du graphique
plt.title("Taux de succès des pointages")

# Affichage du camembert dans Streamlit
st.pyplot(fig)

result = get_entry_exit_times(df)
print(result)

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
