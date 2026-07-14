import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# CSS adaptable (responsive) para todo tipo de pantallas y dispositivos
st.markdown("""
    <style>
    /* Ocultar elementos de la interfaz de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Eliminar el espacio superior por defecto de Streamlit */
    .block-container { 
        padding-top: 0rem; 
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Contenedor del cintillo adaptable */
    .cintillo-container {
        width: 100%;
        margin-bottom: 20px;
        text-align: center;
        overflow: hidden;
    }
    
    /* Control de altura del logo (delgado y centrado) */
    .cintillo-container img {
        max-height: 110px; /* Evita que se vea muy grueso */
        width: auto !important;
        max-width: 100%;
        object-fit: contain;
    }
    
    /* Tarjetas adaptables */
    .card-item {
        background-color: #262730;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #464e5f;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        height: 80px;
    }
    .icon-area { font-size: 28px; margin-right: 15px; color: #ffffff; }
    .text-area { display: flex; flex-direction: column; justify-content: center; }
    .label-style { color: #b0b3b8; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; }
    .value-style { color: #ffffff; font-size: 24px; font-weight: 800; }
    
    /* Título con movimiento adaptable */
    .moving-title {
        overflow: hidden;
        white-space: nowrap;
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 20px;
        border-bottom: 2px solid #4a90e2;
        padding-bottom: 10px;
        width: 100%;
    }
    .moving-title span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }

    /* REGLAS ESPECIALES PARA DISPOSITIVOS MÓVILES (Pantallas menores a 768px) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        .cintillo-container img {
            max-height: 65px; /* Logo más delgado en móviles para que no ocupe toda la pantalla */
        }
        .moving-title {
            font-size: 1.2rem; /* Texto del título más pequeño para que sea legible en celulares */
            margin-bottom: 15px;
        }
        .card-item {
            height: auto; /* Permite que la tarjeta se expanda verticalmente si el texto es largo */
            padding: 12px;
            margin-bottom: 10px;
        }
        .icon-area {
            font-size: 22px;
            margin-right: 10px;
        }
        .value-style {
            font-size: 18px;
        }
        .label-style {
            font-size: 9px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Carga del cintillo controlado por contenedor flexible
ruta_logo = "logo_institucional.jpg"
if os.path.exists(ruta_logo):
    st.markdown('<div class="cintillo-container">', unsafe_allow_html=True)
    st.image(ruta_logo)
    st.markdown('</div>', unsafe_allow_html=True)

# Título con movimiento
st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</span></div>', unsafe_allow_html=True)

# Cargamos los datos
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

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
except Exception:
    st.error("Error al cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")

# Mapa responsivo usando porcentaje en la altura del contenedor principal
mapa_html = """
<div id="map-wrapper" style="position: relative; width: 100%; height: 100%; min-height: 400px; max-height: 550px;">
    <button id="fs-btn" style="position: absolute; top: 10px; right: 10px; z-index: 999; padding: 10px; cursor: pointer; background: white; border-radius: 5px; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3); font-weight: bold; font-size: 12px;">
        ⛶ Pantalla Completa
    </button>
    <iframe id="myMap" src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="480" frameborder="0" style="border:0; border-radius: 8px;"></iframe>
</div>
<script>
    const btn = document.getElementById('fs-btn');
    const wrapper = document.getElementById('map-wrapper');
    btn.onclick = function() { if (wrapper.requestFullscreen) { wrapper.requestFullscreen(); } };
</script>
"""
st.components.v1.html(mapa_html, height=500)
