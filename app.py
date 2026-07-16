import streamlit as st
import pandas as pd
import os
from github import Github  # Nueva librería para el respaldo

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- CSS CON MOVIMIENTO Y ESTILO ---
st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
    .card-title { font-size: 25px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 5px; }
    .card-value { font-size: 35px; font-weight: 800; color: #ffffff; }
    
    /* MARQUEE (MOVIMIENTO) */
    .marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 20px; border-top: 2px solid #31333f; border-bottom: 2px solid #31333f; padding: 10px 0; }
    .marquee-text { display: inline-block; font-size: 30px; animation: marquee 15s linear infinite; margin: 0; color: #ffffff !important; font-weight: bold; }
    @keyframes marquee { 0% { transform: translate(100%, 0); } 100% { transform: translate(-100%, 0); } }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_RESUMEN = "mis_datos.csv"

# --- FUNCIÓN DE RESPALDO EN GITHUB ---
def guardar_en_github(archivo_local):
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
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

# --- INICIALIZACIÓN ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

def inicializar_resumen():
    if not os.path.exists(ARCHIVO_RESUMEN):
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)

inicializar_resumen()

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
        pd.DataFrame(columns=["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS"]).to_csv(archivo_a_editar, index=False)
        
    df_actual = pd.read_csv(archivo_a_editar, dtype=str)
    df_editado = st.data_editor(df_actual, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Guardar Cambios"):
        df_editado.to_csv(archivo_a_editar, index=False)
        if guardar_en_github(archivo_a_editar):
            st.success("Guardado en servidor y respaldado en GitHub correctamente.")
            st.rerun()
            
    if st.button("❌ Cerrar Sesión"):
        st.session_state.admin_logueado = False
        st.rerun()

else:
    # Login flotante
    with st.popover("⚙️"):
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "Admin" and pwd == "diges12..":
                st.session_state.admin_logueado = True
                st.rerun()

    # Logo y Marquee
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

        st.subheader("📍 UBICACIONES")
        st.components.v1.html("""
            <div id="map-container" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
                <button onclick="toggleFS()" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    ⛶ Pantalla Completa
                </button>
                <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
            </div>
            <script>
                function toggleFS() { 
                    var elem = document.getElementById("map-container"); 
                    if (!document.fullscreenElement) { 
                        elem.requestFullscreen(); 
                    } else { 
                        document.exitFullscreen(); 
                    } 
                }
            </script>
        """, height=510)
    
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            st.dataframe(pd.read_csv(archivo_detalle, dtype=str), use_container_width=True, hide_index=True)
        else:
            st.info("Aún no hay registros cargados.")
