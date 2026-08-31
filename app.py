import streamlit as st
import pandas as pd
import os
import base64
import io
import datetime
import urllib.request
import json
import plotly.graph_objects as go
from github import Github
from streamlit_autorefresh import st_autorefresh

# Refrescar la aplicación automáticamente cada 5 segundos
st_autorefresh(interval=5000, key="dataview_autorefresh")

st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

def obtener_hora_red():
    """Obtiene la hora oficial de Venezuela (America/Caracas) desde worldtimeapi, con respaldo en UTC-4."""
    try:
        with urllib.request.urlopen("https://worldtimeapi.org/api/timezone/America/Caracas", timeout=3) as response:
            data = json.loads(response.read().decode())
            datetime_str = data["datetime"]
            dt = datetime.datetime.fromisoformat(datetime_str)
            if dt.tzinfo is not None:
                dt = dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4))).replace(tzinfo=None)
            return dt
    except Exception:
        return datetime.datetime.utcnow() - datetime.timedelta(hours=4)

def formatear_fecha_venezuela(dt):
    meses = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 
        5: "MAY", 6: "JUN", 7: "JUL", 8: "AGO", 
        9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }
    dia = f"{dt.day:02d}"
    mes = meses.get(dt.month, "AGO")
    anio = dt.year
    hora = dt.strftime("%H:%M:%S")
    return f"{dia}{mes}{anio} - {hora}"

def convertir_df_a_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Reporte')
    return output.getvalue()

