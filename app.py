import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide")

# --- CSS CON TAMAÑOS AUMENTADOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Tarjetas más grandes y legibles */
    .compact-card { background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 2px solid #31333f; color: white; margin-bottom: 20px; }
    .card-title { font-size: 18px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 10px; }
    .card-value { font-size: 45px; font-weight: 800; color: #ffffff; }
    
    .floating-btn-container { position: fixed; top: 20px; right: 20px; z-index: 9999; }
    
    /* Título grande y con marquesina */
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 30px; }
    .marquee-text { display: inline-block; font-size: 40px; animation: marquee 20s linear infinite; }
    @keyframes marquee { 
        0% { transform: translate(100%, 0); } 
        100% { transform: translate(-100%, 0); } 
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_datos.csv"

# --- INICIALIZACIÓN ---
if "admin_logueado" not in st.session_state:
    st.session_state.admin_logueado = False

def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_DATOS, index=False)

inicializar_datos()

# --- LÓGICA DE VISTAS ---
if st.session_state.admin_logueado:
    st.header("📝 Panel de Edición de Registros")
    df_actual = pd.read_csv(ARCHIVO_DATOS, dtype=str)
    df_editado = st.data_editor(df_actual, use_container_width=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("💾 Guardar y Volver"):
            df_editado.to_csv(ARCHIVO_DATOS, index=False)
            st.rerun()
    with col2:
        if st.button("❌ Cerrar Sesión"):
            st.session_state.admin_logueado = False
            st.rerun()

else:
    with st.container():
        st.markdown('<div class="floating-btn-container">', unsafe_allow_html=True)
        with st.popover("🔐 ACCESO ADMIN"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user == "Admin" and pwd == "diges12..":
                    st.session_state.admin_logueado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        st.markdown('</div>', unsafe_allow_html=True)

    if os.path.exists("logo_institucional.jpg"):
        st.image("logo_institucional.jpg", use_container_width=True)

    st.markdown("""
        <div class="marquee-container">
            <h2 class="marquee-text" style="color:white;">
                AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA
            </h2>
        </div>
    """, unsafe_allow_html=True)

    df = pd.read_csv(ARCHIVO_DATOS, dtype=str)
    iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
    
    cols = st.columns(4)
    # Convertimos los items del df para poder iterar en grupos de 4
    columnas_lista = list(df.columns)
    for i in range(0, len(columnas_lista), 4):
        fila = st.columns(4)
        for j in range(4):
            if i + j < len(columnas_lista):
                col = columnas_lista[i + j]
                with fila[j]:
                    st.markdown(f"""
                        <div class="compact-card">
                            <div class="card-title">{iconos.get(col, '📊')} {col}</div>
                            <div class="card-value">{df[col].iloc[0]}</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.subheader("📍 Mapa de Afectaciones")
    st.components.v1.html("""
        <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" width="100%" height="500" frameborder="0" style="border:0;" allowfullscreen></iframe>
    """, height=510)
