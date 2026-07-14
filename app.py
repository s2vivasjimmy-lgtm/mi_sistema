import streamlit as st

st.set_page_config(page_title="Sala Situacional", layout="wide")

# Estilo para el modo oscuro profesional
st.markdown("""
    <style>
    .stApp {background-color: #0e1117;}
    .metric-card {
        background-color: #1c202a;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #31333F;
    }
    .metric-title {color: #808495; font-size: 14px; text-transform: uppercase;}
    .metric-value {color: #ffffff; font-size: 28px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# SIDEBAR (Menú lateral)
with st.sidebar:
   st.image("https://i.ibb.co/6wXbKqZ/escudo-salud-fanb.jpg", width=120)
    st.title("SALA SITUACIONAL")
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

# Tus datos en tarjetas
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
