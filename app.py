import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide")

# --- CSS MEJORADO: BOTÓN FLOTANTE Y PANEL ---
st.markdown("""
    <style>
    /* Estilos generales */
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    /* Tarjetas */
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 10px; }
    .card-title { font-size: 11px; text-transform: uppercase; color: #b0b3b8; }
    .card-value { font-size: 20px; font-weight: 700; }
    
    /* Botón flotante para asegurar acceso al menú */
    .btn-floating { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

# --- BOTÓN DE ACCESO ---
if st.button("☰ MENÚ DE REGISTROS"):
    st.session_state.menu_activo = not st.session_state.get("menu_activo", False)

ARCHIVO_DATOS = "mis_datos.csv"

def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_DATOS, index=False)

inicializar_datos()

def verificar_admin():
    if "admin_logueado" not in st.session_state:
        st.session_state.admin_logueado = False
    
    if not st.session_state.admin_logueado:
        st.subheader("🔐 Acceso Restringido - Panel Administrativo")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "Admin" and pwd == "diges12..":
                st.session_state.admin_logueado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
        return False
    return True

# --- NAVEGACIÓN ---
# Si el botón fue presionado, mostramos la radio box
if st.session_state.get("menu_activo", False):
    menu = st.sidebar.radio("Navegación", ["Vista de Comando", "Panel de Registros"])
else:
    menu = "Vista de Comando"

if menu == "Vista de Comando":
    if os.path.exists("logo_institucional.jpg"):
        st.image("logo_institucional.jpg", use_container_width=True)

    st.markdown('<h2 style="color:white; text-align:center;">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2>', unsafe_allow_html=True)

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

    st.subheader("📍 Mapa de Afectaciones")
    st.components.v1.html('<iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="300" frameborder="0"></iframe>', height=300)

else:
    if verificar_admin():
        st.header("📝 Panel de Edición de Registros")
        df_actual = pd.read_csv(ARCHIVO_DATOS, dtype=str)
        df_editado = st.data_editor(df_actual, use_container_width=True)
        
        if st.button("Guardar Cambios"):
            df_editado.to_csv(ARCHIVO_DATOS, index=False)
            st.success("¡Datos guardados con éxito!")
            st.rerun()
