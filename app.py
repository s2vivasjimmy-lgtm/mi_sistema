import streamlit as st
import folium
from streamlit_folium import st_folium

# Configuración de página
st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilo CSS para el modo oscuro profesional
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

# SIDEBAR
with st.sidebar:
    # URL directa del escudo
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Coat_of_arms_of_Venezuela.svg/512px-Coat_of_arms_of_Venezuela.svg.png", width=120)
    st.markdown("## SALA SITUACIONAL")
    st.write("Dirección General de Salud")
    st.write("---")
    st.write("PRINCIPAL")
    st.button("Dashboard")
    st.button("Reportes")
    st.write("ADMINISTRACIÓN")
    st.button("Gestión Usuarios")
    st.button("Tablas del Sistema")

# DASHBOARD
st.title("🛡️ Monitoreo de Gestión de Salud")
st.caption("Panel de control en tiempo real — Sala Situacional")

# Datos
datos = [
    ("Atenciones", "1.240"), ("Altas Médicas", "950"), ("Fallecidos", "12"),
    ("Traslados", "45"), ("Camas Ocupadas", "320"), ("Camas Disponibles", "85"),
    ("Hospitalizaciones", "210"), ("Inmunizaciones", "540"), ("Intervenciones Q.", "35")
]

# Crear las filas de tarjetas
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

# MAPA INTERACTIVO
st.subheader("📍 Mapa de Afectaciones")
st.caption("Datos en tiempo real")

# Crear el mapa con estilo oscuro
m = folium.Map(location=[8.0, -66.0], zoom_start=6, tiles="CartoDB dark_matter")

# Añadir punto de ejemplo
folium.Marker(
    [10.48, -66.87], 
    popup="Zona de Afectación",
    icon=folium.Icon(color="red", icon="info-sign")
).add_to(m)

# Mostrar mapa
st_folium(m, width=1200, height=400)
