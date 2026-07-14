import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="collapsed")

# --- CSS OPTIMIZADO CON TAMAÑOS GRANDES ---
st.markdown("""
    <style>
    /* Eliminar espacio superior */
    .block-container { padding-top: 0rem !important; }
    
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Tarjetas compactas con fuentes grandes para visibilidad a distancia */
    .compact-card { background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 2px solid #31333f; color: white; margin-bottom: 15px; text-align: center; }
    .card-title { font-size: 20px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 10px; }
    .card-value { font-size: 45px; font-weight: 900; color: #ffffff; }
    
    .floating-btn-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    
    /* Marquesina */
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 20px; }
    .marquee-text { display: inline-block; font-size: 40px; animation: marquee 15s linear infinite; margin: 0; color: white; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(100%, 0); } 100% { transform: translate(-100%, 0); } }
    
    /* Overlay para pantalla completa */
    .fullscreen-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #0E1117; z-index: 99999; padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_datos.csv"

# --- INICIALIZACIÓN ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False
if "mostrar_mapa" not in st.session_state: st.session_state.mostrar_mapa = False

def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_DATOS, index=False)

inicializar_datos()

# --- LÓGICA DE VISTAS ---

if st.session_state.mostrar_mapa:
    st.markdown('<div class="fullscreen-overlay">', unsafe_allow_html=True)
    if st.button("⬅️ CERRAR MAPA Y VOLVER"):
        st.session_state.mostrar_mapa = False
        st.rerun()
    st.components.v1.html("""
        <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" 
        width="100%" height="90%" frameborder="0" style="border:0;"></iframe>
    """, height=800)
    st.markdown('</div>', unsafe_allow_html=True)

else:
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

        if os.path.exists("logo_institucional.jpg"):
            st.image("logo_institucional.jpg", use_container_width=True)
        
        st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

        df = pd.read_csv(ARCHIVO_DATOS, dtype=str)
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        cols = st.columns(4)
        for i, col_name in enumerate(df.columns):
            with cols[i % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)

        st.subheader("📍 Ubicaciones en Tiempo Real")
        if st.button("⛶ ABRIR MAPA EN PANTALLA COMPLETA"):
            st.session_state.mostrar_mapa = True
            st.rerun()
        
        st.components.v1.html("""
            <div style="width: 100%; height: 500px; border: 2px solid #31333f; border-radius: 12px; overflow: hidden;">
                <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
            </div>
        """, height=510)
