import streamlit as st
import pandas as pd
import os
import base64
import io
import plotly.graph_objects as go
from github import Github

st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- FUNCIÓN PARA GENERAR EXCEL ---
def convertir_df_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

# --- CSS RESPONSIVE ---
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
    .strat-card { background-color: #2b3a4a; padding: 15px; border-radius: 8px; border-left: 5px solid #00d2ff; text-align: center; margin-bottom: 10px; }
    .card-title { font-size: 0.8rem; text-transform: uppercase; color: #b0b3b8; font-weight: bold; }
    .card-value { font-size: 1.2rem; font-weight: 800; color: #ffffff; }
    .strat-title { font-size: 0.7rem; text-transform: uppercase; color: #e0e0e0; font-weight: bold; }
    .strat-value { font-size: 1.1rem; font-weight: 900; color: #ffffff; }
    .logo-custom { width: 100%; max-height: 150px; object-fit: contain; display: block; margin: auto; margin-bottom: 15px; }
    .marquee-container { width: 100%; overflow: hidden; border-top: 2px solid #31333f; border-bottom: 2px solid #31333f; margin-bottom: 20px; }
    .marquee-text { font-size: 1rem; color: #ffffff; font-weight: bold; text-align: center; padding: 10px 0; }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_RESUMEN = "mis_datos.csv"

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
            repo.update_file(contents.path, "Actualización datos Puesto Comando", contenido, contents.sha)
        except:
            repo.create_file(archivo_local, "Creación datos Puesto Comando", contenido)
        return True
    except Exception as e:
        st.error(f"Error al respaldar en GitHub: {e}")
        return False

if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

def inicializar_resumen():
    if not os.path.exists(ARCHIVO_RESUMEN):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"],
                "SISTEMA DE SALUD TRADICIONAL": ["0"], "HOSP. DE CAMPAÑA NACIONALES": ["0"], 
                "HOSP. DE CAMPAÑA INTERNACIONALES": ["0"], "CAMP. TRANSITORIOS": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)
    else:
        df_mig = pd.read_csv(ARCHIVO_RESUMEN)
        mapeo = {"SALUD PÚBLICA": "SISTEMA DE SALUD TRADICIONAL", "HOSP. NACIONALES": "HOSP. DE CAMPAÑA NACIONALES", "HOSP. EXTRANJEROS": "HOSP. DE CAMPAÑA INTERNACIONALES"}
        if any(col in df_mig.columns for col in mapeo.keys()):
            df_mig.rename(columns=mapeo, inplace=True)
            df_mig.to_csv(ARCHIVO_RESUMEN, index=False)

inicializar_resumen()

with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", ["Resumen General", "Hospitales de Campaña", "Campamentos Transitorios", "Puntos de Inmunización", "Daños de Infraestructura"])

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_')}.csv"
    
    if seleccion == "Resumen General":
        cols_maestras = ["ATENCIONES", "ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INMUNIZACIONES", "INTERVENCIONES Q.", "SISTEMA DE SALUD TRADICIONAL", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES", "CAMP. TRANSITORIOS"]
    elif seleccion == "Campamentos Transitorios":
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "ATENCIONES", "NACIONALIAD"]
    elif seleccion == "Puntos de Inmunización":
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "TOTAL INMUNIZACIONES"]
    else:
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "PAIS RESPONSABLE", "ATENCIONES", "NACIONALIAD"]
    
    if not os.path.exists(archivo_a_editar):
        df_actual = pd.DataFrame(columns=cols_maestras)
        df_actual.to_csv(archivo_a_editar, index=False)
    else:
        df_actual = pd.read_csv(archivo_a_editar, dtype=str)
        for col in cols_maestras:
            if col not in df_actual.columns: df_actual[col] = "0"
            
    df_editado = st.data_editor(df_actual, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Guardar Cambios"):
        df_editado.to_csv(archivo_a_editar, index=False)
        if guardar_en_github(archivo_a_editar): st.success("Guardado en servidor.")
        st.rerun()
    if st.button("❌ Cerrar Sesión"):
        st.session_state.admin_logueado = False
        st.rerun()

else:
    with st.popover("⚙️"):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar") and user == "Admin" and pwd == "diges12..":
            st.session_state.admin_logueado = True
            st.rerun()
                
    if os.path.exists("logo_institucional.jpg"):
        with open("logo_institucional.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/jpeg;base64,{encoded_string}" class="logo-custom">', unsafe_allow_html=True)
            
    st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
        st.subheader("📊 ATENCIONES")
        
        strat_cols = ["SISTEMA DE SALUD TRADICIONAL", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES", "CAMP. TRANSITORIOS"]
        c_strat = st.columns(2)
        for i, campo in enumerate(strat_cols):
            val = df[campo].iloc[0] if campo in df.columns else "0"
            c_strat[i % 2].markdown(f'<div class="strat-card"><div class="strat-title">{campo}</div><div class="strat-value">{val}</div></div>', unsafe_allow_html=True)
        
        st.subheader("🏥 RESUMEN OPERATIVO")
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        cols_mostrar = ["ATENCIONES", "ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INMUNIZACIONES", "INTERVENCIONES Q."]
        cols = st.columns(2)
        for idx, col_name in enumerate(cols_mostrar):
            if col_name in df.columns:
                with cols[idx % 2]:
                    st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
        
        st.subheader("📍UBICACIONES EN TIEMPO REAL")
        st.components.v1.html("""
            <div id="map-container" style="position: relative; width: 100%; height: 350px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
                <button onclick="toggleFS()" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 5px 10px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold;">
                    ⛶ Pantalla Completa
                </button>
                <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
            </div>
            <script>
                function toggleFS() { var elem = document.getElementById("map-container"); if (!document.fullscreenElement) { elem.requestFullscreen(); } else { document.exitFullscreen(); } }
            </script>
        """, height=360)
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            df_detalle = pd.read_csv(archivo_detalle, dtype=str)
            if "NACIONALIAD" in df_detalle.columns and "ATENCIONES" in df_detalle.columns:
                df_stats = df_detalle.copy()
                df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].str.replace('.', '', regex=False), errors='coerce').fillna(0)
                resumen = df_stats.groupby(df_stats['NACIONALIAD'].str.upper().str.strip())['ATENCIONES'].sum()
                suma_nac = resumen.get('NACIONAL', 0)
                suma_ext = resumen.get('EXTRANJERO', 0) + resumen.get('ESTRANJERO', 0)
                cols = st.columns(2)
                cols[0].metric("Atenciones NACIONALES", f"{int(suma_nac):,}".replace(",", "."))
                cols[1].metric("Atenciones EXTRANJEROS", f"{int(suma_ext):,}".replace(",", "."))
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Aún no hay registros cargados.")
