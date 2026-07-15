import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
# expanded = Barra siempre abierta, datos seguros y siempre accesibles
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- CSS OPTIMIZADO ---
st.markdown("""
    <style>
    header { visibility: hidden !important; }
    .stApp { background-color: #0E1117 !important; }
    .gear-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    
    .block-container { padding-top: 1rem !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 20px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 2px; }
    .card-value { font-size: 20px; font-weight: 800; color: #ffffff; }
    
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 10px; }
    .marquee-text { display: inline-block; font-size: 30px; animation: marquee 15s linear infinite; margin: 0; color: #ffffff !important; }
    @keyframes marquee { 0% { transform: translate(100%, 0); } 100% { transform: translate(-100%, 0); } }
    
    .stTable { width: 100% !important; }
    .stTable table { width: 100% !important; border-collapse: collapse !important; background-color: #1a1c23 !important; }
    .stTable th, .stTable td { color: #ffffff !important; white-space: nowrap !important; padding: 10px 15px !important; border-bottom: 1px solid #31333f !important; }
    .stTable thead tr { background-color: #262730 !important; }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_RESUMEN = "mis_datos.csv"

# --- INICIALIZACIÓN ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

def inicializar_resumen():
    if not os.path.exists(ARCHIVO_RESUMEN):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)

inicializar_resumen()

# --- PANEL DE CONTROL FLOTANTE (Solo engranaje) ---
with st.container():
    st.markdown('<div class="gear-container">', unsafe_allow_html=True)
    with st.popover("⚙️"):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "Admin" and pwd == "diges12..":
                st.session_state.admin_logueado = True
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", 
                         ["Resumen General", "Hospitales de Campaña", 
                          "Campamentos Transitorios", "Puntos de Inmunización", "Daños de Infraestructura"])

# --- LÓGICA ---
if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_')}.csv"
    
    if not os.path.exists(archivo_a_editar):
        cols = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS"]
        pd.DataFrame(columns=cols).to_csv(archivo_a_editar, index=False)
        
    df_actual = pd.read_csv(archivo_a_editar, dtype=str)
    df_editado = st.data_editor(df_actual, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Guardar Cambios"):
        df_editado.to_csv(archivo_a_editar, index=False)
        st.success("Guardado exitosamente")
        st.rerun()
    if st.button("❌ Cerrar Sesión"):
        st.session_state.admin_logueado = False
        st.rerun()
else:
    if os.path.exists("logo_institucional.jpg"):
        st.image("logo_institucional.jpg", use_container_width=True)
    st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        cols = st.columns(4)
        for i, col_name in enumerate(df.columns):
            with cols[i % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
        
        st.subheader("📍 UBICACIONES EN TIEMPO REAL")
        st.components.v1.html("""<div id="map-container" style="width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;"><iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe></div>""", height=510)
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle): st.table(pd.read_csv(archivo_detalle, dtype=str))
        else: st.info("Aún no hay registros cargados.")
