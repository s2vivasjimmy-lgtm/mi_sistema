import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="collapsed")

# --- CSS OPTIMIZADO ---
st.markdown("""
    <style>
    /* Eliminar espacio superior */
    .block-container { padding-top: 0rem !important; }
    
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Tarjetas compactas */
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 11px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 2px; }
    .card-value { font-size: 20px; font-weight: 800; color: #ffffff; }
    
    .floating-btn-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    
    /* Marquesina ajustada */
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 10px; }
    .marquee-text { display: inline-block; font-size: 24px; animation: marquee 15s linear infinite; margin: 0; }
    @keyframes marquee { 0% { transform: translate(100%, 0); } 100% { transform: translate(-100%, 0); } }
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
    st.header("📝 Panel de Edición")
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
    # Botón de acceso
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

    # Logo
    if os.path.exists("logo_institucional.jpg"):
        st.image("logo_institucional.jpg", use_container_width=True)

    # Título marquesina
    st.markdown("""
        <div class="marquee-container">
            <h2 class="marquee-text" style="color:white;">
                AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA
            </h2>
        </div>
    """, unsafe_allow_html=True)

    # Grid de tarjetas
    df = pd.read_csv(ARCHIVO_DATOS, dtype=str)
    iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
    
    cols = st.columns(4)
    columnas_lista = list(df.columns)
    for i in range(len(columnas_lista)):
        with cols[i % 4]:
            st.markdown(f"""
                <div class="compact-card">
                    <div class="card-title">{iconos.get(columnas_lista[i], '📊')} {columnas_lista[i]}</div>
                    <div class="card-value">{df[columnas_lista[i]].iloc[0]}</div>
                </div>
            """, unsafe_allow_html=True)

    # Mapa incrustado (solo para visualización rápida)
    st.components.v1.html("""
        <iframe 
            src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" 
            width="100%" 
            height="600" 
            frameborder="0" 
            style="border:0;">
        </iframe>
    """, height=610)
    
    # Botón de enlace corregido para abrir la vista completa de Google My Maps
    st.link_button("🌐 ABRIR MAPA EN PANTALLA COMPLETA", "https://www.google.com/maps/d/viewer?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg")
