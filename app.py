import streamlit as st
import pandas as pd
import os
import base64
import io
import plotly.graph_objects as go
from github import Github

st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

def convertir_df_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

# --- CSS OPTIMIZADO PARA PROYECCIÓN Y MÓVILES ---
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }

    /* Tarjetas de Atenciones */
    .strat-card { background-color: #2b3a4a; padding: 15px; border-radius: 8px; border-left: 5px solid #00d2ff; text-align: center; margin-bottom: 15px; height: 120px; }
    .strat-title { font-size: 14px; text-transform: uppercase; color: #e0e0e0; font-weight: bold; margin-bottom: 10px; }
    .strat-value { font-size: 30px; font-weight: 900; color: #ffffff; }

    /* Resumen Operativo */
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 4px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
    .card-title { font-size: 14px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 5px; }
    .card-value { font-size: 22px; font-weight: 800; color: #ffffff; }

    /* Totales y marquesina */
    .total-card { background-color: #1e2025; padding: 15px; border-radius: 8px; border: 2px solid #FFD700; text-align: center; margin-top: 10px; }
    .total-title { font-size: 18px; text-transform: uppercase; color: #FFD700; font-weight: bold; margin-bottom: 5px; }
    .total-value { font-size: 35px; font-weight: 900; color: #ffffff; }

    .marquee-container { width: 100%; overflow: hidden; background-color: #0E1117; padding: 10px 0; }
    .marquee-text { display: inline-block; white-space: nowrap; animation: marquee 15s linear infinite; color: #ffffff !important; font-weight: bold; font-size: 35px; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

    .logo-custom { width: 100%; height: 200px; object-fit: contain; display: block; margin-left: auto; margin-right: auto; margin-bottom: 10px; }

    /* Lógica Pantalla Completa iOS */
    .fullscreen-active { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; z-index: 999999 !important; margin: 0 !important; border-radius: 0 !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE MAPA COMPATIBLE CON IPHONE ---
def renderizar_mapa_ios(id_mapa, url):
    st.components.v1.html(f"""
    <div id="{id_mapa}" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden; background:#0E1117;">
        <button id="btn-{id_mapa}" style="position: absolute; top: 10px; right: 10px; z-index: 2000; padding: 10px; cursor: pointer; background: #FFD700; border: none; border-radius: 5px; font-weight: bold;">⛶ Expandir</button>
        <iframe src="{url}" width="100%" height="100%" frameborder="0" style="pointer-events: auto;"></iframe>
    </div>
    <script>
        const btn = document.getElementById('btn-{id_mapa}');
        const wrap = document.getElementById('{id_mapa}');
        btn.onclick = function() {{
            if (wrap.classList.contains('fullscreen-active')) {{
                wrap.classList.remove('fullscreen-active');
                btn.innerText = '⛶ Expandir';
            }} else {{
                wrap.classList.add('fullscreen-active');
                btn.innerText = '❌ Cerrar';
            }}
        }};
    </script>
    """, height=520)

# --- LÓGICA DE DATOS ---
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
        data = {"ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"], "HOSPITALIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)

inicializar_resumen()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", ["Resumen General", "Red Sanitaria Militar", "Hospitales de Campaña","Sistema de Salud Tradicional", "Campamentos Transitorios", "Inmunización", "Saneamiento Ambiental", "Programas de Salud", "Ruta Epidemiológica", "Daños de Infraestructura"])

# --- INTERFAZ PRINCIPAL ---
if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_')}.csv"
    
    if seleccion == "Resumen General":
        cols_maestras = ["ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INTERVENCIONES Q."]
    elif seleccion == "Red Sanitaria Militar":
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "ATENCIONES"]
    elif seleccion in ["Campamentos Transitorios", "Sistema de Salud Tradicional", "Inmunización", "Saneamiento Ambiental", "Programas de Salud"]:
        cols_maestras = ["Nº", "NOMBRE", "ATENCIONES"]
    elif seleccion == "Ruta Epidemiológica":
        cols_maestras = ["Nº", "GRUPO ETARIO", "SEXO", "PUNTO/RUTA", "DIÁNOSTICO", "ACCIONES", "RESULTADO", "NIVEL DE PRIORIDAD", "DIRECCIÓN DEL PACIENTE", "TELEFONO", "FECHA"]
    else:
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIAD", "PAIS RESPONSABLE", "ATENCIONES"]

    if not os.path.exists(archivo_a_editar):
        df_actual = pd.DataFrame(columns=cols_maestras)
    else:
        df_actual = pd.read_csv(archivo_a_editar, dtype=str)
        df_actual = df_actual.loc[:, df_actual.columns.isin(cols_maestras)]
        df_actual = df_actual.dropna(how='all')

    df_editado = st.data_editor(df_actual.reindex(columns=cols_maestras, fill_value="0"), use_container_width=True, num_rows="dynamic")

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
        if st.button("Ingresar"):
            if user == "Admin" and pwd == "diges12..":
                st.session_state.admin_logueado = True
                st.rerun()

if os.path.exists("logo_institucional.jpg"):
    try:
        with open("logo_institucional.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            st.markdown(f'<img src="data:image/jpeg;base64,{encoded_string}" class="logo-custom">', unsafe_allow_html=True)
    except: pass

st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

def formatear_numero(n):
    try: return f"{int(n):,}".replace(",", ".")
    except: return "0"

if seleccion == "Resumen General":
    st.subheader("🧑‍⚕️ ATENCIONES")
    categorias = {"Red Sanitaria Militar": "red_sanitaria_militar.csv", "Inmunización": "inmunización.csv", "Saneamiento Ambiental": "saneamiento_ambiental.csv", "Programas de Salud": "programas_de_salud.csv", "Sistema de Salud Tradicional": "sistema_de_salud_tradicional.csv", "Camp. Transitorios": "campamentos_transitorios.csv"}
    totales = {}
    total_general = 0
    for cat, archivo in categorias.items():
        val = 0
        if os.path.exists(archivo):
            df_cat = pd.read_csv(archivo, dtype=str)
            if "ATENCIONES" in df_cat.columns:
                vals = pd.to_numeric(df_cat["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                val = int(vals.sum())
        totales[cat] = val
        total_general += val
        
    hosp_nac = 0
    hosp_ext = 0
    archivo_hosp = "hospitales_de_campaña.csv"
    if os.path.exists(archivo_hosp):
        df_hosp = pd.read_csv(archivo_hosp, dtype=str)
        if "ATENCIONES" in df_hosp.columns and "NACIONALIAD" in df_hosp.columns:
            df_hosp["ATENCIONES"] = pd.to_numeric(df_hosp["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            resumen = df_hosp.groupby(df_hosp["NACIONALIAD"].astype(str).str.upper().str.strip())["ATENCIONES"].sum()
            hosp_nac = int(resumen.get("NACIONAL", 0))
            hosp_ext = int(resumen.get("EXTRANJERO", 0))

    totales["HOSP. DE CAMPAÑA NACIONALES"] = hosp_nac
    totales["HOSP. DE CAMPAÑA INTERNACIONALES"] = hosp_ext
    total_general += (hosp_nac + hosp_ext)

    orden_tarjetas = ["Red Sanitaria Militar", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES", "Sistema de Salud Tradicional", "Camp. Transitorios", "Inmunización", "Saneamiento Ambiental", "Programas de Salud"]
    
    for i in range(0, len(orden_tarjetas), 4):
        cols = st.columns(4)
        for j, cat in enumerate(orden_tarjetas[i:i+4]):
            with cols[j]:
                st.markdown(f'''<div class="strat-card"><div class="strat-title">{cat.upper()}</div><div class="strat-value">{formatear_numero(totales.get(cat, 0))}</div></div>''', unsafe_allow_html=True)

    st.markdown(f'''<div style="text-align: center; margin: 20px 0;"><div class="total-card" style="width: 50%; margin: auto;"><div class="total-title">TOTAL ATENCIONES</div><div class="total-value">{formatear_numero(total_general)}</div></div></div>''', unsafe_allow_html=True)

    st.subheader("🏥 RESUMEN OPERATIVO")
    df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
    iconos = {"ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INTERVENCIONES Q.": "🔪"}
    cols_mostrar = ["ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INTERVENCIONES Q."]
    
    cols = st.columns(4)
    idx = 0
    for col_name in cols_mostrar:
        if col_name in df.columns:
            with cols[idx % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
            idx += 1
            
    st.subheader("📍UBICACIONES EN TIEMPO REAL")
    renderizar_mapa_ios("map-general", "https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F")

elif seleccion == "Ruta Epidemiológica":
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = "ruta_epidemiológica.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.markdown("### 📍UBICACIÓN DEL PACIENTE")
    renderizar_mapa_ios("map-ruta", "https://www.google.com/maps/d/embed?mid=1yl45t_HdDytdAAzsaOcMJzM3ICa5bPk")

elif seleccion in ["Red Sanitaria Militar", "Inmunización", "Saneamiento Ambiental", "Campamentos Transitorios", "Sistema de Salud Tradicional", "Programas de Salud"]:
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        if "ATENCIONES" in df_detalle.columns:
            total_atenciones = pd.to_numeric(df_detalle["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum()
            st.markdown(f'''<div style="text-align: center; margin-bottom: 20px;"><div class="total-card" style="width: 300px; margin: auto;"><div class="total-title">TOTAL DE ATENCIONES</div><div class="total-value">{formatear_numero(total_atenciones)}</div></div></div>''', unsafe_allow_html=True)
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        if "ATENCIONES" in df_detalle.columns:
            total_atenciones = pd.to_numeric(df_detalle["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum()
            st.markdown(f'''<div style="text-align: center; margin-bottom: 20px;"><div class="total-card" style="width: 300px; margin: auto;"><div class="total-title">TOTAL DE ATENCIONES</div><div class="total-value">{formatear_numero(total_atenciones)}</div></div></div>''', unsafe_allow_html=True)
        
        if seleccion == "Hospitales de Campaña":
            df_stats = df_detalle.copy()
            df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            resumen = df_stats.groupby(df_stats['NACIONALIAD'].astype(str).str.upper().str.strip())['ATENCIONES'].sum()
            suma_nac, suma_ext = resumen.get('NACIONAL', 0), resumen.get('EXTRANJERO', 0)
            col1, col2 = st.columns(2)
            with col1: st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES NACIONALES</div><div class="total-value">{formatear_numero(suma_nac)}</div></div>''', unsafe_allow_html=True)
            with col2: st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES EXTRANJEROS</div><div class="total-value">{formatear_numero(suma_ext)}</div></div>''', unsafe_allow_html=True)
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            if (suma_nac + suma_ext) > 0:
                fig = go.Figure(data=[go.Pie(labels=['NACIONAL', 'EXTRANJERO'], values=[suma_nac, suma_ext], hole=.6, marker_colors=['#FF0000', '#002060'])])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
