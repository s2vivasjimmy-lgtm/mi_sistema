import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# CSS ajustado para mayor claridad y uniformidad
st.markdown("""
    <style>
    .card-item {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #464e5f;
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        height: 80px;
    }
    .icon-area { font-size: 30px; margin-right: 20px; color: #ffffff; }
    .text-area { display: flex; flex-direction: column; justify-content: center; }
    .label-style { color: #b0b3b8; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; }
    .value-style { color: #ffffff; font-size: 26px; font-weight: 800; }
    
    /* Animación del Título */
    .moving-title {
        overflow: hidden;
        white-space: nowrap;
        font-size: 2.5rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 30px;
        background-color: transparent;
        border-bottom: 2px solid #4a90e2;
        padding-bottom: 10px;
    }
    .moving-title span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 20s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
""", unsafe_allow_html=True)

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
