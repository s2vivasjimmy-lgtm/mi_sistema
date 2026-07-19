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

# --- CSS ---
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
.stApp { background-color: #0E1117 !important; }
.compact-card { background-color: #1a1c23; padding: 4px; border-radius: 4px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
.strat-card { background-color: #2b3a4a; padding: 10px; border-radius: 8px; border-left: 5px solid #00d2ff; text-align: center; margin-bottom: 15px; }
.total-card { background-color: #1e2025; padding: 15px; border-radius: 8px; border: 2px solid #FFD700; text-align: center; margin-top: 10px; }
.total-title { font-size: 14px; text-transform: uppercase; color: #FFD700; font-weight: bold; margin-bottom: 5px; }
.total-value { font-size: 28px; font-weight: 900; color: #ffffff; }
.card-title { font-size: 17px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 5px; }
.card-value { font-size: 30px; font-weight: 800; color: #ffffff; }
.strat-title { font-size: 14px; text-transform: uppercase; color: #e0e0e0; font-weight: bold; }
.strat-value { font-size: 24px; font-weight: 900; color: #ffffff; }
.marquee-container { width: 100%; overflow: hidden; white-space: nowrap; box-sizing: border-box; margin-bottom: 20px; border-top: 2px solid #31333f; border-bottom: 2px solid #31333f; padding: 0px 0; }
.marquee-text { display: inline-block; font-size: 20px; animation: marquee 15s linear infinite; margin: 0; color: #ffffff !important; font-weight: bold; }
@keyframes marquee { 0% { transform: translate(-100%, 0); } 100% { transform: translate(100%, 0); } }
.logo-custom { width: 100%; height: 200px; object-fit: contain; display: block; margin-left: auto; margin-right: auto; margin-bottom: 10px; }
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

if "admin_logueado" not in st.session_state: 
    st.session_state.admin_logueado = False

def inicializar_resumen():
    if not os.path.exists(ARCHIVO_RESUMEN):
        data = {
            "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], "TRASLADOS": ["0"], 
            "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"], 
            "HOSPITALIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]
        }
        pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)

inicializar_resumen()

with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", 
                         ["Resumen General", "Red Sanitaria Militar", "Hospitales de Campaña","Sistema de Salud Tradicional", 
                          "Campamentos Transitorios", "Inmunización", "Saneamiento Ambiental", 
                          "Programas de Salud", "Ruta Epidemiológica", "Daños de Infraestructura"])

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
        if guardar_en_github(archivo_a_editar): 
            st.success("Guardado en servidor.")
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

# --- BLOQUE CORREGIDO ---
if os.path.exists("logo_institucional.jpg"):
    try:
        with open("logo_institucional.jpg", "rb") as image_file:
            img_bytes = image_file.read()
            encoded_string = base64.b64encode(img_bytes).decode('utf-8')
            html_img = f'<img src="data:image/jpeg;base64,{encoded_string}" class="logo-custom">'
            st.markdown(html_img, unsafe_allow_html=True)
    except Exception:
        pass

st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

js_fullscreen = """
<script>
    function toggleFS(id) { 
        var elem = document.getElementById(id); 
        if (!document.fullscreenElement) { 
            elem.requestFullscreen().catch(err => alert("Error: " + err.message)); 
        } else { 
            document.exitFullscreen(); 
        } 
    }
</script>
"""

def formatear_numero(n):
    try:
        return f"{int(n):,}".replace(",", ".")
    except:
        return "0"

if seleccion == "Resumen General":
    st.subheader("🧑‍⚕️ ATENCIONES")
    
    categorias = {
        "Red Sanitaria Militar": "red_sanitaria_militar.csv",
        "Inmunización": "inmunización.csv",
        "Saneamiento Ambiental": "saneamiento_ambiental.csv",
        "Programas de Salud": "programas_de_salud.csv",
        "Sistema de Salud Tradicional": "sistema_de_salud_tradicional.csv",
        "Camp. Transitorios": "campamentos_transitorios.csv"
    }
    
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
            df_hosp["NACIONALIAD"] = df_hosp["NACIONALIAD"].astype(str).str.upper().str.strip()
            resumen = df_hosp.groupby("NACIONALIAD")["ATENCIONES"].sum()
            hosp_nac = int(resumen.get("NACIONAL", 0))
            hosp_ext = int(resumen.get("EXTRANJERO", 0))
    
    totales["HOSP. DE CAMPAÑA NACIONALES"] = hosp_nac
    totales["HOSP. DE CAMPAÑA INTERNACIONALES"] = hosp_ext
    total_general += (hosp_nac + hosp_ext)

    fila1_nombres = ["Red Sanitaria Militar", "Inmunización", "Saneamiento Ambiental", "Programas de Salud"]
    fila2_nombres = ["Sistema de Salud Tradicional", "Camp. Transitorios", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES"]

    cols1 = st.columns(4)
    for i, cat in enumerate(fila1_nombres):
        val = totales.get(cat, 0)
        cols1[i].markdown(f'''
        <div class="strat-card">
            <div class="strat-title" style="font-size: 11px;">{cat.upper()}</div>
            <div class="strat-value">{formatear_numero(val)}</div>
        </div>
        ''', unsafe_html=True)

    cols2 = st.columns(4)
    for i, cat in enumerate(fila2_nombres):
        val = totales.get(cat, 0)
        cols2[i].markdown(f'''
        <div class="strat-card">
            <div class="strat-title" style="font-size: 11px;">{cat.upper()}</div>
            <div class="strat-value">{formatear_numero(val)}</div>
        </div>
        ''', unsafe_html=True)

    st.markdown(f'''
    <div style="text-align: center; margin: 20px 0;">
        <div class="total-card" style="width: 50%; margin: auto;">
            <div class="total-title">TOTAL ATENCIONES</div>
            <div class="total-value">{formatear_numero(total_general)}</div>
        </div>
    </div>
    ''', unsafe_html=True)

    st.subheader("🏥 RESUMEN OPERATIVO")
    df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
    iconos = {"ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", 
              "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INTERVENCIONES Q.": "🔪"}
    cols_mostrar = ["ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", 
                    "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INTERVENCIONES Q."]
    
    cols = st.columns(4)
    idx = 0
    for col_name in cols_mostrar:
        if col_name in df.columns:
            with cols[idx % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_html=True)
            idx += 1
            
    st.subheader("📍UBICACIONES EN TIEMPO REAL")
    st.components.v1.html(f"""
        <div id="map-container-general" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS('map-container-general')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ⛶ Pantalla Completa
            </button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
        </div>
        {js_fullscreen}
    """, height=510)

elif seleccion == "Ruta Epidemiológica":
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = "ruta_epidemiológica.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    st.markdown("### 📍UBICACIÓN DEL PACIENTE")
    st.components.v1.html(f"""
        <div id="map-container-ruta" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS('map-container-ruta')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ⛶ Pantalla Completa
            </button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1yl45t_HdDytdAAzsaOcMJzM3ICa5bPk" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
        </div>
        {js_fullscreen}
    """, height=510)

elif seleccion in ["Red Sanitaria Militar", "Inmunización", "Saneamiento Ambiental", "Campamentos Transitorios", "Sistema de Salud Tradicional", "Programas de Salud"]:
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        if "ATENCIONES" in df_detalle.columns:
            df_sum = df_detalle.copy()
            df_sum["ATENCIONES"] = pd.to_numeric(df_sum["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            total_atenciones = df_sum["ATENCIONES"].sum()
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 20px;">
                <div class="total-card" style="width: 300px; margin: auto;">
                    <div class="total-title">TOTAL DE ATENCIONES</div>
                    <div class="total-value">{formatear_numero(total_atenciones)}</div>
                </div>
            </div>
            ''', unsafe_html=True)
            
        st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.subheader(f"📋 Detalle: {seleccion}")
    archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
    if os.path.exists(archivo_detalle):
        df_detalle = pd.read_csv(archivo_detalle, dtype=str)
        if "ATENCIONES" in df_detalle.columns:
            df_sum = df_detalle.copy()
            df_sum["ATENCIONES"] = pd.to_numeric(df_sum["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            total_atenciones = df_sum["ATENCIONES"].sum()
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 20px;">
                <div class="total-card" style="width: 300px; margin: auto;">
                    <div class="total-title">TOTAL DE ATENCIONES</div>
                    <div class="total-value">{formatear_numero(total_atenciones)}</div>
                </div>
            </div>
            ''', unsafe_html=True)
        
        if seleccion == "Hospitales de Campaña":
            df_stats = df_detalle.copy()
            df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_stats['NACIONALIAD'] = df_stats['NACIONALIAD'].astype(str).str.upper().str.strip()
            resumen = df_stats.groupby('NACIONALIAD')['ATENCIONES'].sum()
            suma_nac = resumen.get('NACIONAL', 0)
            suma_ext = resumen.get('EXTRANJERO', 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES NACIONALES</div><div class="total-value">{formatear_numero(suma_nac)}</div></div>''', unsafe_html=True)
            with col2:
                st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES EXTRANJEROS</div><div class="total-value">{formatear_numero(suma_ext)}</div></div>''', unsafe_html=True)
            
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            
            if (suma_nac + suma_ext) > 0:
                fig = go.Figure(data=[go.Pie(labels=['NACIONAL', 'EXTRANJERO'], values=[suma_nac, suma_ext], hole=.6, marker_colors=['#FF0000', '#002060'], textinfo='none')])
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=20, b=80, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
