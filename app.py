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

inicializar_resumen()

with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", 
                         ["Resumen General", "Hospitales de Campaña", 
                          "Campamentos Transitorios", "Inmunización", 
                          "Saneamiento Ambiental", "Ruta Epidemiológica", "Daños de Infraestructura"])

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo_a_editar = ARCHIVO_RESUMEN if seleccion == "Resumen General" else f"{seleccion.lower().replace(' ', '_')}.csv"

    if seleccion == "Resumen General":
        cols_maestras = ["ATENCIONES", "ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", 
                         "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INMUNIZACIONES", "INTERVENCIONES Q.",
                         "SISTEMA DE SALUD TRADICIONAL", "HOSP. DE CAMPAÑA NACIONALES",
                         "HOSP. DE CAMPAÑA INTERNACIONALES", "CAMP. TRANSITORIOS"]
    elif seleccion == "Campamentos Transitorios":
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS"]
    elif seleccion == "Inmunización":
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "TOXOIDE", "FIEBRE AMARILLA", "S.R.P", "TOTAL"]
    elif seleccion == "Saneamiento Ambiental":
        cols_maestras = ["DESRATIZACIÓN", "FUMIGACIÓN", "DESINFECCIÓN Y ABATIZACIÓN", "DESPARASITACIÓN", "PERSONAS PROTEGIDAS"]
    elif seleccion == "Ruta Epidemiológica":
        cols_maestras = ["Nº", "POBLACIÓN DE EDAD", "SEXO", "PUNTO/RUTA", "DIÁNOSTICO", "ACCIONES", "RESULTADO", "NIVEL DE PRIORIDAD", "DIRECCIÓN DEL PACIENTE", "TELEFONO", "FECHA"]
    else:
        cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIAD", "PAIS RESPONSABLE", "ATENCIONES"]

    if not os.path.exists(archivo_a_editar):
        df_actual = pd.DataFrame(columns=cols_maestras)
    else:
        df_actual = pd.read_csv(archivo_a_editar, dtype=str)
        df_actual = df_actual.loc[:, df_actual.columns.isin(cols_maestras)]
        df_actual = df_actual.dropna(how='all')
        df_actual = df_actual[~df_actual.apply(lambda x: x.astype(str).str.contains("None", na=False).any() if x.name in df_actual.columns else False, axis=1)]

    df_editado = st.data_editor(df_actual.reindex(columns=cols_maestras, fill_value="0"), use_container_width=True, num_rows="dynamic")

    if st.button("💾 Guardar Cambios"):
        if seleccion == "Inmunización":
            for c in ["TOXOIDE", "FIEBRE AMARILLA", "S.R.P"]:
                df_editado[c] = pd.to_numeric(df_editado[c].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
            df_editado["TOTAL"] = df_editado["TOXOIDE"] + df_editado["FIEBRE AMARILLA"] + df_editado["S.R.P"]
            
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
        with open("logo_institucional.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            st.markdown(f'<img src="data:image/jpeg;base64,{encoded_string}" class="logo-custom">', unsafe_allow_html=True)

    st.markdown('<div class="marquee-container"><h2 class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</h2></div>', unsafe_allow_html=True)

    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVO_RESUMEN, dtype=str)
        st.subheader("📊ATENCIONES")
        strat_cols = ["SISTEMA DE SALUD TRADICIONAL", "HOSP. DE CAMPAÑA NACIONALES", 
                      "HOSP. DE CAMPAÑA INTERNACIONALES", "CAMP. TRANSITORIOS"]
        c_strat = st.columns(4)
        for i, campo in enumerate(strat_cols):
            val = df[campo].iloc[0] if campo in df.columns else "0"
            c_strat[i].markdown(f'''
            <div class="strat-card">
                <div class="strat-title">{campo}</div>
                <div class="strat-value">{val}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.subheader("🏥RESUMEN OPERATIVO")
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "⚰️", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        cols_mostrar = ["ATENCIONES", "ALTAS MÉDICAS", "FALLECIDOS", "TRASLADOS", "CAMAS OCUPADAS", "CAMAS DISPONIBLES", "HOSPITALIZACIONES", "INMUNIZACIONES", "INTERVENCIONES Q."]
        cols = st.columns(4)
        idx = 0
        for col_name in cols_mostrar:
            if col_name in df.columns:
                with cols[idx % 4]:
                    st.markdown(f'<div class="compact-card"><div class="card-title">{iconos.get(col_name, "📊")} {col_name}</div><div class="card-value">{df[col_name].iloc[0]}</div></div>', unsafe_allow_html=True)
                idx += 1
        
        st.subheader("📍UBICACIONES EN TIEMPO REAL")
        st.components.v1.html("""
            <div id="map-container-general" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
                <button onclick="toggleFS('map-container-general')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                    ⛶ Pantalla Completa
                </button>
                <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" 
                        width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
            </div>
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
        """, height=510)

    elif seleccion == "Inmunización":
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            df_detalle = pd.read_csv(archivo_detalle, dtype=str).fillna("0")
            cols_vacunas = ["TOXOIDE", "FIEBRE AMARILLA", "S.R.P", "TOTAL"]
            sumas = {}
            for v in cols_vacunas:
                sumas[v] = pd.to_numeric(df_detalle[v].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0).sum() if v in df_detalle.columns else 0
            c_vac = st.columns(4)
            for i, v in enumerate(cols_vacunas):
                valor_formateado = f"{int(sumas[v]):,}".replace(",", ".")
                c_vac[i].markdown(f'''
                    <div class="strat-card" style="padding: 15px 5px;">
                        <div class="strat-value" style="font-size: 16px;">{v}: {valor_formateado}</div>
                    </div>
                ''', unsafe_allow_html=True)
            st.write("<br><br>", unsafe_allow_html=True)
            st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif seleccion == "Saneamiento Ambiental":
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            df_detalle = pd.read_csv(archivo_detalle, dtype=str).fillna("0")
            iconos = {
                "DESRATIZACIÓN": "🐀", "FUMIGACIÓN": "💨", 
                "DESINFECCIÓN Y ABATIZACIÓN": "🪣", "DESPARASITACIÓN": "💊", 
                "PERSONAS PROTEGIDAS": "🛡️"
            }
            campos = ["DESRATIZACIÓN", "FUMIGACIÓN", "DESINFECCIÓN Y ABATIZACIÓN", "DESPARASITACIÓN", "PERSONAS PROTEGIDAS"]
            c_sane = st.columns(3)
            for i, campo in enumerate(campos):
                val = df_detalle[campo].iloc[0] if campo in df_detalle.columns else "0"
                c_sane[i % 3].markdown(f'''
                    <div class="strat-card" style="padding: 15px 5px;">
                        <div class="strat-title" style="font-size: 13px;">{iconos.get(campo, "📊")} {campo}</div>
                        <div class="strat-value" style="font-size: 22px; margin-top: 5px;">{val}</div>
                    </div>
                ''', unsafe_allow_html=True)
            st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

   st.markdown("### 📍Ubicación En Tiempo Real")
            html_mapa = """
<div id="map-container-ruta" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
    <button onclick="toggleFS('map-container-ruta')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ⛶ Pantalla Completa
    </button>
    <iframe src="https://www.google.com/maps/d/embed?mid=1yl45t_HdDytdAAzsaOcMJzM3ICa5bPk" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
</div>
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
            st.components.v1.html(html_mapa, height=510)
                    function toggleFS(id) { 
                        var elem = document.getElementById(id); 
                        if (!document.fullscreenElement) { 
                            elem.requestFullscreen().catch(err => alert("Error: " + err.message)); 
                        } else { 
                            document.exitFullscreen(); 
                        } 
                    }
                </script>
            """, height=510)
            
            st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("Aún no se han cargado datos en esta sección.")

    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        archivo_detalle = f"{seleccion.lower().replace(' ', '_')}.csv"
        if os.path.exists(archivo_detalle):
            df_detalle = pd.read_csv(archivo_detalle, dtype=str)
            df_detalle = df_detalle.replace('None', pd.NA).dropna(how='all')
            if seleccion == "Campamentos Transitorios": orden = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS"]
            else: orden = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIAD", "PAIS RESPONSABLE", "ATENCIONES"]
            df_detalle = df_detalle.reindex(columns=orden)
            if seleccion == "Hospitales de Campaña" and "NACIONALIAD" in df_detalle.columns and "ATENCIONES" in df_detalle.columns:
                df_stats = df_detalle.copy()
                df_stats['ATENCIONES'] = pd.to_numeric(df_stats['ATENCIONES'].astype(str).str.replace('.', '', regex=False), errors='coerce').fillna(0)
                df_stats['NACIONALIAD'] = df_stats['NACIONALIAD'].astype(str).str.upper().str.strip()
                resumen = df_stats.groupby('NACIONALIAD')['ATENCIONES'].sum()
                suma_nac = resumen.get('NACIONAL', 0)
                suma_ext = resumen.get('EXTRANJERO', 0) + resumen.get('ESTRANJERO', 0)
                cols = st.columns(2)
                cols[0].metric("Total Atenciones NACIONALES", f"{int(suma_nac):,}".replace(",", "."))
                cols[1].metric("Total Atenciones EXTRANJEROS", f"{int(suma_ext):,}".replace(",", "."))
                st.dataframe(df_detalle, use_container_width=True, hide_index=True)
                if (suma_nac + suma_ext) > 0:
                    fig = go.Figure(data=[go.Pie(labels=['NACIONAL', 'EXTRANJERO'], values=[suma_nac, suma_ext], hole=.6, marker_colors=['#FF0000', '#002060'], textinfo='none')])
                    fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(t=20, b=80, l=20, r=20))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df_detalle, use_container_width=True, hide_index=True)
            st.download_button("📥 Descargar Reporte en Excel", data=convertir_df_a_excel(df_detalle), file_name=f"{seleccion}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
