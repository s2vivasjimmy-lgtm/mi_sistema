import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# CSS optimizado para asegurar compatibilidad
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
    .icon-area { 
        font-size: 30px; 
        margin-right: 15px; 
        min-width: 40px; 
        text-align: center; 
    }
    .text-area { 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
    }
    .label-style { 
        color: #808495; 
        font-size: 10px; 
        text-transform: uppercase; 
        font-weight: bold; 
        letter-spacing: 0.5px;
    }
    .value-style { 
        color: #ffffff; 
        font-size: 22px; 
        font-weight: bold; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Diccionario de iconos
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
    
    # Crear las tres columnas para el grid
    cols = st.columns(3)
    
    for i, col in enumerate(df.columns):
        icono = iconos.get(col, "📊")
        valor = df[col].iloc[0]
