import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilo CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #1c202a; padding: 20px; border-radius: 10px; 
        border: 1px solid #31333F; margin-bottom: 10px;
    } 
    .metric-title {
        color: #808495; font-size: 14px; text-transform: uppercase;
    } 
    .metric-value {
        color: #ffffff; font-size: 28px; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

# URL de tu Google Sheet
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Leer datos SIN cache para forzar la actualización en cada refresco
try:
    # Agregamos un parámetro de tiempo falso al final de la URL para evitar que Google guarde caché
    url_fresh = f"{url}&cache_buster={time.time()}"
    df = pd.read_csv(url_fresh)
    
    # Mostrar métricas
    cols = st.columns(3)
    for i, col in enumerate(df.columns):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{col}</div>
                    <div class="metric-value">{df.iloc[0, i]}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.caption(f"Última actualización leída: {time.strftime('%H:%M:%S')}")

except Exception as e:
    st.error("No se pudieron cargar los datos. Verifica la publicación del Sheet.")

# Mapa
st.subheader("📍 Mapa de Afectaciones")
# El timestamp en la URL del mapa ya lo tenías, eso está bien para refrescar el mapa
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