# --- CSS GENERAL ---
st.markdown("""
<style>
button[kind="header"] {
    display: none !important;
}

.block-container { padding-top: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
.stApp { background-color: #0E1117 !important; }

.strat-card { 
    background-color: #2b3a4a; 
    padding: 12px; 
    border-radius: 6px; 
    border-left: 4px solid #00d2ff; 
    text-align: center; 
    margin-bottom: 10px; 
    height: 105px; 
}
.strat-title { font-size: 12px; text-transform: uppercase; color: #e0e0e0; font-weight: bold; margin-bottom: 6px; }
.strat-value { font-size: 26px; font-weight: 900; color: #ffffff; }

.compact-card { background-color: #1a1c23; padding: 8px; border-radius: 4px; border: 1px solid #31333f; text-align: center; margin-bottom: 8px; }
.card-title { font-size: 12px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 4px; }
.card-value { font-size: 18px; font-weight: 800; color: #ffffff; }

.total-card { background-color: #1e2025; padding: 12px; border-radius: 6px; border: 2px solid #FFD700; text-align: center; margin-top: 5px; }
.total-title { font-size: 15px; text-transform: uppercase; color: #FFD700; font-weight: bold; margin-bottom: 4px; }
.total-value { font-size: 30px; font-weight: 900; color: #ffffff; }

.total-tab { background: #1f3044; padding: 10px 20px; border-radius: 6px; border: 1px solid #00d2ff; display: inline-block; margin-bottom: 15px; }

.marquee-container { width: 100%; overflow: hidden; background-color: #0E1117; padding: 2px 0; }
.marquee-text { 
    display: inline-block; 
    white-space: nowrap; 
    animation: marquee 15s linear infinite; 
    color: #ffffff !important; 
    font-weight: bold; 
    font-size: 20px; 
}
@keyframes marquee {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

.logo-custom { width: 100%; height: 90px; object-fit: contain; display: block; margin-left: auto; margin-right: auto; margin-bottom: 2px; }

.pro-table-container {
    background: linear-gradient(145deg, #161b22, #0d1117);
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}
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
        st.warning(f"Aviso: Los datos se guardaron localmente, pero falló el respaldo en GitHub. (Detalle: {e})")
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
                         ["Resumen General", "Red Sanitaria Militar", "Hospitales de Campaña", "Sistema de Salud Tradicional", 
                          "Campamentos Transitorios", "Campamentos Itinerantes", "Inmunización", "Saneamiento Ambiental", 
                          "Programas de Salud", "Ruta Epidemiológica", "Daños de Infraestructura", 
                          "Total 4 Jornadas", "I Jornada Médica", "II Jornada Médica", "III Jornada Médica", "IV Jornada Médica"])

jornadas_map = {
    "I Jornada Médica": ("i", "I"),
    "II Jornada Médica": ("ii", "II"),
    "III Jornada Médica": ("iii", "III"),
    "IV Jornada Médica": ("iv", "IV")
}

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    
    if seleccion in jornadas_map:
        suf, num_romano = jornadas_map[seleccion]
        tab_ed1, tab_ed2, tab_ed3 = st.tabs(["🩺 Atenciones por Especialidad", "🤝 Apoyo Social", "👥 Demografía (Personas)"])
        
        archivo_esp = f"{suf}_especialidades_venezuela_renace.csv"
        archivo_apo = f"{suf}_apoyo_social_venezuela_renace.csv"
        archivo_demo = f"{suf}_demografia_venezuela_renace.csv"
        archivo_meta = f"{suf}_meta_venezuela_renace.csv"

        with tab_ed1:
            st.markdown(f"### Tabla: Atenciones por Especialidad ({seleccion})")
            cols_maestras = ["Nº", "ESPECIALIDAD", "ATENCIONES"]
            if not os.path.exists(archivo_esp):
                pd.DataFrame(columns=cols_maestras).to_csv(archivo_esp, index=False)
            df_esp = pd.read_csv(archivo_esp, dtype=str)
            
            df_esp_edit = st.data_editor(df_esp.reindex(columns=cols_maestras, fill_value="0"), use_container_width=True, num_rows="dynamic", key=f"esp_{suf}")
            
            if st.button("💾 Guardar Especialidades y Autosumar", key=f"btn_esp_{suf}"):
                df_esp_edit.to_csv(archivo_esp, index=False)
                
                try:
                    vals_esp = pd.to_numeric(df_esp_edit["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                    suma_especialidades = int(vals_esp.sum())
                    
                    if os.path.exists(archivo_meta):
                        df_m = pd.read_csv(archivo_meta, dtype=str)
                    else:
                        df_m = pd.DataFrame({"FECHA_JORNADA": [""], "TOTAL_ATENCIONES": ["0"]})
                    
                    dt_red = obtener_hora_red()
                    fecha_hora_actualizada = formatear_fecha_venezuela(dt_red)
                    
                    df_m.loc[0, "TOTAL_ATENCIONES"] = str(suma_especialidades)
                    df_m.loc[0, "FECHA_JORNADA"] = fecha_hora_actualizada
                    df_m.to_csv(archivo_meta, index=False)
                    guardar_en_github(archivo_meta)
                except Exception as e:
                    st.error(f"Error al autosumar y actualizar fecha: {e}")

                guardar_en_github(archivo_esp)
                st.success(f"¡Especialidades guardadas, Total de Atenciones actualizado a {suma_especialidades} y Fecha/Hora sincronizada!")

        with tab_ed2:
            st.markdown(f"### Tabla: Apoyo Social ({seleccion})")
            cols_apoyo = ["Nº", "CATEGORIA_APOYO", "VALOR"]
            if not os.path.exists(archivo_apo):
                pd.DataFrame(columns=cols_apoyo).to_csv(archivo_apo, index=False)
            df_apo = pd.read_csv(archivo_apo, dtype=str)
            df_apo_edit = st.data_editor(df_apo.reindex(columns=cols_apoyo, fill_value="0"), use_container_width=True, num_rows="dynamic", key=f"apo_{suf}")
            
            if st.button("💾 Guardar Apoyo Social", key=f"btn_apo_{suf}"):
                df_apo_edit.to_csv(archivo_apo, index=False)
                try:
                    if os.path.exists(archivo_meta):
                        df_m = pd.read_csv(archivo_meta, dtype=str)
                        dt_red = obtener_hora_red()
                        df_m.loc[0, "FECHA_JORNADA"] = formatear_fecha_venezuela(dt_red)
                        df_m.to_csv(archivo_meta, index=False)
                        guardar_en_github(archivo_meta)
                except:
                    pass
                guardar_en_github(archivo_apo)
                st.success("Apoyo social guardado.")

        with tab_ed3:
            st.markdown(f"### Desglose Demográfico ({seleccion})")
            if not os.path.exists(archivo_demo):
                pd.DataFrame({"MUJERES": ["0"], "HOMBRES": ["0"], "NIÑAS": ["0"], "NIÑOS": ["0"]}).to_csv(archivo_demo, index=False)
            df_demo = pd.read_csv(archivo_demo, dtype=str)
            df_demo_edit = st.data_editor(df_demo, use_container_width=True, num_rows="fixed", key=f"demo_{suf}")
            
            if st.button("💾 Guardar Demografía", key=f"btn_demo_{suf}"):
                df_demo_edit.to_csv(archivo_demo, index=False)
                try:
                    if os.path.exists(archivo_meta):
                        df_m = pd.read_csv(archivo_meta, dtype=str)
                        dt_red = obtener_hora_red()
                        df_m.loc[0, "FECHA_JORNADA"] = formatear_fecha_venezuela(dt_red)
                        df_m.to_csv(archivo_meta, index=False)
                        guardar_en_github(archivo_meta)
                except:
                    pass
                guardar_en_github(archivo_demo)
                st.success("Demografía guardada.")

        if st.button("❌ Cerrar Sesión", key=f"logout_{suf}"):
            st.session_state.admin_logueado = False
            st.rerun()

    else:
        archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_').replace('\'', '').replace('“', '').replace('”', '')}.csv"
        
        if seleccion == "Resumen General":
            cols_maestras = ["ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INTERVENCIONES Q."]
        elif seleccion == "Red Sanitaria Militar":
            cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "ATENCIONES"]
        elif seleccion == "Campamentos Itinerantes":
            cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "RESPONSABLE", "ATENCIONES"]
        elif seleccion in ["Campamentos Transitorios", "Sistema_de_Salud_Tradicional", "Sistema de Salud Tradicional", "Inmunización", "Saneamiento Ambiental", "Programas de Salud"]:
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

@st.cache_data(ttl=5)
def cargar_datos_cache(archivo):
    if os.path.exists(archivo):
        return pd.read_csv(archivo, dtype=str)
    return pd.DataFrame()

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
        "Campamentos Transitorios": "campamentos_transitorios.csv",
        "Campamentos Itinerantes": "campamentos_itinerantes.csv"
    }
    
    totales = {}
    total_general = 0
    
    for cat, archivo in categorias.items():
        val = 0
        if os.path.exists(archivo):
            df_cat = cargar_datos_cache(archivo)
            if not df_cat.empty and "ATENCIONES" in df_cat.columns:
                vals = pd.to_numeric(df_cat["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                val = int(vals.sum())
        totales[cat] = val
        total_general += val
        
    hosp_nac = 0
    hosp_ext = 0
    archivo_hosp = "hospitales_de_campaña.csv"
    if os.path.exists(archivo_hosp):
        df_hosp = cargar_datos_cache(archivo_hosp)
        if not df_hosp.empty and "ATENCIONES" in df_hosp.columns and "NACIONALIAD" in df_hosp.columns:
            df_hosp["ATENCIONES"] = pd.to_numeric(df_hosp["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_hosp["NACIONALIAD"] = df_hosp["NACIONALIAD"].astype(str).str.upper().str.strip()
            resumen = df_hosp.groupby("NACIONALIAD")["ATENCIONES"].sum()
            hosp_nac = int(resumen.get("NACIONAL", 0))
            hosp_ext = int(resumen.get("EXTRANJERO", 0))
    
    totales["Red Sanitaria Militar"] = totales.get("Red Sanitaria Militar", 0)
    totales["HOSP. DE CAMPAÑA NACIONALES"] = hosp_nac
    totales["HOSP. DE CAMPAÑA INTERNACIONALES"] = hosp_ext
    totales["Sistema de Salud Tradicional"] = totales.get("Sistema de Salud Tradicional", 0)
    totales["Campamentos Transitorios"] = totales.get("Campamentos Transitorios", 0)
    totales["Campamentos Itinerantes"] = totales.get("Campamentos Itinerantes", 0)
    totales["Inmunización"] = totales.get("Inmunización", 0)
    totales["Saneamiento Ambiental"] = totales.get("Saneamiento Ambiental", 0)
    totales["Programas de Salud"] = totales.get("Programas de Salud", 0)
    
    total_general += (hosp_nac + hosp_ext)

    orden_tarjetas = [
        "Red Sanitaria Militar", "HOSP. DE CAMPAÑA NACIONALES", "HOSP. DE CAMPAÑA INTERNACIONALES", "Sistema de Salud Tradicional", 
        "Campamentos Transitorios", "Campamentos Itinerantes", "Inmunización", "Saneamiento Ambiental", "Programas de Salud"
    ]

    fila1 = orden_tarjetas[:4]
    fila2 = orden_tarjetas[4:]

    cols1 = st.columns(4)
    for i, cat in enumerate(fila1):
        with cols1[i]:
            st.markdown(f'''
            <div class="strat-card">
                <div class="strat-title">{cat.upper()}</div>
                <div class="strat-value">{formatear_numero(totales.get(cat, 0))}</div>
            </div>
            ''', unsafe_allow_html=True)

    cols2 = st.columns(len(fila2) if len(fila2) > 0 else 4)
    for i, cat in enumerate(fila2):
        with cols2[i]:
            st.markdown(f'''
            <div class="strat-card">
                <div class="strat-title">{cat.upper()}</div>
                <div class="strat-value">{formatear_numero(totales.get(cat, 0))}</div>
            </div>
            ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div style="text-align: center; margin: 15px 0;">
        <div class="total-card" style="width: 50%; margin: auto;">
            <div class="total-title">TOTAL ATENCIONES</div>
            <div class="total-value">{formatear_numero(total_general)}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.subheader("🏥 RESUMEN OPERATIVO")
    df = cargar_datos_cache(ARCHIVO_RESUMEN)
    iconos = {"ALTAS MÉDICAS": "✅", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", 
              "CAMAS DISPONIBLES": "🛏️", "INTERVENCIONES Q.": "🔪"}
    cols_mostrar = ["ALTAS MÉDICAS", "TRASLADOS", "CAMAS OCUPADAS", 
                    "CAMAS DISPONIBLES", "INTERVENCIONES Q."]
    
    cols = st.columns(4)
    idx = 0
    for col_name in cols_mostrar:
        if not df.empty and col_name in df.columns:
            with cols[idx % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
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
        df_detalle = cargar_datos_cache(archivo_detalle)
        
        if not df_detalle.empty:
            st.markdown(f"""
            <div class="total-tab">
                <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">TOTAL REGISTROS {seleccion.upper()}: </span>
                <span style="color: #ffffff; font-size: 20px; font-weight: 900; margin-left: 10px;">{formatear_numero(len(df_detalle))}</span>
            </div>
            """, unsafe_allow_html=True)

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

elif seleccion == "Total 4 Jornadas":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); padding: 10px; border-radius: 6px; border: 1px solid #00d2ff; text-align: center; margin-bottom: 15px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 900;">CONSOLIDADO GENERAL DE LAS 4 JORNADAS VENEZUELA RENACE</h1>
        <p style="color: #00d2ff; margin: 0; font-size: 13px;">Acumulado total de atenciones, apoyo social y demografía de las jornadas I, II, III y IV.</p>
    </div>
    """, unsafe_allow_html=True)

    # Consolidar datos de las 4 jornadas
    jornadas_ids = ['i', 'ii', 'iii', 'iv']
    
    total_atenciones_acumulado = 0
    total_apoyo_acumulado = 0
    tot_mujeres, tot_hombres, tot_ninas, tot_ninos = 0, 0, 0, 0
    
    df_esp_list = []
    df_apo_list = []

    for s in jornadas_ids:
        # Especialidades
        f_esp = f"{s}_especialidades_venezuela_renace.csv"
        if os.path.exists(f_esp):
            df_e = cargar_datos_cache(f_esp)
            if not df_e.empty and "ATENCIONES" in df_e.columns:
                df_e["ATENCIONES_NUM"] = pd.to_numeric(df_e["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                total_atenciones_acumulado += df_e["ATENCIONES_NUM"].sum()
                df_esp_list.append(df_e)
        
        # Apoyo Social
        f_apo = f"{s}_apoyo_social_venezuela_renace.csv"
        if os.path.exists(f_apo):
            df_a = cargar_datos_cache(f_apo)
            if not df_a.empty and "VALOR" in df_a.columns:
                df_a["VALOR_NUM"] = pd.to_numeric(df_a["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                total_apoyo_acumulado += df_a["VALOR_NUM"].sum()
                df_apo_list.append(df_a)

        # Demografía
        f_dem = f"{s}_demografia_venezuela_renace.csv"
        if os.path.exists(f_dem):
            df_d = cargar_datos_cache(f_dem)
            if not df_d.empty:
                try:
                    row = df_d.iloc[0]
                    tot_mujeres += int(str(row.get("MUJERES", "0")).replace('.', ''))
                    tot_hombres += int(str(row.get("HOMBRES", "0")).replace('.', ''))
                    tot_ninas += int(str(row.get("NIÑAS", "0")).replace('.', ''))
                    tot_ninos += int(str(row.get("NIÑOS", "0")).replace('.', ''))
                except:
                    pass

    gran_total_general = total_atenciones_acumulado + total_apoyo_acumulado

    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;">
        <div style="background: linear-gradient(90deg, #0055ff, #00d2ff); padding: 12px 20px; border-radius: 6px; text-align: center; box-shadow: 0 2px 6px rgba(0,210,255,0.3);">
            <div style="color: #ffffff; font-size: 12px; font-weight: bold; text-transform: uppercase;">TOTAL ATENCIONES:</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: 900;">{formatear_numero(total_atenciones_acumulado)}</div>
        </div>
        <div style="background: linear-gradient(90deg, #ff8800, #ffaa00); padding: 12px 20px; border-radius: 6px; text-align: center; box-shadow: 0 2px 6px rgba(255,170,0,0.3);">
            <div style="color: #ffffff; font-size: 12px; font-weight: bold; text-transform: uppercase;">TOTAL APOYO SOCIAL:</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: 900;">{formatear_numero(total_apoyo_acumulado)}</div>
        </div>
        <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 12px 20px; border-radius: 6px; text-align: center; box-shadow: 0 2px 6px rgba(40,167,69,0.3);">
            <div style="color: #ffffff; font-size: 12px; font-weight: bold; text-transform: uppercase;">CONSOLIDADO GENERAL:</div>
            <div style="color: #ffffff; font-size: 24px; font-weight: 900;">{formatear_numero(gran_total_general)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 👥 Desglose Demográfico Acumulado (Las 4 Jornadas)")
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 25px;">
        <div style="background: #1e2025; padding: 12px; border-radius: 6px; border-left: 4px solid #ff4b4b; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">MUJERES</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900;">{formatear_numero(tot_mujeres)}</div>
        </div>
        <div style="background: #1e2025; padding: 12px; border-radius: 6px; border-left: 4px solid #00d2ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">HOMBRES</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900;">{formatear_numero(tot_hombres)}</div>
        </div>
        <div style="background: #1e2025; padding: 12px; border-radius: 6px; border-left: 4px solid #ff88ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">NIÑAS</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900;">{formatear_numero(tot_ninas)}</div>
        </div>
        <div style="background: #1e2025; padding: 12px; border-radius: 6px; border-left: 4px solid #ffd700; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">NIÑOS</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900;">{formatear_numero(tot_ninos)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df_esp_list:
        df_esp_total = pd.concat(df_esp_list, ignore_index=True)
        df_esp_grouped = df_esp_total.groupby("ESPECIALIDAD", as_index=False)["ATENCIONES_NUM"].sum()
        df_esp_grouped = df_esp_grouped.sort_values(by="ATENCIONES_NUM", ascending=True)

        st.markdown("### 🩺 Consolidado de Atenciones por Especialidad")
        fig_total_esp = go.Figure(data=[go.Bar(
            y=df_esp_grouped["ESPECIALIDAD"],
            x=df_esp_grouped["ATENCIONES_NUM"],
            orientation='h',
            marker=dict(color='#00d2ff', line=dict(color='#ffffff', width=1)),
            text=df_esp_grouped["ATENCIONES_NUM"],
            textposition='outside',
            textfont=dict(size=11, color='white', weight="bold")
        )])
        fig_total_esp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=11),
            margin=dict(t=10, b=10, l=180, r=40),
            height=max(350, len(df_esp_grouped) * 25),
            xaxis=dict(showgrid=True, gridcolor='#30363d', fixedrange=True),
            yaxis=dict(tickfont=dict(size=11, color='white', weight="bold"), fixedrange=True)
        )
        st.plotly_chart(fig_total_esp, use_container_width=True, config={'displayModeBar': False})

elif seleccion not in jornadas_map:
    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #00d2ff; padding-bottom: 8px; margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800;">📊 REGISTROS INSTITUCIONALES: <span style="color: #00d2ff;">{seleccion.upper()}</span></h2>
    </div>
    """, unsafe_allow_html=True)
    
    archivo_cat = f"{seleccion.lower().replace(' ', '_').replace('\'', '').replace('“', '').replace('”', '')}.csv"
    
    if os.path.exists(archivo_cat):
        df_cat_vista = cargar_datos_cache(archivo_cat)
        
        if not df_cat_vista.empty:
            st.markdown(f"""
            <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
                    <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">TOTAL DE REGISTROS</span>
                    <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{formatear_numero(len(df_cat_vista))}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="pro-table-container">', unsafe_allow_html=True)
            st.dataframe(df_cat_vista, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            col_dl1, col_dl2 = st.columns([2, 8])
            with col_dl1:
                st.download_button(
                    "📥 Descargar Reporte en Excel", 
                    data=convertir_df_a_excel(df_cat_vista), 
                    file_name=f"{seleccion.replace(' ', '_')}.xlsx", 
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info(f"No hay registros guardados actualmente en {seleccion}.")
    else:
        st.info(f"Aún no se ha creado el archivo de datos para {seleccion}.")

elif seleccion in jornadas_map:
    suf, num_romano = jornadas_map[seleccion]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); padding: 0px 4px; border-radius: 3px; border: 1px solid #00d2ff; text-align: center; margin: 0 0 2px 0;">
        <h4 style="color: #00d2ff; letter-spacing: 0.5px; margin: 0; padding: 0; font-size: 11px; font-weight: bold; line-height: 1;">REPÚBLICA BOLIVARIANA DE VENEZUELA • MINISTERIO DEL PODER POPULAR PARA LA DEFENSA</h4>
        <h1 style="color: #ffffff; margin: 0; padding: 0; font-size: 18px; font-weight: 900; line-height: 1.05;">{num_romano} ATENCIÓN MÉDICA ESPECIALIZADA <span style="color: #ffd700;">VENEZUELA RENACE</span></h1>
        <h3 style="color: #e0e0e0; margin: 0; padding: 0; font-size: 12px; background: #1f3044; display: inline-block; padding: 0px 4px; border-radius: 2px; line-height: 1;">PARA EL ESTADO LA GUAIRA</h3>
    </div>
    """, unsafe_allow_html=True)

    df_esp_viz = None
    archivo_esp = f"{suf}_especialidades_venezuela_renace.csv"
    
    if f"esp_{suf}" in st.session_state and st.session_state[f"esp_{suf}"] is not None:
        edited_data = st.session_state[f"esp_{suf}"]
        if isinstance(edited_data, pd.DataFrame):
            df_esp_viz = edited_data

    if df_esp_viz is None and os.path.exists(archivo_esp):
        df_esp_viz = cargar_datos_cache(archivo_esp)

    total_atenciones_num = 0
    if df_esp_viz is not None and not df_esp_viz.empty and "ATENCIONES" in df_esp_viz.columns:
        try:
            vals_temp = pd.to_numeric(df_esp_viz["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            total_atenciones_num = int(vals_temp.sum())
        except:
            pass
    else:
        archivo_meta = f"{suf}_meta_venezuela_renace.csv"
        if os.path.exists(archivo_meta):
            df_m = cargar_datos_cache(archivo_meta)
            if not df_m.empty:
                try:
                    total_atenciones_num = int(str(df_m.iloc[0].get("TOTAL_ATENCIONES", "0")).replace('.', ''))
                except:
                    pass

    total_atenciones_val = formatear_numero(total_atenciones_num)

    total_apoyo_num = 0
    archivo_apo_calc = f"{suf}_apoyo_social_venezuela_renace.csv"
    if os.path.exists(archivo_apo_calc):
        df_apo_calc = cargar_datos_cache(archivo_apo_calc)
        if not df_apo_calc.empty and "VALOR" in df_apo_calc.columns:
            try:
                vals_apo = pd.to_numeric(df_apo_calc["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                total_apoyo_num = int(vals_apo.sum())
            except:
                pass

    total_apoyo_val = formatear_numero(total_apoyo_num)
    suma_total_ambos = formatear_numero(total_atenciones_num + total_apoyo_num)

    fecha_str = "13AGO2026 - 15:03:52"
    archivo_meta = f"{suf}_meta_venezuela_renace.csv"
    if os.path.exists(archivo_meta):
        df_m = cargar_datos_cache(archivo_meta)
        if not df_m.empty:
            fecha_str = df_m.iloc[0].get("FECHA_JORNADA", fecha_str)

    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 12px; margin-bottom: 6px; flex-wrap: wrap;">
        <div style="background: #1e2025; padding: 6px 12px; border-radius: 4px; border: 1px solid #444; color: #ffd700; font-weight: bold; font-size: 16px; display: flex; align-items: center;">
            📅 {fecha_str}
        </div>
        <div style="background: linear-gradient(90deg, #0055ff, #00d2ff); padding: 6px 14px; border-radius: 4px; text-align: center; box-shadow: 0 2px 6px rgba(0,210,255,0.3);">
            <div style="color: #ffffff; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL ATENCIONES ESPECIALIDAD:</div>
            <div style="color: #ffffff; font-size: 20px; font-weight: 900; line-height: 1.1;">{total_atenciones_val}</div>
        </div>
        <div style="background: linear-gradient(90deg, #ff8800, #ffaa00); padding: 6px 14px; border-radius: 4px; text-align: center; box-shadow: 0 2px 6px rgba(255,170,0,0.3);">
            <div style="color: #ffffff; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL APOYO SOCIAL:</div>
            <div style="color: #ffffff; font-size: 20px; font-weight: 900; line-height: 1.1;">{total_apoyo_val}</div>
        </div>
        <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 6px 14px; border-radius: 4px; text-align: center; box-shadow: 0 2px 6px rgba(40,167,69,0.3);">
            <div style="color: #ffffff; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL GENERAL:</div>
            <div style="color: #ffffff; font-size: 20px; font-weight: 900; line-height: 1.1;">{suma_total_ambos}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_izq, col_der = st.columns([1.1, 0.9])

    with col_izq:
        st.markdown("""
        <div style="background: #161b22; padding: 6px; border-radius: 6px; border: 1px solid #30363d;">
            <h3 style="color: #00d2ff; text-align: center; font-size: 16px; margin-bottom: 4px; border-bottom: 2px solid #00d2ff; padding-bottom: 2px;">🩺 ATENCIONES POR ESPECIALIDAD</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if df_esp_viz is not None and not df_esp_viz.empty and "ESPECIALIDAD" in df_esp_viz.columns and "ATENCIONES" in df_esp_viz.columns:
            df_esp_viz["ATENCIONES_NUM"] = pd.to_numeric(df_esp_viz["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            max_val_esp = df_esp_viz["ATENCIONES_NUM"].max() if not df_esp_viz["ATENCIONES_NUM"].empty else 100
            
            fig_esp = go.Figure(data=[go.Bar(
                y=df_esp_viz["ESPECIALIDAD"],
                x=df_esp_viz["ATENCIONES_NUM"],
                orientation='h',
                marker=dict(color='#00d2ff', line=dict(color='#ffffff', width=1)),
                text=df_esp_viz["ATENCIONES_NUM"],
                textposition='outside',
                textfont=dict(size=11, color='white', family="sans-serif", weight="bold")
            )])
            
            fig_esp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                margin=dict(t=2, b=2, l=150, r=40),
                height=max(280, len(df_esp_viz) * 22), 
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='#30363d', 
                    tickfont=dict(size=11, color='white'), 
                    fixedrange=True,
                    range=[0, max_val_esp * 1.15]
                ),
                yaxis=dict(
                    autorange="reversed", 
                    tickfont=dict(size=11, color='white', weight="bold"), 
                    fixedrange=True,
                    dtick=1, 
                    showticklabels=True
                )
            )
            st.plotly_chart(fig_esp, use_container_width=True, key=f"grafico_especialidades_dinamico_{suf}", config={'displayModeBar': False})
        else:
            st.info("Sin registros de especialidades cargados.")

    with col_der:
        st.markdown("""
        <div style="background: #161b22; padding: 6px; border-radius: 6px; border: 1px solid #30363d; margin-bottom: 4px;">
            <h3 style="color: #ffaa00; text-align: center; font-size: 16px; margin-bottom: 4px; border-bottom: 2px solid #ffaa00; padding-bottom: 2px;">🤝 APOYO SOCIAL</h3>
        </div>
        """, unsafe_allow_html=True)

        archivo_apo = f"{suf}_apoyo_social_venezuela_renace.csv"
        df_apo_viz = None
        if f"apo_{suf}" in st.session_state and st.session_state[f"apo_{suf}"] is not None:
            edited_apo = st.session_state[f"apo_{suf}"]
            if isinstance(edited_apo, pd.DataFrame):
                df_apo_viz = edited_apo
        if df_apo_viz is None and os.path.exists(archivo_apo):
            df_apo_viz = cargar_datos_cache(archivo_apo)

        if df_apo_viz is not None and not df_apo_viz.empty and "CATEGORIA_APOYO" in df_apo_viz.columns and "VALOR" in df_apo_viz.columns:
            df_apo_viz["VALOR_NUM"] = pd.to_numeric(df_apo_viz["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            max_val_apo = df_apo_viz["VALOR_NUM"].max() if not df_apo_viz["VALOR_NUM"].empty else 100

            fig_apo = go.Figure(data=[go.Bar(
                y=df_apo_viz["CATEGORIA_APOYO"],
                x=df_apo_viz["VALOR_NUM"],
                orientation='h',
                marker=dict(color='#ffaa00', line=dict(color='#ffffff', width=1)),
                text=df_apo_viz["VALOR_NUM"],
                textposition='outside',
                textfont=dict(size=11, color='white', family="sans-serif", weight="bold")
            )])

            fig_apo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                margin=dict(t=2, b=2, l=150, r=40),
                height=max(140, len(df_apo_viz) * 22),
                xaxis=dict(
                    showgrid=True,
                    gridcolor='#30363d',
                    tickfont=dict(size=11, color='white'),
                    fixedrange=True,
                    range=[0, max_val_apo * 1.15]
                ),
                yaxis=dict(
                    autorange="reversed",
                    tickfont=dict(size=11, color='white', weight="bold"),
                    fixedrange=True,
                    dtick=1,
                    showticklabels=True
                )
            )
            st.plotly_chart(fig_apo, use_container_width=True, key=f"grafico_apoyo_social_dinamico_{suf}", config={'displayModeBar': False})
        else:
            st.info("Sin registros de apoyo social cargados.")

        st.markdown("""
        <div style="background: #161b22; padding: 6px; border-radius: 6px; border: 1px solid #30363d; margin-top: 10px; margin-bottom: 4px;">
            <h3 style="color: #20c997; text-align: center; font-size: 16px; margin-bottom: 4px; border-bottom: 2px solid #20c997; padding-bottom: 2px;">👥 DESGLOSE DEMOGRÁFICO</h3>
        </div>
        """, unsafe_allow_html=True)

        archivo_demo = f"{suf}_demografia_venezuela_renace.csv"
        df_demo_viz = None
        if f"demo_{suf}" in st.session_state and st.session_state[f"demo_{suf}"] is not None:
            edited_demo = st.session_state[f"demo_{suf}"]
            if isinstance(edited_demo, pd.DataFrame):
                df_demo_viz = edited_demo
        if df_demo_viz is None and os.path.exists(archivo_demo):
            df_demo_viz = cargar_datos_cache(archivo_demo)

        mujeres, hombres, ninas, ninos = 0, 0, 0, 0
        if df_demo_viz is not None and not df_demo_viz.empty:
            try:
                row = df_demo_viz.iloc[0]
                mujeres = int(str(row.get("MUJERES", "0")).replace('.', ''))
                hombres = int(str(row.get("HOMBRES", "0")).replace('.', ''))
                ninas = int(str(row.get("NIÑAS", "0")).replace('.', ''))
                ninos = int(str(row.get("NIÑOS", "0")).replace('.', ''))
            except:
                pass

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 5px;">
            <div style="background: #1e2025; padding: 8px; border-radius: 4px; border-left: 3px solid #ff4b4b; text-align: center;">
                <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">MUJERES</div>
                <div style="color: #ffffff; font-size: 16px; font-weight: 900;">{formatear_numero(mujeres)}</div>
            </div>
            <div style="background: #1e2025; padding: 8px; border-radius: 4px; border-left: 3px solid #00d2ff; text-align: center;">
                <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">HOMBRES</div>
                <div style="color: #ffffff; font-size: 16px; font-weight: 900;">{formatear_numero(hombres)}</div>
            </div>
            <div style="background: #1e2025; padding: 8px; border-radius: 4px; border-left: 3px solid #ff88ff; text-align: center;">
                <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">NIÑAS</div>
                <div style="color: #ffffff; font-size: 16px; font-weight: 900;">{formatear_numero(ninas)}</div>
            </div>
            <div style="background: #1e2025; padding: 8px; border-radius: 4px; border-left: 3px solid #ffd700; text-align: center;">
                <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">NIÑOS</div>
                <div style="color: #ffffff; font-size: 16px; font-weight: 900;">{formatear_numero(ninos)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if os.path.exists(archivo_esp):
            df_dl_esp = cargar_datos_cache(archivo_esp)
            st.download_button(
                f"📥 Descargar Especialidades ({num_romano})",
                data=convertir_df_a_excel(df_dl_esp),
                file_name=f"{suf}_especialidades_venezuela_renace.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    with col_btn2:
        if os.path.exists(archivo_apo):
            df_dl_apo = cargar_datos_cache(archivo_apo)
            st.download_button(
                f"📥 Descargar Apoyo Social ({num_romano})",
                data=convertir_df_a_excel(df_dl_apo),
                file_name=f"{suf}_apoyo_social_venezuela_renace.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
