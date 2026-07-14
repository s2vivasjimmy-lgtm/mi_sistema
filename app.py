import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# CSS optimizado para un aspecto profesional y limpio
st.markdown("""
    <style>
    /* Forzar fondo oscuro y limpiar interfaz */
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Contenedor del logo con fondo transparente y sombra sutil */
    .logo-wrapper { 
        display: flex; 
        justify-content: center; 
        margin-bottom: 25px; 
        padding: 10px;
    }
    .logo-wrapper img { 
        max-height: 90px; 
        width: auto !important; 
        background-color: transparent !important; 
        border-radius: 8px;
    }
    
    /* Título con diseño integrado */
    .moving-title { 
        width: 100%; overflow: hidden; white-space: nowrap; 
        font-size: 1.8rem; font-weight: 700; color: #ffffff; 
        margin-bottom: 30px; border-top: 1px solid #4a90e2; 
        border-bottom: 1px solid #4a90e2; padding: 12px 0; 
    }
    .moving-title span { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    </style>
""", unsafe_allow_html=True)

# Carga del cintillo (Logo)
ruta_logo = "logo_institucional.jpg"
if os.path.exists(ruta_logo):
    st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
    st.image(ruta_logo)
    st.markdown('</div>', unsafe_allow_html=True)

# Título con movimiento
st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</span></div>', unsafe_allow_html=True)

# Datos
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"
iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    cols = st.columns(3)
    for i, col in enumerate(df.columns):
        icono = iconos.get(col, "📊")
        valor = df[col].iloc[0]
        with cols[i % 3]:
            st.markdown(f"""
                <div style="background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #31333f; display: flex; align-items: center; margin-bottom: 20px; color: white;">
                    <div style="font-size: 28px; margin-right: 20px;">{icono}</div>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #b0b3b8; letter-spacing: 1px;">{col}</div>
                        <div style="font-size: 24px; font-weight: 800;">{valor}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except:
    st.error("Error al cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")

# Mapa con pantalla completa
mapa_html = """
<div id="map-container" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
    <button onclick="toggleFS()" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ⛶ Pantalla Completa
    </button>
    <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
</div>
<script>
    function toggleFS() {
        var elem = document.getElementById("map-container");
        if (!document.fullscreenElement) { elem.requestFullscreen(); } 
        else { document.exitFullscreen(); }
    }
</script>
"""
st.components.v1.html(mapa_html, height=510)
