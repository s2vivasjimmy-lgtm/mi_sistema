import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# 1. Fuerza el fondo oscuro globalmente mediante CSS inyectado al inicio
st.markdown("""
    <style>
    /* Forzar fondo oscuro en toda la app */
    .stApp { background-color: #0E1117 !important; }
    
    /* Ocultar elementos */
    #MainMenu, footer, header { visibility: hidden !important; }
    
    .cintillo-container { width: 100%; text-align: center; margin-bottom: 20px; }
    .cintillo-container img { max-height: 100px; width: auto !important; max-width: 100%; }
    
    /* Animación del título */
    .moving-title { width: 100%; overflow: hidden; white-space: nowrap; font-size: 2rem; font-weight: 900; color: #ffffff; margin-bottom: 20px; border-bottom: 2px solid #4a90e2; padding: 10px 0; }
    .moving-title span { display: inline-block; padding-left: 100%; animation: marquee 15s linear infinite; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    </style>
""", unsafe_allow_html=True)

# 2. Carga del cintillo
ruta_logo = "logo_institucional.jpg"
if os.path.exists(ruta_logo):
    st.markdown('<div class="cintillo-container">', unsafe_allow_html=True)
    st.image(ruta_logo)
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Título con movimiento
st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</span></div>', unsafe_allow_html=True)

# 4. Datos con estilo aplicado directamente en el componente para mayor estabilidad
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"
iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    cols = st.columns(3)
    for i, col in enumerate(df.columns):
        icono = iconos.get(col, "📊")
        valor = df[col].iloc[0]
        with cols[i % 3]:
            # Estilos aplicados directamente en el div (estilo inline) para evitar fallos de renderizado
            st.markdown(f"""
                <div style="background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #464e5f; display: flex; align-items: center; margin-bottom: 15px; color: white;">
                    <div style="font-size: 24px; margin-right: 15px;">{icono}</div>
                    <div>
                        <div style="font-size: 10px; text-transform: uppercase; color: #b0b3b8;">{col}</div>
                        <div style="font-size: 20px; font-weight: bold;">{valor}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
except:
    st.error("Error al cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")

# 5. Mapa con botón de pantalla completa más robusto
mapa_html = """
<div id="map-wrapper" style="width: 100%; height: 500px; background: #0E1117;">
    <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0" style="border:0;"></iframe>
</div>
"""
st.components.v1.html(mapa_html, height=500)
