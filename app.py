import streamlit as st
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #1c202a; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #31333F; 
        margin-bottom: 20px;
    } 
    .metric-title {
        color: #808495; 
        font-size: 14px; 
        text-transform: uppercase;
        margin-bottom: 5px;
    } 
    .metric-value {
        color: #ffffff; 
        font-size: 32px; 
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

# URL directa de tu Google Sheet publicada
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Carga de datos forzando refresco
try:
    # Añadimos un timestamp al final para evitar caché del navegador
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    
    # Mostrar métricas en columnas
    cols = st.columns(3)
    for i, col in enumerate(df.columns):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{col}</div>
                    <div class="metric-value">{df.iloc[0, i]}</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.write(f"🕒 *Última actualización: {time.strftime('%H:%M:%S')}, {time.strftime('%d/%m/%Y')}*")

except Exception as e:
    st.error("Error al conectar con la base de datos. Asegúrate de que el archivo esté publicado en la web.")

# Mapa
st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
