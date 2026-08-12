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

# --- CSS GENERAL ---
st.markdown("""
<style>
.block-container { padding-top: 1rem !important; }
.stApp { background-color: #0E1117 !important; }

.strat-card { 
    background-color: #2b3a4a; 
    padding: 15px; 
    border-radius: 8px; 
    border-left: 5px solid #00d2ff; 
    text-align: center; 
    margin-bottom: 15px; 
    height: 120px; 
}
.strat-title { font-size: 14px; text-transform: uppercase; color: #e0e0e0; font-weight: bold; margin-bottom: 10px; }
.strat-value { font-size: 30px; font-weight: 900; color: #ffffff; }

.compact-card { background-color: #1a1c23; padding: 10px; border-radius: 4px; border: 1px solid #31333f; text-align: center; margin-bottom: 10px; }
.card-title { font-size: 14px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 5px; }
.card-value { font-size: 22px; font-weight: 800; color: #ffffff; }

.total-card { background-color: #1e2025; padding: 15px; border-radius: 8px; border: 2px solid #FFD700; text-align: center; margin-top: 10px; }
.total-title { font-size: 18px; text-transform: uppercase; color: #FFD700; font-weight: bold; margin-bottom: 5px; }
.total-value { font-size: 35px; font-weight: 900; color: #ffffff; }

.marquee-container { width: 100%; overflow: hidden; background-color: #0E1117; padding: 10px 0; }
.marquee-text { 
    display: inline-block; 
    white-space: nowrap; 
    animation: marquee 15s linear infinite; 
    color: #ffffff !important; 
    font-weight: bold; 
    font-size: 35px; 
}
@keyframes marquee {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

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
                         ["Resumen General", "Red Sanitaria Militar", "Hospitales de Campaña", "Sistema de Salud Tradicional", 
                          "Campamentos Transitorios", "Campamentos Itinerantes", "Inmunización", "Saneamiento Ambiental", 
                          "Programas de Salud", "Ruta Epidemiológica", "Daños de Infraestructura", "II Atención Médica Especializada 'Venezuela Renace'"])

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    
    if seleccion == "II Atención Médica Especializada 'Venezuela Renace'":
        tab_ed1, tab_ed2, tab_ed3, tab_ed4 = st.tabs(["📅 Info General & Totales", "🩺 Atenciones por Especialidad", "🤝 Apoyo Social", "👥 Demografía (Personas)"])
        
        with tab_ed1:
            st.markdown("### Fecha y Totales Principales")
            archivo_meta = "ii_meta_venezuela_renace.csv"
            if not os.path.exists(archivo_meta):
                pd.DataFrame({"FECHA_JORNADA": ["08AGO2026"], "TOTAL_ATENCIONES": ["3893"], "PERSONAS_ATENDIDAS": ["1235"]}).to_csv(archivo_meta, index=False)
            df_meta = pd.read_csv(archivo_meta, dtype=str)
            df_meta_edit = st.data_editor(df_meta, use_container_width=True, num_rows="fixed", key="meta_renace")
            if st.button("💾 Guardar Totales y Fecha"):
                df_meta_edit.to_csv(archivo_meta, index=False)
                guardar_en_github(archivo_meta)
                st.success("Totales guardados correctamente.")

        with tab_ed2:
            st.markdown("### Tabla: Atenciones por Especialidad")
            cols_maestras = ["Nº", "ESPECIALIDAD", "ATENCIONES"]
            archivo_esp = "ii_especialidades_venezuela_renace.csv"
            if not os.path.exists(archivo_esp):
                pd.DataFrame(columns=cols_maestras).to_csv(archivo_esp, index=False)
            df_esp = pd.read_csv(archivo_esp, dtype=str)
            
            # Usar st.data_editor y capturar el resultado devuelto en tiempo real (df_esp_edit)
            df_esp_edit = st.data_editor(df_esp.reindex(columns=cols_maestras, fill_value="0"), use_container_width=True, num_rows="dynamic", key="esp_renace")
            
            if st.button("💾 Guardar Especialidades y Autosumar"):
                # Guardar el editor de especialidades directamente
                df_esp_edit.to_csv(archivo_esp, index=False)
                
                # CÁLCULO AUTOMÁTICO INMEDIATO usando el dataframe editado actual
                try:
                    vals_esp = pd.to_numeric(df_esp_edit["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                    suma_especialidades = int(vals_esp.sum())
                    
                    archivo_meta = "ii_meta_venezuela_renace.csv"
                    if os.path.exists(archivo_meta):
                        df_m = pd.read_csv(archivo_meta, dtype=str)
                    else:
                        df_m = pd.DataFrame({"FECHA_JORNADA": ["08AGO2026"], "TOTAL_ATENCIONES": ["0"], "PERSONAS_ATENDIDAS": ["1235"]})
                    
                    df_m.loc[0, "TOTAL_ATENCIONES"] = str(suma_especialidades)
                    df_m.to_csv(archivo_meta, index=False)
                    guardar_en_github(archivo_meta)
                except Exception as e:
                    st.error(f"Error al autosumar: {e}")

                guardar_en_github(archivo_esp)
                st.success(f"¡Especialidades guardadas y Total de Atenciones autosumado correctamente a {suma_especialidades}!")
                # Nota: Ya no ejecutamos st.rerun() aquí para evitar el parpadeo y permitir ver el cambio instantáneamente abajo.

        with tab_ed3:
            st.markdown("### Tabla: Apoyo Social")
            cols_apoyo = ["Nº", "CATEGORIA_APOYO", "VALOR"]
            archivo_apo = "ii_apoyo_social_venezuela_renace.csv"
            if not os.path.exists(archivo_apo):
                pd.DataFrame(columns=cols_apoyo).to_csv(archivo_apo, index=False)
            df_apo = pd.read_csv(archivo_apo, dtype=str)
            df_apo_edit = st.data_editor(df_apo.reindex(columns=cols_apoyo, fill_value="0"), use_container_width=True, num_rows="dynamic", key="apo_renace")
            if st.button("💾 Guardar Apoyo Social"):
                df_apo_edit.to_csv(archivo_apo, index=False)
                guardar_en_github(archivo_apo)
                st.success("Apoyo social guardado.")

        with tab_ed4:
            st.markdown("### Desglose Demográfico (Mujeres, Hombres, Niñas, Niños)")
            archivo_demo = "ii_demografia_venezuela_renace.csv"
            if not os.path.exists(archivo_demo):
                pd.DataFrame({"MUJERES": ["587"], "HOMBRES": ["431"], "NIÑAS": ["121"], "NIÑOS": ["96"]}).to_csv(archivo_demo, index=False)
            df_demo = pd.read_csv(archivo_demo, dtype=str)
            df_demo_edit = st.data_editor(df_demo, use_container_width=True, num_rows="fixed", key="demo_renace")
            if st.button("💾 Guardar Demografía"):
                df_demo_edit.to_csv(archivo_demo, index=False)
                guardar_en_github(archivo_demo)
                st.success("Demografía guardada.")

        if st.button("❌ Cerrar Sesión"):
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
    <div style="text-align: center; margin: 20px 0;">
        <div class="total-card" style="width: 50%; margin: auto;">
            <div class="total-title">TOTAL ATENCIONES</div>
            <div class="total-value">{formatear_numero(total_general)}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.subheader("🏥 RESUMEN OPERATIVO")
    df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
    iconos = {"ALTAS MÉDICAS": "✅", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", 
              "CAMAS DISPONIBLES": "🛏️", "INTERVENCIONES Q.": "🔪"}
    cols_mostrar = ["ALTAS MÉDICAS", "TRASLADOS", "CAMAS OCUPADAS", 
                    "CAMAS DISPONIBLES", "INTERVENCIONES Q."]
    
    cols = st.columns(4)
    idx = 0
    for col_name in cols_mostrar:
        if col_name in df.columns:
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

elif seleccion == "II Atención Médica Especializada 'Venezuela Renace'":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%); padding: 25px; border-radius: 12px; border: 2px solid #00d2ff; text-align: center; margin-bottom: 25px;">
        <h4 style="color: #00d2ff; letter-spacing: 2px; margin: 0; font-size: 14px; font-weight: bold;">REPÚBLICA BOLIVARIANA DE VENEZUELA • MINISTERIO DEL PODER POPULAR PARA LA DEFENSA</h4>
        <h1 style="color: #ffffff; margin: 10px 0; font-size: 30px; font-weight: 900;">ATENCIÓN MÉDICA ESPECIALIZADA<br><span style="color: #ffd700;">VENEZUELA RENACE</span></h1>
        <h3 style="color: #e0e0e0; margin: 0; font-size: 18px; background: #1f3044; display: inline-block; padding: 6px 20px; border-radius: 20px;">PARA EL ESTADO LA GUAIRA</h3>
    </div>
    """, unsafe_allow_html=True)

    # Si hay datos recién editados en el session_state del data_editor, los usamos directamente en tiempo real para la gráfica y el total sin requerir refresh
    df_esp_viz = None
    archivo_esp = "ii_especialidades_venezuela_renace.csv"
    
    if "esp_renace" in st.session_state and st.session_state["esp_renace"] is not None:
        # st.session_state["esp_renace"] contiene las modificaciones pendientes o recién guardadas en el editor
        edited_data = st.session_state["esp_renace"]
        if isinstance(edited_data, dict) and "edited_rows" in edited_data:
            # Reconstruir o aplicar cambios si viene estructurado como diccionario de ediciones de Streamlit
            pass
        # O si el state almacena directamente el dataframe modificado según la versión de Streamlit:
        if isinstance(edited_data, pd.DataFrame):
            df_esp_viz = edited_data

    if df_esp_viz is None and os.path.exists(archivo_esp):
        df_esp_viz = pd.read_csv(archivo_esp, dtype=str)

    # Cálculo dinámico en tiempo real del total de atenciones basado en lo que está en la tabla de especialidades
    total_atenciones_val = "0"
    if df_esp_viz is not None and not df_esp_viz.empty and "ATENCIONES" in df_esp_viz.columns:
        try:
            vals_temp = pd.to_numeric(df_esp_viz["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            total_atenciones_val = formatear_numero(vals_temp.sum())
        except:
            pass
    else:
        archivo_meta = "ii_meta_venezuela_renace.csv"
        if os.path.exists(archivo_meta):
            df_m = pd.read_csv(archivo_meta, dtype=str)
            if not df_m.empty:
                total_atenciones_val = formatear_numero(df_m.iloc[0].get("TOTAL_ATENCIONES", "3893"))

    fecha_str = "08AGO2026"
    archivo_meta = "ii_meta_venezuela_renace.csv"
    if os.path.exists(archivo_meta):
        df_m = pd.read_csv(archivo_meta, dtype=str)
        if not df_m.empty:
            fecha_str = df_m.iloc[0].get("FECHA_JORNADA", fecha_str)

    st.markdown(f"""
    <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 25px; flex-wrap: wrap;">
        <div style="background: #1e2025; padding: 10px 25px; border-radius: 8px; border: 1px solid #444; color: #ffd700; font-weight: bold; font-size: 18px;">
            📅 {fecha_str}
        </div>
        <div style="background: linear-gradient(90deg, #0055ff, #00d2ff); padding: 12px 40px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(0,210,255,0.4);">
            <div style="color: #ffffff; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">TOTAL DE ATENCIONES:</div>
            <div style="color: #ffffff; font-size: 38px; font-weight: 900; line-height: 1.1;">{total_atenciones_val}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_izq, col_der = st.columns([1.1, 0.9])

    with col_izq:
        st.markdown("""
        <div style="background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d;">
            <h3 style="color: #00d2ff; text-align: center; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #00d2ff; padding-bottom: 8px;">🩺 ATENCIONES POR ESPECIALIDAD</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if df_esp_viz is not None and not df_esp_viz.empty and "ESPECIALIDAD" in df_esp_viz.columns and "ATENCIONES" in df_esp_viz.columns:
            df_esp_viz["ATENCIONES_NUM"] = pd.to_numeric(df_esp_viz["ATENCIONES"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            
            fig_esp = go.Figure(data=[go.Bar(
                y=df_esp_viz["ESPECIALIDAD"],
                x=df_esp_viz["ATENCIONES_NUM"],
                orientation='h',
                marker=dict(color='#00d2ff', line=dict(color='#ffffff', width=1)),
                text=df_esp_viz["ATENCIONES_NUM"],
                textposition='outside'
            )])
            fig_esp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=11),
                margin=dict(t=10, b=10, l=10, r=30),
                height=550,
                xaxis=dict(showgrid=True, gridcolor='#30363d'),
                yaxis=dict(autorange="reversed")
            )
            st.plotly_chart(fig_esp, use_container_width=True, key="grafico_especialidades_dinamico")
        else:
            st.info("Sin registros de especialidades cargados.")

    with col_der:
        st.markdown("""
        <div style="background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 20px;">
            <h3 style="color: #ffd700; text-align: center; font-size: 18px; margin-bottom: 15px; border-bottom: 2px solid #ffd700; padding-bottom: 8px;">🤝 APOYO SOCIAL</h3>
        </div>
        """, unsafe_allow_html=True)

        archivo_apo = "ii_apoyo_social_venezuela_renace.csv"
        if os.path.exists(archivo_apo):
            df_apo = pd.read_csv(archivo_apo, dtype=str)
            if not df_apo.empty and "CATEGORIA_APOYO" in df_apo.columns and "VALOR" in df_apo.columns:
                df_apo["VALOR_NUM"] = pd.to_numeric(df_apo["VALOR"].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                
                fig_apo = go.Figure(data=[go.Bar(
                    y=df_apo["CATEGORIA_APOYO"],
                    x=df_apo["VALOR_NUM"],
                    orientation='h',
                    marker=dict(color='#ffaa00', line=dict(color='#ffffff', width=1)),
                    text=df_apo["VALOR_NUM"],
                    textposition='outside'
                )])
                fig_apo.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=11),
                    margin=dict(t=10, b=10, l=10, r=30),
                    height=350,
                    xaxis=dict(showgrid=True, gridcolor='#30363d'),
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig_apo, use_container_width=True, key="grafico_apoyo_dinamico")
            else:
                st.info("Agregue los registros de apoyo social desde el panel (⚙️).")
        else:
            st.info("Sin registros de apoyo social cargados.")

    mujeres, hombres, ninas, ninos, total_personas = "587", "431", "121", "96", "1.235"
    archivo_demo = "ii_demografia_venezuela_renace.csv"
    if os.path.exists(archivo_demo):
        df_d = pd.read_csv(archivo_demo, dtype=str)
        if not df_d.empty:
            row_d = df_d.iloc[0]
            mujeres = formatear_numero(row_d.get("MUJERES", "587"))
            hombres = formatear_numero(row_d.get("HOMBRES", "431"))
            ninas = formatear_numero(row_d.get("NIÑAS", "121"))
            ninos = formatear_numero(row_d.get("NIÑOS", "96"))
            try:
                tot_p = int(row_d.get("MUJERES","587").replace('.','')) + int(row_d.get("HOMBRES","431").replace('.','')) + int(row_d.get("NIÑAS","121").replace('.','')) + int(row_d.get("NIÑOS","96").replace('.',''))
                total_personas = formatear_numero(tot_p)
            except:
                pass

    st.markdown(f"""
    <div style="background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px;">
        <h3 style="color: #00d2ff; text-align: center; font-size: 18px; margin-bottom: 20px; text-transform: uppercase;">👥 Desglose de Personas Atendidas</h3>
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; gap: 15px; text-align: center;">
            <div style="background: #21262d; padding: 15px 25px; border-radius: 8px; border-bottom: 4px solid #ff4b4b; min-width: 150px;">
                <div style="font-size: 24px;">👩</div>
                <div style="color: #ff4b4b; font-size: 24px; font-weight: 900;">{mujeres}</div>
                <div style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">Mujeres</div>
            </div>
            <div style="background: #21262d; padding: 15px 25px; border-radius: 8px; border-bottom: 4px solid #00d2ff; min-width: 150px;">
                <div style="font-size: 24px;">👨</div>
                <div style="color: #00d2ff; font-size: 24px; font-weight: 900;">{hombres}</div>
                <div style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">Hombres</div>
            </div>
            <div style="background: #21262d; padding: 15px 25px; border-radius: 8px; border-bottom: 4px solid #ff79c6; min-width: 150px;">
                <div style="font-size: 24px;">👧</div>
                <div style="color: #ff79c6; font-size: 24px; font-weight: 900;">{ninas}</div>
                <div style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">Niñas</div>
            </div>
            <div style="background: #21262d; padding: 15px 25px; border-radius: 8px; border-bottom: 4px solid #50fa7b; min-width: 150px;">
                <div style="font-size: 24px;">👦</div>
                <div style="color: #50fa7b; font-size: 24px; font-weight: 900;">{ninos}</div>
                <div style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">Niños</div>
            </div>
            <div style="background: linear-gradient(135deg, #2b3a4a 0%, #1f3044 100%); padding: 15px 35px; border-radius: 8px; border: 2px solid #ffd700; min-width: 180px;">
                <div style="color: #ffd700; font-size: 12px; font-weight: bold; text-transform: uppercase;">Total Personas Atendidas</div>
                <div style="color: #ffffff; font-size: 28px; font-weight: 900;">{total_personas}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif seleccion in ["Red Sanitaria Militar", "Inmunización", "Saneamiento Ambiental", "Campamentos Transitorios", "Campamentos Itinerantes", "Sistema de Salud Tradicional", "Programas de Salud"]:
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
            ''', unsafe_allow_html=True)
            
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
            ''', unsafe_allow_html=True)
        
        if seleccion == "Hospitales de Campaña":
            df_stats = df_detalle.copy()
            df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_stats['NACIONALIAD'] = df_stats['NACIONALIAD'].astype(str).str.upper().str.strip()
            resumen = df_stats.groupby('NACIONALIAD')['ATENCIONES'].sum()
            suma_nac = resumen.get('NACIONAL', 0)
            suma_ext = resumen.get('EXTRANJERO', 0)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES NACIONALES</div><div class="total-value">{formatear_numero(suma_nac)}</div></div>''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''<div class="total-card"><div class="total-title">TOTAL ATENCIONES EXTRANJEROS</div><div class="total-value">{formatear_numero(suma_ext)}</div></div>''', unsafe_allow_html=True)
            
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            
            if (suma_nac + suma_ext) > 0:
                fig = go.Figure(data=[go.Pie(labels=['NACIONAL', 'EXTRANJERO'], values=[suma_nac, suma_ext], hole=.6, marker_colors=['#FF0000', '#002060'], textinfo='none')])
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=20, b=80, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
        
        st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
