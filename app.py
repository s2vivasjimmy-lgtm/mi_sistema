import streamlit as st
import pandas as pd
import os
import base64
import io
import plotly.graph_objects as go
from github import Github

# --- CONFIGURACIÓN ---
HOSPITALES_CONFIG = {
    "hosp_nac1": {"nombre": "HOSP. DE CAMPAÑA NACIONAL 01", "tipo": "HOSP. DE CAMPAÑA NACIONALES", "pwd": "clave1"},
    "hosp_ext1": {"nombre": "HOSP. DE CAMPAÑA INTERNACIONAL 01", "tipo": "HOSP. DE CAMPAÑA INTERNACIONALES", "pwd": "clave2"}
}
ARCHIVO_RESUMEN = "mis_datos.csv"

st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- LÓGICA DE URL ---
query_params = st.query_params
es_acceso_hospital = query_params.get("page") == "hosp"

# --- FUNCIONES ---
def convertir_df_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

def guardar_en_github(archivo_local):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["GITHUB_REPO"] 
        g = Github(token)
        repo = g.get_repo(repo_name)
        with open(archivo_local, 'r', encoding='utf-8') as file:
            contenido = file.read()
        try:
            contents = repo.get_contents(archivo_local)
            repo.update_file(contents.path, "Actualización", contenido, contents.sha)
        except:
            repo.create_file(archivo_local, "Creación", contenido)
        return True
    except: return False

def actualizar_totales_maestro():
    if os.path.exists(ARCHIVO_RESUMEN):
        df = pd.read_csv(ARCHIVO_RESUMEN)
        for h_id, info in HOSPITALES_CONFIG.items():
            if os.path.exists(f"{h_id}.csv"):
                df_h = pd.read_csv(f"{h_id}.csv")
                val = int(df_h['ATENCIONES'].iloc[0])
                df.at[0, info["tipo"]] = val
        df.to_csv(ARCHIVO_RESUMEN, index=False)
        guardar_en_github(ARCHIVO_RESUMEN)

# --- CSS ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }
    .compact-card { background-color: #1a1c23; padding: 4px; border-radius: 4px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
    .strat-card { background-color: #2b3a4a; padding: 10px; border-radius: 8px; border-left: 5px solid #00d2ff; text-align: center; margin-bottom: 15px; }
    .card-title { font-size: 17px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 5px; }
    .card-value { font-size: 30px; font-weight: 800; color: #ffffff; }
    .strat-title { font-size: 12px; text-transform: uppercase; color: #e0e0e0; font-weight: bold; }
    .strat-value { font-size: 24px; font-weight: 900; color: #ffffff; }
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 20px; border-top: 2px solid #31333f; border-bottom: 2px solid #31333f; padding: 0px 0; }
    .marquee-text { display: inline-block; font-size: 20px; animation: marquee 15s linear infinite; margin: 0; color: #ffffff !important; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(-100%, 0); } 100% { transform: translate(100%, 0); } }
    .logo-custom { width: 100%; height: 200px; object-fit: contain; display: block; margin-left: auto; margin-right: auto; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO Y SIDEBAR ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False
if "hosp_logueado" not in st.session_state: st.session_state.hosp_logueado = False

with st.sidebar:
    st.header("📋 Registros")
    # Login Hospitales
    if es_acceso_hospital and not st.session_state.hosp_logueado:
        st.subheader("🏥 Ingreso Hospitales")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user in HOSPITALES_CONFIG and pwd == HOSPITALES_CONFIG[user]["pwd"]:
                st.session_state.hosp_logueado = True
                st.session_state.hosp_id = user
                st.rerun()
    # Login Admin
    elif not st.session_state.admin_logueado and not st.session_state.hosp_logueado and not es_acceso_hospital:
        with st.popover("⚙️ Acceso Admin"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user == "Admin" and pwd == "diges12..":
                    st.session_state.admin_logueado = True
                    st.rerun()

    seleccion = st.radio("Seleccionar categoría:", ["Resumen General", "Hospitales de Campaña", "Campamentos Transitorios", "Puntos de Inmunización", "Daños de Infraestructura"])
    
    if (st.session_state.admin_logueado or st.session_state.hosp_logueado) and st.button("❌ Cerrar Sesión"):
        st.session_state.admin_logueado = False
        st.session_state.hosp_logueado = False
        st.rerun()

# --- LÓGICA PRINCIPAL ---
if st.session_state.hosp_logueado:
    hosp = HOSPITALES_CONFIG[st.session_state.hosp_id]
    st.title(f"🏥 Gestión: {hosp['nombre']}")
    archivo_h = f"{st.session_state.hosp_id}.csv"
    if not os.path.exists(archivo_h): pd.DataFrame({'ATENCIONES': [0]}).to_csv(archivo_h, index=False)
    val = st.number_input("Carga de Atenciones:", value=int(pd.read_csv(archivo_h)['ATENCIONES'].iloc[0]))
    if st.button("💾 Guardar y Actualizar"):
        pd.DataFrame({'ATENCIONES': [val]}).to_csv(archivo_h, index=False)
        actualizar_totales_maestro()
        st.success("Guardado correctamente.")

elif st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_')}.csv"
    if not os.path.exists(archivo_a_editar): pd.DataFrame().to_csv(archivo_a_editar, index=False)
    df_actual = pd.read_csv(archivo_a_editar, dtype=str)
    df_editado = st.data_editor(df_actual, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Guardar Cambios"):
        df_editado.to_csv(archivo_a_editar, index=False)
        guardar_en_github(archivo_a_editar); st.success("Guardado.")

else:
    if os.path.exists("logo_institucional.jpg"):
        with open("logo_institucional.jpg", "rb") as f:
            st.markdown(f'<img src="data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}" class="logo-custom">', unsafe_allow_html=True)
    st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
        st.subheader("📊 ATENCIONES")
        strat_cols = ["SISTEMA DE SALUD TRADICIONAL", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES", "CAMP. TRANSITORIOS"]
        c_strat = st.columns(4)
        for i, campo in enumerate(strat_cols):
            val = df[campo].iloc[0] if campo in df.columns else "0"
            c_strat[i].markdown(f'<div class="strat-card"><div class="strat-title">{campo}</div><div class="strat-value">{val}</div></div>', unsafe_allow_html=True)
        
        st.subheader("🏥 RESUMEN OPERATIVO")
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        cols_mostrar = ["ATENCIONES", "ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INMUNIZACIONES", "INTERVENCIONES Q."]
        cols = st.columns(4)
        idx = 0
        for col_name in cols_mostrar:
            if col_name in df.columns:
                with cols[idx % 4]:
                    st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
                idx += 1
        
        st.subheader("📍 UBICACIONES EN TIEMPO REAL")
        st.components.v1.html("""
            <div id="map-container" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
                <button onclick="toggleFS()" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    ⛶ Pantalla Completa
                </button>
                <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
            </div>
            <script>
                function toggleFS() { var elem = document.getElementById("map-container"); if (!document.fullscreenElement) { elem.requestFullscreen(); } else { document.exitFullscreen(); } }
            </script>
        """, height=510)
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            df_d = pd.read_csv(archivo_detalle, dtype=str)
            st.dataframe(df_d, use_container_width=True)
            if st.button("📥 Descargar Excel"):
                st.download_button("Descargar Reporte", data=convertir_df_a_excel(df_d), file_name=f"{seleccion}.xlsx")
