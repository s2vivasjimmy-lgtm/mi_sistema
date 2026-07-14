import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilos CSS para círculos
st.markdown("""
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px;
        padding: 20px;
    }
    .circle-card {
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 3px solid var(--border-color);
    }
    .icon-box { font-size: 40px; margin-right: 20px; }
    .content-box { text-align: left; }
    .metric-title { color: #555; font-size: 12px; text-transform: uppercase; font-weight: bold; }
    .metric-value { color: #333; font-size: 28px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Monitoreo de Gestión de Salud")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Diccionario de configuración para colores e íconos
config = {
    "ATENCIONES": {"color": "#FF6B6B", "icon": "🏥"},
    "ALTAS MÉDICAS": {"color": "#4ECDC4", "icon": "✅"},
    "FALLECIDOS": {"color": "#2D3436", "icon": "🕊️"},
    "TRASLADOS": {"color": "#FFE66D", "icon": "🚑"},
    "CAMAS OCUPADAS": {"color": "#FF9F1C", "icon": "🛏️"},
    "CAMAS DISPONIBLES": {"color": "#2ECC71", "icon": "🔋"},
    "HOSPITALIZACIONES": {"color": "#3498DB", "icon": "🩺"},
    "INMUNIZACIONES": {"color": "#9B59B6", "icon": "💉"},
    "INTERVENCIONES Q.": {"color": "#E74C3C", "icon": "✂️"}
}

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    
    for col in df.columns:
        # Buscamos configuración, si no existe usamos gris por defecto
        c = config.get(col, {"color": "#BDC3C7", "icon": "📊"})
        
        st.markdown(f"""
            <div class="circle-card" style="--border-color: {c['color']}">
                <div class="icon-box">{c['icon']}</div>
                <div class="content-box">
                    <div class="metric-title">{col}</div>
                    <div class="metric-value">{df[col].iloc[0]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption(f"🕒 Última actualización: {time.strftime('%H:%M:%S')}")

except Exception:
    st.error("Error al cargar los datos.")

# Mapa
st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
