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
                          "Total 5 Jornadas", "I Jornada Médica", "II Jornada Médica", "III Jornada Médica", "IV Jornada Médica", "V Jornada Médica"])

jornadas_map = {
    "I Jornada Médica": ("i", "I"),
    "II Jornada Médica": ("ii", "II"),
    "III Jornada Médica": ("iii", "III"),
    "IV Jornada Médica": ("iv", "IV"),
    "V Jornada Médica": ("v", "V")
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

elif seleccion in jornadas_map:
    suf, num_romano = jornadas_map[seleccion]
    
    archivo_esp = f"{suf}_especialidades_venezuela_renace.csv"
    archivo_apo = f"{suf}_apoyo_social_venezuela_renace.csv"
    archivo_demo = f"{suf}_demografia_venezuela_renace.csv"
    archivo_meta = f"{suf}_meta_venezuela_renace.csv"

    tot_atenciones = 0
    fecha_jornada_str = "S/F"
    if os.path.exists(archivo_meta):
        df_meta = cargar_datos_cache(archivo_meta)
        if not df_meta.empty:
            fecha_jornada_str = str(df_meta.loc[0, "FECHA_JORNADA"]) if "FECHA_JORNADA" in df_meta.columns else "S/F"
            try:
                tot_atenciones = int(str(df_meta.loc[0, "TOTAL_ATENCIONES"]).replace('.', ''))
            except:
                pass

    if tot_atenciones == 0 and os.path.exists(archivo_esp):
        df_e_tmp = cargar_datos_cache(archivo_esp)
        if not df_e_tmp.empty and "ATENCIONES" in df_e_tmp.columns:
            tot_atenciones = int(pd.to_numeric(df_e_tmp["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum())

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); padding: 12px; border-radius: 8px; border: 1px solid #00d2ff; text-align: center; margin-bottom: 15px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 900;">{seleccion.upper()} - VENEZUELA RENACE</h1>
        <p style="color: #00d2ff; margin: 3px 0 0 0; font-size: 12px;">Sincronización: <b>{fecha_jornada_str}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Demografía
    m_muj, m_hom, m_nin, m_ninos = 0, 0, 0, 0
    if os.path.exists(archivo_demo):
        df_d_vis = cargar_datos_cache(archivo_demo)
        if not df_d_vis.empty:
            try:
                row = df_d_vis.iloc[0]
                m_muj = int(str(row.get("MUJERES", "0")).replace('.', ''))
                m_hom = int(str(row.get("HOMBRES", "0")).replace('.', ''))
                m_nin = int(str(row.get("NIÑAS", "0")).replace('.', ''))
                m_ninos = int(str(row.get("NIÑOS", "0")).replace('.', ''))
            except:
                pass

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px;">
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ff4b4b; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">MUJERES</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(m_muj)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #00d2ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">HOMBRES</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(m_hom)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ff88ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">NIÑAS</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(m_nin)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ffd700; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">NIÑOS</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(m_ninos)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- CARGA DE DATOS PARA ESPECIALIDADES Y APOYO SOCIAL ---
    tot_esp_val = 0
    df_esp_vis = pd.DataFrame()
    if os.path.exists(archivo_esp):
        df_esp_vis = cargar_datos_cache(archivo_esp)
        if not df_esp_vis.empty and "ATENCIONES" in df_esp_vis.columns and "ESPECIALIDAD" in df_esp_vis.columns:
            df_esp_vis["ATENCIONES_NUM"] = pd.to_numeric(df_esp_vis["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_esp_vis["ESPECIALIDAD"] = df_esp_vis["ESPECIALIDAD"].astype(str).str.strip().str.upper()
            tot_esp_val = int(df_esp_vis["ATENCIONES_NUM"].sum())
            df_esp_vis = df_esp_vis.iloc[::-1].reset_index(drop=True)

    tot_apo_val = 0
    df_apo_vis = pd.DataFrame()
    if os.path.exists(archivo_apo):
        df_apo_vis = cargar_datos_cache(archivo_apo)
        if not df_apo_vis.empty and "VALOR" in df_apo_vis.columns and "CATEGORIA_APOYO" in df_apo_vis.columns:
            df_apo_vis["VALOR_NUM"] = pd.to_numeric(df_apo_vis["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_apo_vis["CATEGORIA_APOYO"] = df_apo_vis["CATEGORIA_APOYO"].astype(str).str.strip().str.upper()
            tot_apo_val = int(df_apo_vis["VALOR_NUM"].sum())
            df_apo_vis = df_apo_vis.iloc[::-1].reset_index(drop=True)

    total_general_jornada = tot_esp_val + tot_apo_val

    # --- ALTURA COMPACTA (Reducción de espacio entre líneas) ---
    altura_esp = max(250, len(df_esp_vis) * 22) if not df_esp_vis.empty else 250
    altura_apo = max(250, len(df_apo_vis) * 22) if not df_apo_vis.empty else 250

    # --- SECCIÓN LADO A LADO ---
    col_izq, col_der = st.columns(2)

    with col_izq:
        st.markdown("### 🩺 Atenciones por Especialidad")
        if not df_esp_vis.empty:
            fig_esp = go.Figure(data=[go.Bar(
                y=df_esp_vis["ESPECIALIDAD"],
                x=df_esp_vis["ATENCIONES_NUM"],
                orientation='h',
                marker=dict(color='#00d2ff', line=dict(color='#ffffff', width=1)),
                text=df_esp_vis["ATENCIONES_NUM"],
                textposition='outside',
                textfont=dict(size=13, color='white', family="Arial Black")
            )])
            fig_esp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=13),
                margin=dict(t=10, b=10, l=220, r=120),
                height=altura_esp,
                xaxis=dict(showgrid=True, gridcolor='#30363d', fixedrange=True, tickfont=dict(size=12, color='white')),
                yaxis=dict(tickfont=dict(size=13, color='white', family="Arial Black"), fixedrange=True, categoryorder="array", categoryarray=df_esp_vis["ESPECIALIDAD"].tolist())
            )
            st.plotly_chart(fig_esp, use_container_width=True, config={'displayModeBar': False})
            st.download_button("📥 Descargar Especialidades Excel", data=convertir_df_a_excel(df_esp_vis), file_name=f"{seleccion}_especialidades.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_esp_{suf}")

    with col_der:
        st.markdown("### 🤝 Apoyo Social")
        if not df_apo_vis.empty:
            fig_apo = go.Figure(data=[go.Bar(
                y=df_apo_vis["CATEGORIA_APOYO"],
                x=df_apo_vis["VALOR_NUM"],
                orientation='h',
                marker=dict(color='#ffaa00', line=dict(color='#ffffff', width=1)),
                text=df_apo_vis["VALOR_NUM"],
                textposition='outside',
                textfont=dict(size=13, color='white', family="Arial Black")
            )])
            fig_apo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=13),
                margin=dict(t=10, b=10, l=220, r=120),
                height=altura_apo,
                xaxis=dict(showgrid=True, gridcolor='#30363d', fixedrange=True, tickfont=dict(size=12, color='white')),
                yaxis=dict(tickfont=dict(size=13, color='white', family="Arial Black"), fixedrange=True, categoryorder="array", categoryarray=df_apo_vis["CATEGORIA_APOYO"].tolist())
            )
            st.plotly_chart(fig_apo, use_container_width=True, config={'displayModeBar': False})
            st.download_button("📥 Descargar Apoyo Social Excel", data=convertir_df_a_excel(df_apo_vis), file_name=f"{seleccion}_apoyo_social.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_apo_{suf}")

    # --- TOTALES HORIZONTALES ---
    st.markdown("---")
    t_col1, t_col2, t_col3 = st.columns(3)
    
    with t_col1:
        st.markdown(f"""
        <div style="background: #1a1c23; padding: 10px; border-radius: 6px; border: 1px solid #00d2ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL ATENCIONES ESPECIALIDAD</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(tot_esp_val)}</div>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        st.markdown(f"""
        <div style="background: #1a1c23; padding: 10px; border-radius: 6px; border: 1px solid #ffaa00; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL APOYO SOCIAL</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(tot_apo_val)}</div>
        </div>
        """, unsafe_allow_html=True)

    with t_col3:
        st.markdown(f"""
        <div style="background: #1e2025; padding: 10px; border-radius: 6px; border: 2px solid #FFD700; text-align: center;">
            <div style="color: #FFD700; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL GENERAL</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(total_general_jornada)}</div>
        </div>
        """, unsafe_allow_html=True)

elif seleccion == "Total 5 Jornadas":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); padding: 10px; border-radius: 6px; border: 1px solid #00d2ff; text-align: center; margin-bottom: 15px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 900;">CONSOLIDADO GENERAL DE LAS 5 JORNADAS VENEZUELA RENACE</h1>
        <p style="color: #00d2ff; margin: 0; font-size: 13px;">Acumulado total de atenciones, apoyo social y demografía de las jornadas I, II, III, IV y V.</p>
    </div>
    """, unsafe_allow_html=True)

    jornadas_ids = ['i', 'ii', 'iii', 'iv', 'v']
    
    lista_df_esp = []
    lista_df_apo = []
    
    c_muj, c_hom, c_nin, c_ninos = 0, 0, 0, 0

    for jid in jornadas_ids:
        f_esp = f"{jid}_especialidades_venezuela_renace.csv"
        f_apo = f"{jid}_apoyo_social_venezuela_renace.csv"
        f_demo = f"{jid}_demografia_venezuela_renace.csv"
        
        if os.path.exists(f_esp):
            df_e = cargar_datos_cache(f_esp)
            if not df_e.empty and "ESPECIALIDAD" in df_e.columns and "ATENCIONES" in df_e.columns:
                lista_df_esp.append(df_e)
                
        if os.path.exists(f_apo):
            df_a = cargar_datos_cache(f_apo)
            if not df_a.empty and "CATEGORIA_APOYO" in df_a.columns and "VALOR" in df_a.columns:
                lista_df_apo.append(df_a)
                
        if os.path.exists(f_demo):
            df_d = cargar_datos_cache(f_demo)
            if not df_d.empty:
                try:
                    row = df_d.iloc[0]
                    c_muj += int(str(row.get("MUJERES", "0")).replace('.', ''))
                    c_hom += int(str(row.get("HOMBRES", "0")).replace('.', ''))
                    c_nin += int(str(row.get("NIÑAS", "0")).replace('.', ''))
                    c_ninos += int(str(row.get("NIÑOS", "0")).replace('.', ''))
                except:
                    pass

    df_cons_esp = pd.DataFrame()
    if lista_df_esp:
        df_concat_esp = pd.concat(lista_df_esp, ignore_index=True)
        df_concat_esp["ATENCIONES_NUM"] = pd.to_numeric(df_concat_esp["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
        df_concat_esp["ESPECIALIDAD"] = df_concat_esp["ESPECIALIDAD"].astype(str).str.strip().str.upper()
        df_cons_esp = df_concat_esp.groupby("ESPECIALIDAD", as_index=False)["ATENCIONES_NUM"].sum()
        df_cons_esp = df_cons_esp.iloc[::-1].reset_index(drop=True)

    df_cons_apo = pd.DataFrame()
    if lista_df_apo:
        df_concat_apo = pd.concat(lista_df_apo, ignore_index=True)
        df_concat_apo["VALOR_NUM"] = pd.to_numeric(df_concat_apo["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
        df_concat_apo["CATEGORIA_APOYO"] = df_concat_apo["CATEGORIA_APOYO"].astype(str).str.strip().str.upper()
        df_cons_apo = df_concat_apo.groupby("CATEGORIA_APOYO", as_index=False)["VALOR_NUM"].sum()
        df_cons_apo = df_cons_apo.iloc[::-1].reset_index(drop=True)

    tot_cons_esp = int(df_cons_esp["ATENCIONES_NUM"].sum()) if not df_cons_esp.empty else 0
    tot_cons_apo = int(df_cons_apo["VALOR_NUM"].sum()) if not df_cons_apo.empty else 0
    total_general_5 = tot_cons_esp + tot_cons_apo

    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px;">
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ff4b4b; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">TOTAL MUJERES</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(c_muj)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #00d2ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">TOTAL HOMBRES</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(c_hom)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ff88ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">TOTAL NIÑAS</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(c_nin)}</div>
        </div>
        <div style="background: #1e2025; padding: 8px; border-radius: 6px; border-left: 4px solid #ffd700; text-align: center;">
            <div style="color: #b0b3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;">TOTAL NIÑOS</div>
            <div style="color: #ffffff; font-size: 18px; font-weight: 900;">{formatear_numero(c_ninos)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    altura_c_esp = max(250, len(df_cons_esp) * 22) if not df_cons_esp.empty else 250
    altura_c_apo = max(250, len(df_cons_apo) * 22) if not df_cons_apo.empty else 250

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("### 🩺 Consolidado Atenciones por Especialidad")
        if not df_cons_esp.empty:
            fig_c_esp = go.Figure(data=[go.Bar(
                y=df_cons_esp["ESPECIALIDAD"],
                x=df_cons_esp["ATENCIONES_NUM"],
                orientation='h',
                marker=dict(color='#00d2ff', line=dict(color='#ffffff', width=1)),
                text=df_cons_esp["ATENCIONES_NUM"],
                textposition='outside',
                textfont=dict(size=13, color='white', family="Arial Black")
            )])
            fig_c_esp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=13),
                margin=dict(t=10, b=10, l=220, r=120),
                height=altura_c_esp,
                xaxis=dict(showgrid=True, gridcolor='#30363d', fixedrange=True, tickfont=dict(size=12, color='white')),
                yaxis=dict(tickfont=dict(size=13, color='white', family="Arial Black"), fixedrange=True, categoryorder="array", categoryarray=df_cons_esp["ESPECIALIDAD"].tolist())
            )
            st.plotly_chart(fig_c_esp, use_container_width=True, config={'displayModeBar': False})
            st.download_button("📥 Descargar Consolidado Especialidades Excel", data=convertir_df_a_excel(df_cons_esp), file_name="consolidado_especialidades.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_cons_esp")

    with col_c2:
        st.markdown("### 🤝 Consolidado Apoyo Social")
        if not df_cons_apo.empty:
            fig_c_apo = go.Figure(data=[go.Bar(
                y=df_cons_apo["CATEGORIA_APOYO"],
                x=df_cons_apo["VALOR_NUM"],
                orientation='h',
                marker=dict(color='#ffaa00', line=dict(color='#ffffff', width=1)),
                text=df_cons_apo["VALOR_NUM"],
                textposition='outside',
                textfont=dict(size=13, color='white', family="Arial Black")
            )])
            fig_c_apo.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=13),
                margin=dict(t=10, b=10, l=220, r=120),
                height=altura_c_apo,
                xaxis=dict(showgrid=True, gridcolor='#30363d', fixedrange=True, tickfont=dict(size=12, color='white')),
                yaxis=dict(tickfont=dict(size=13, color='white', family="Arial Black"), fixedrange=True, categoryorder="array", categoryarray=df_cons_apo["CATEGORIA_APOYO"].tolist())
            )
            st.plotly_chart(fig_c_apo, use_container_width=True, config={'displayModeBar': False})
            st.download_button("📥 Descargar Consolidado Apoyo Social Excel", data=convertir_df_a_excel(df_cons_apo), file_name="consolidado_apoyo_social.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_cons_apo")

    st.markdown("---")
    tc_1, tc_2, tc_3 = st.columns(3)
    
    with tc_1:
        st.markdown(f"""
        <div style="background: #1a1c23; padding: 10px; border-radius: 6px; border: 1px solid #00d2ff; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL ACUMULADO ESPECIALIDAD</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(tot_cons_esp)}</div>
        </div>
        """, unsafe_allow_html=True)

    with tc_2:
        st.markdown(f"""
        <div style="background: #1a1c23; padding: 10px; border-radius: 6px; border: 1px solid #ffaa00; text-align: center;">
            <div style="color: #b0b3b8; font-size: 11px; font-weight: bold; text-transform: uppercase;">TOTAL ACUMULADO APOYO SOCIAL</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(tot_cons_apo)}</div>
        </div>
        """, unsafe_allow_html=True)

    with tc_3:
        st.markdown(f"""
        <div style="background: #1e2025; padding: 10px; border-radius: 6px; border: 2px solid #FFD700; text-align: center;">
            <div style="color: #FFD700; font-size: 11px; font-weight: bold; text-transform: uppercase;">GRAN TOTAL 5 JORNADAS</div>
            <div style="color: #ffffff; font-size: 22px; font-weight: 900; margin-top: 5px;">{formatear_numero(total_general_5)}</div>
        </div>
        """, unsafe_allow_html=True)
