import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# CSS para las tarjetas, el cintillo y la nueva animación del título
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
    .cintillo-wrapper { background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
    
    /* Animación del Título */
    .moving-title {
        overflow: hidden;
        white-space: nowrap;
        font-size: 2.2rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 20px;
        background-color: #0e1117;
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
    </style>
""", unsafe_allow_html=True)

# Título con movimiento aplicado
st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LAGUAIRA</span></div>', unsafe_allow_html=True)

# Cintillo robusto
try:
    st.markdown('<div class="cintillo-wrapper">', unsafe_allow_html=True)
    st.image("images/logo_institucional.png", width=1000)
    st.markdown('</div>', unsafe_allow_html=True)
except Exception:
    st.warning("El logo institucional no se pudo cargar. Verifica que el archivo esté en la carpeta /images")

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
except:
    st.error("Error al cargar los datos desde la hoja de cálculo.")

st.subheader("📍 Mapa de Afectaciones")

mapa_html = """
<div id="map-wrapper" style="position: relative; width: 100%; height: 550px;">
    <button id="fs-btn" style="position: absolute; top: 10px; right: 10px; z-index: 999; padding: 10px; cursor: pointer; background: white; border-radius: 5px; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ⛶ Pantalla Completa
    </button>
    <iframe id="myMap" src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
</div>
<script>
    const btn = document.getElementById('fs-btn');
    const wrapper = document.getElementById('map-wrapper');
    btn.onclick = function() { if (wrapper.requestFullscreen) { wrapper.requestFullscreen(); } };
</script>
"""
st.components.v1.html(mapa_html, height=560)
