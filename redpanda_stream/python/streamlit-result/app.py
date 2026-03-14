import streamlit as st
import pandas as pd
import s3fs
import pyarrow.dataset as ds
import pyarrow as pa
from dotenv import load_dotenv
import os
import time
from streamlit_autorefresh import st_autorefresh

# Charge les variables du fichier .env
load_dotenv()

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Bank Sandaga | Live Insights",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-active { color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- AUTO-REFRESH (Toutes les 3 secondes) ---
# Force le script à se relancer pour détecter les nouveaux fichiers
count = st_autorefresh(interval=3000, key="datarefresh")

# --- PARAMÈTRES MINIO ---
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "client-redpanda")
TOPIC_NAME = os.getenv("TOPIC_NAME", "bank_sandaga.REDPANDA.TYROK.product")
MINIO_CONF = {
    "key": os.getenv("MINIO_ACCESS_KEY", "admin"),
    "secret": os.getenv("MINIO_SECRET_KEY", "password123"),
    "client_kwargs": {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    }
}

@st.cache_data(ttl=2)
def load_data():
    base_path = f"{MINIO_BUCKET}/topics/{TOPIC_NAME}"
    
    # IMPORTANT : use_listings_cache=False force s3fs à rescanner le bucket à chaque appel
    fs = s3fs.S3FileSystem(**MINIO_CONF, use_listings_cache=False)
    
    try:
        # Initialisation du dataset avec partitionnement Hive
        dataset = ds.dataset(
            base_path, 
            filesystem=fs, 
            format="parquet", 
            partitioning="hive"
        )
        
        tables = []
        # Lecture fragment par fragment pour ignorer les fichiers en cours d'écriture
        for fragment in dataset.get_fragments():
            try:
                # Tentative de conversion en table (échoue si le fichier est incomplet/locké)
                table = fragment.to_table()
                df_temp = table.to_pandas()
                
                # SÉCURITÉ : Extraction manuelle des partitions (year, month, day, hour)
                # car pyarrow.dataset peut parfois les omettre sur des fragments isolés
                path_parts = fragment.path.split('/')
                for part in path_parts:
                    if '=' in part:
                        k, v = part.split('=')
                        df_temp[k] = v
                
                tables.append(pa.Table.from_pandas(df_temp))
            except Exception:
                # On ignore le fichier s'il est illisible (Redpanda est en train de l'écrire)
                continue

        if not tables:
            return pd.DataFrame()

        # Fusion de tous les fragments valides
        df = pa.concat_tables(tables).to_pandas()

        # Nettoyage et typage forcé pour éviter les erreurs d'affichage ou KeyError
        for col in ['year', 'month', 'day', 'hour']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            else:
                df[col] = 0 # Colonne de secours si absente
                
        return df

    except Exception as e:
        # Erreur si le bucket est inaccessible
        st.error(f"⚠️ Erreur système de fichiers : {e}")
        return pd.DataFrame()

# --- SIDEBAR (BARRE LATÉRALE) ---
with st.sidebar:
    st.title("🏦 Navigation")
    
    # BOUTON DE RAFRAÎCHISSEMENT MANUEL
    if st.button("🔄 Rafraîchir les données", use_container_width=True, type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Recherche dynamique
    search_query = st.text_input("🔍 Rechercher (Nom/Code)", "")
    
    st.divider()
    st.caption(f"Dernier check : {time.strftime('%H:%M:%S')}")
    st.caption(f"Total Refresh : {count}")

# --- CORPS PRINCIPAL ---
st.title("🏦 Bank Sandaga - Flux Clients Live")
df = load_data()

# Vérification des données avant affichage
if not df.empty and 'day' in df.columns:
    # Filtre de recherche
    if search_query:
        df = df[df['name'].str.contains(search_query, case=False) | 
                df['code'].str.contains(search_query, case=False)]

    # --- SECTION MÉTRIQUES ---
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Clients", len(df))
    with m2: 
        active_count = len(df[df['actif'] == True])
        pct = (active_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("Clients Actifs", active_count, f"{pct:.1f}%")
    with m3: 
        max_d, max_m = int(df['day'].max()), int(df['month'].max())
        st.metric("Dernière Ingestion", f"{max_d:02d}/{max_m:02d}")
    with m4: 
        mode_h = df['hour'].mode()
        st.metric("Heure Pointe", f"{int(mode_h[0]) if not mode_h.empty else 0}h")

    st.divider()

    # --- AFFICHAGE PAR ONGLETS ANNUELS ---
    years = sorted([y for y in df['year'].unique() if y > 0], reverse=True)
    
    if years:
        tabs = st.tabs([f"Année {int(y)}" for y in years])

        for i, year in enumerate(years):
            with tabs[i]:
                months = sorted(df[df['year'] == year]['month'].unique(), reverse=True)
                for month in months:
                    with st.expander(f"📂 Mois : {int(month):02d} / {int(year)}", expanded=(month == months[0])):
                        monthly_df = df[(df['year'] == year) & (df['month'] == month)]
                        
                        # Sélection et tri
                        display_df = monthly_df[['id', 'code', 'name', 'actif', 'day', 'hour']].copy()
                        display_df = display_df.sort_values(['day', 'hour'], ascending=False)
                        
                        st.dataframe(
                            display_df,
                            column_config={
                                "actif": st.column_config.CheckboxColumn("Statut"),
                                "id": st.column_config.NumberColumn("ID", format="%d"),
                                "day": "Jour", "hour": "Heure"
                            },
                            use_container_width=True,
                            hide_index=True,
                            key=f"df_{year}_{month}"
                        )
    else:
        st.info("Aucune partition annuelle détectée.")
else:
    st.warning("📭 Aucun fichier valide trouvé. Vérifiez le bucket MinIO.")

st.markdown("---")
st.markdown("<center><small>Dashboard Temps Réel</small></center>", unsafe_allow_html=True)
