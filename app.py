import streamlit as st
import pandas as pd
import time

# Configuración de la página
st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilos CSS Profesional
st.markdown("""
    <style>
    .metric-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }
    .metric-card {
        background-color: #161a22;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #2d3446;
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        border-color: #4a90e2;
        transform: translateY(-5px);
    }
    .metric-title {
        color: #8892b0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
    }
    .metric-value {
        color: #e6edf3;
        font-size: 2.2rem;
        font-weight: 700;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

# URL directa de tu Google Sheet
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Carga de datos
try:
    # Añadimos timestamp para evitar caché
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    
    # Inicio del contenedor de tarjetas
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    
    # Ciclo para crear las tarjetas
    for col in df.columns:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{col}</div>
                <div class="metric-value">{df[col].iloc[0]}</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.caption(f"🕒 Última actualización: {time.strftime('%H:%M:%S')}, {time.strftime('%d/%m/%Y')}")

except Exception as e:
    st.error("Error al conectar con la base de datos. Asegúrate de que el archivo esté publicado.")

# Mapa
st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
