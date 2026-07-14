import streamlit as st
import time

# Configuración de página
st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilo CSS
st.markdown("""
    <style>
    .stApp {background-color: #0e1117;}
    .metric-card {
        background-color: #1c202a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #31333F;
        margin-bottom: 10px;
    }
    .metric-title {color: #808495; font-size: 14px; text-transform: uppercase;}
    .metric-value {color: #ffffff; font-size: 28px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# SIDEBAR CON PANEL DE EDICIÓN
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Coat_of_arms_of_Venezuela.svg/512px-Coat_of_arms_of_Venezuela.svg.png", width=120)
    st.markdown("## SALA SITUACIONAL")
    st.write("Dirección General de Salud")
    st.write("---")
    
    st.write("🛠️ ADMINISTRACIÓN")
    with st.expander("Actualizar Estadísticas"):
        v1 = st.text_input("Atenciones", value="1.240")
        v2 = st.text_input("Altas Médicas", value="950")
        v3 = st.text_input("Fallecidos", value="12")
        v4 = st.text_input("Traslados", value="45")
        v5 = st.text_input("Camas Ocupadas", value="320")
        v6 = st.text_input("Camas Disponibles", value="85")
        v7 = st.text_input("Hospitalizaciones", value="210")
        v8 = st.text_input("Inmunizaciones", value="540")
        v9 = st.text_input("Intervenciones Q.", value="35")

    st.write("---")
    st.button("Dashboard")
    st.button("Reportes")
    st.button("Gestión Usuarios")
    st.button("Tablas del Sistema")

# DASHBOARD
st.title("🛡️ Monitoreo de Gestión de Salud")

datos = [
    ("Atenciones", v1), ("Altas Médicas", v2), ("Fallecidos", v3),
    ("Traslados", v4), ("Camas Ocupadas", v5), ("Camas Disponibles", v6),
    ("Hospitalizaciones", v7), ("Inmunizaciones", v8), ("Intervenciones Q.", v9)
]

for i in range(0, 9, 3):
    cols = st.columns(3)
    for j in range(3):
        with cols[j]:
            titulo, valor = datos[i+j]
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{titulo}</div>
                    <div class="metric-value">{valor}</div>
                </div>
            """, unsafe_allow_html=True)

# MAPA
st.subheader("📍 Mapa de Afectaciones en Tiempo Real")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
