import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# CSS exacto para mantener tu interfaz original
st.markdown("""
    <style>
    .card-item {
        background-color: #1c202a;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #31333F;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        height: 75px;
    }
    .icon-area { font-size: 28px; margin-right: 15px; min-width: 40px; color: #4a90e2; text-align: center; }
    .text-area { display: flex; flex-direction: column; justify-content: center; }
    .label-style { color: #808495; font-size: 10px; text-transform: uppercase; font-weight: bold; }
    .value-style { color: #ffffff; font-size: 22px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Diccionario de emojis (más confiables en columnas de Streamlit)
iconos = {
    "ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀",
    "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌",
    "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"
}

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    cols = st.columns(3)
    
    for i, col in enumerate(df.columns):
        icono = iconos.get(col, "📊")
        valor = df[col].iloc[0]
        with cols[i % 3]:
            st.markdown(f"""
                <div class="card-item">
                    <div class="icon-area">{icono}</div>
                    <div class="text-area">
                        <div class="label-style">{col}</div>
                        <div class="value-style">{valor}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
except:
    st.error("Error al cargar datos.")

st.subheader("📍 Mapa de Afectaciones")

# Mapa con botón de pantalla completa
mapa_html = f"""
<div style="position: relative; width: 100%; height: 550px;">
    <button onclick="document.getElementById('myMap').requestFullscreen()" 
            style="position: absolute; top: 10px; right: 10px; z-index: 999; padding: 10px; cursor: pointer; background: white; border-radius: 5px; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ⛶ Pantalla Completa
    </button>
    <iframe id="myMap" src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" 
            width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
</div>
"""
st.components.v1.html(mapa_html, height=560)
