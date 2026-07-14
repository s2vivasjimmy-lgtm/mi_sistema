import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# CSS para tarjetas compactas y elegantes
st.markdown("""
    <style>
    .card {
        background: #1c202a;
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #31333F;
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        height: 80px;
    }
    .icon { font-size: 35px; margin-right: 15px; min-width: 40px; text-align: center; }
    .text-box { display: flex; flex-direction: column; justify-content: center; }
    .title { color: #808495; font-size: 11px; text-transform: uppercase; font-weight: bold; }
    .value { color: #ffffff; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Íconos precisos por métrica
iconos = {
    "ATENCIONES": "📋",
    "ALTAS MÉDICAS": "✅",
    "FALLECIDOS": "🥀",
    "TRASLADOS": "🚑",
    "CAMAS OCUPADAS": "🛏️",
    "CAMAS DISPONIBLES": "🛌",
    "HOSPITALIZACIONES": "🏥",
    "INMUNIZACIONES": "💉",
    "INTERVENCIONES Q.": "🔪"
}

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    
    columnas = st.columns(3)
    
    for i, col in enumerate(df.columns):
        icono = iconos.get(col, "📊")
        valor = df[col].iloc[0]
        
        with columnas[i % 3]:
            st.markdown(f"""
                <div class="card">
                    <div class="icon">{icono}</div>
                    <div class="text-box">
                        <div class="title">{col}</div>
                        <div class="value">{valor}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    st.caption(f"🕒 Última actualización: {time.strftime('%H:%M:%S')}")

except Exception as e:
    st.error("No se pudieron cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
