import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- CSS OPTIMIZADO ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 15px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 2px; }
    .card-value { font-size: 20px; font-weight: 800; color: #ffffff; }
    .floating-btn-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

# --- MAPA DE ARCHIVOS POR CATEGORÍA ---
ARCHIVOS = {
    "Resumen General": "datos_resumen.csv",
    "Hospitales de Campaña": "datos_hospitales.csv",
    "Campamentos Transitorios": "datos_campamentos.csv",
    "Puntos de Inmunización": "datos_inmunizacion.csv"
}

def inicializar_archivos():
    # Inicializar Resumen
    if not os.path.exists(ARCHIVOS["Resumen General"]):
        pd.DataFrame({"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                      "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                      "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}).to_csv(ARCHIVOS["Resumen General"], index=False)
    
    # Inicializar Hospitales con tus columnas específicas
    if not os.path.exists(ARCHIVOS["Hospitales de Campaña"]):
        pd.DataFrame(columns=["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIDAD", "PAIS RESPONSABLE"]).to_csv(ARCHIVOS["Hospitales de Campaña"], index=False)

inicializar_archivos()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", list(ARCHIVOS.keys()))

# --- LÓGICA DE VISTAS ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_actual = ARCHIVOS[seleccion]
    df_actual = pd.read_csv(archivo_actual, dtype=str)
    
    # num_rows="dynamic" permite al usuario agregar o borrar filas fácilmente
    df_editado = st.data_editor(df_actual, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Guardar Cambios"):
        df_editado.to_csv(archivo_actual, index=False)
        st.success("Guardado correctamente")
        st.rerun()
    if st.button("❌ Cerrar Sesión"):
        st.session_state.admin_logueado = False
        st.rerun()
else:
    # Botón acceso admin
    with st.container():
        st.markdown('<div class="floating-btn-container">', unsafe_allow_html=True)
        with st.popover("⚙️"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user == "Admin" and pwd == "diges12..":
                    st.session_state.admin_logueado = True
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Vista General
    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVOS["Resumen General"], dtype=str)
        cols = st.columns(4)
        for i, col_name in enumerate(df.columns):
            with cols[i % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        df = pd.read_csv(ARCHIVOS[seleccion], dtype=str)
        st.table(df)
