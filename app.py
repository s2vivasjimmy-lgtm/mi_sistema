import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# CSS optimizado
st.markdown("""
    <style>
    .card-item {
        background-color: #1c202a !important;
        padding: 15px !important;
        border-radius: 12px !important;
        border: 1px solid #31333F !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: 20px !important;
        height: 75px !important;
    }
    .icon-area { 
        font-size: 32px !important; 
        margin-right: 15px !important; 
        min-width: 40px !important; 
        text-align: center !important; 
        display: inline-block !important;
    }
    .text-area { display: flex !important; flex-direction: column !important; justify-content: center !important; }
    .label-style { color: #808495 !important; font-size: 10px !important; text-transform: uppercase !important; font-weight: bold !important; }
    .value-style { color: #ffffff !important; font-size: 22px !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Diccionario de iconos
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
            # Forzamos el renderizado del icono como HTML estricto
            st.markdown(f"""
                <div class="card-item">
                    <span class="icon-area">{icono}</span>
                    <div class="text-area">
                        <div class="label-style">{col}</div>
                        <div class="value-style">{valor}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    st.caption(f"🕒 Última actualización: {time.strftime('%H:%M:%S')}")

except Exception as e:
    st.error("Error al cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
