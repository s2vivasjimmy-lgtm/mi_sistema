import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 10px; }
    .card-title { font-size: 11px; text-transform: uppercase; color: #b0b3b8; }
    .card-value { font-size: 20px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_datos.csv"

def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCiones Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_DATOS, index=False)

inicializar_datos()

# --- INTERFAZ PRINCIPAL ---
if os.path.exists("logo_institucional.jpg"):
    st.image("logo_institucional.jpg", use_container_width=True)

st.markdown('<h2 style="color:white; text-align:center;">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2>', unsafe_allow_html=True)

# --- VENTANA DE ACCESO ADMINISTRATIVO (EN EL CENTRO) ---
with st.expander("🔐 Panel Administrativo"):
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if user == "Admin" and pwd == "diges12..":
            st.session_state.admin_logueado = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# --- DATOS ---
df = pd.read_csv(ARCHIVO_DATOS, dtype=str)
iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}

cols = st.columns(4)
for i, col in enumerate(df.columns):
    with cols[i % 4]:
        st.markdown(f"""
            <div class="compact-card">
                <div class="card-title">{iconos.get(col, '📊')} {col}</div>
                <div class="card-value">{df[col].iloc[0]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- MAPA ---
st.subheader("📍 Mapa de Afectaciones")
st.components.v1.html("""
    <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" width="100%" height="500" frameborder="0" style="border:0;" allowfullscreen></iframe>
""", height=510)

# --- PANEL DE EDICIÓN (VISIBLE SOLO SI ESTÁ LOGUEADO) ---
if st.session_state.get("admin_logueado", False):
    st.markdown("---")
    st.header("📝 Panel de Edición de Registros")
    df_actual = pd.read_csv(ARCHIVO_DATOS, dtype=str)
    df_editado = st.data_editor(df_actual, use_container_width=True)
    
    if st.button("Guardar Cambios"):
        df_editado.to_csv(ARCHIVO_DATOS, index=False)
        st.success("¡Datos guardados correctamente!")
        st.rerun()
