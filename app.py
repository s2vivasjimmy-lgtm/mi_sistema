import base64
import datetime
import io
import json
import os
import urllib.request
from github import Github
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Refrescar la aplicación automáticamente cada 5 segundos
st_autorefresh(interval=5000, key="dataview_autorefresh")

st.set_page_config(
    page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded"
)

# --- CSS GENERAL Y OCULTAR "MANAGE APP" ---
st.markdown(
    """
<style>
/* Ocultar la insignia flotante de Manage app / Streamlit Viewer Badge */
.viewerBadge_container__1QSob, 
.styles_viewerBadge__1yB5_, 
[data-testid="stStatusWidget"] {
    display: none !important;
}

button[kind="header"] { display: none !important; }
.block-container { padding-top: 0rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
.stApp { background-color: #0E1117 !important; }

.strat-card { 
    background-color: #2b3a4a; padding: 12px; border-radius: 6px; 
    border-left: 4px solid #00d2ff; text-align: center; margin-bottom: 10px; height: 105px; 
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
    display: inline-block; white-space: nowrap; animation: marquee 15s linear infinite; 
    color: #ffffff !important; font-weight: bold; font-size: 20px; 
}
@keyframes marquee {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}
.logo-custom { width: 100%; height: 90px; object-fit: contain; display: block; margin-left: auto; margin-right: auto; margin-bottom: 2px; }
</style>
""",
    unsafe_allow_html=True,
)


def obtener_hora_red():
  """Obtiene la hora oficial de Venezuela (America/Caracas) desde worldtimeapi, con respaldo en UTC-4."""
  try:
    with urllib.request.urlopen(
        "https://worldtimeapi.org/api/timezone/America/Caracas", timeout=3
    ) as response:
      data = json.loads(response.read().decode())
      datetime_str = data["datetime"]
      dt = datetime.datetime.fromisoformat(datetime_str)
      if dt.tzinfo is not None:
        dt = dt.astimezone(
            datetime.timezone(datetime.timedelta(hours=-4))
        ).replace(tzinfo=None)
      return dt
  except Exception:
    return datetime.datetime.utcnow() - datetime.timedelta(hours=4)


def formatear_fecha_venezuela(dt):
  meses = {
      1: "ENE",
      2: "FEB",
      3: "MAR",
      4: "ABR",
      5: "MAY",
      6: "JUN",
      7: "JUL",
      8: "AGO",
      9: "SEP",
      10: "OCT",
      11: "NOV",
      12: "DIC",
  }
  dia = f"{dt.day:02d}"
  mes = meses.get(dt.month, "AGO")
  anio = dt.year
  hora = dt.strftime("%H:%M:%S")
  return f"{dia}{mes}{anio} - {hora}"


def convertir_df_a_excel(df):
  output = io.BytesIO()
  with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    df.to_excel(writer, index=False, sheet_name="Reporte")
  return output.getvalue()


def formatear_numero(n):
  try:
    return f"{int(str(n).replace('.', '')):,}".replace(",", ".")
  except:
    return str(n)


# --- GENERADOR DE TABLAS HTML PROFESIONALES (TEXTO 100% BLANCO Y LEGIBLE) ---
def renderizar_tabla_html_pro(df):
  if df.empty:
    return (
        "<p style='color: #ffffff; text-align: center;'>No hay registros"
        " disponibles.</p>"
    )

  html = """
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <div class="overflow-x-auto rounded-xl border border-slate-700 bg-slate-950 shadow-2xl my-3">
      <table class="w-full text-left text-sm text-white">
        <thead class="bg-slate-900 text-xs uppercase tracking-wider text-white border-b border-slate-700">
          <tr>
    """

  columnas = list(df.columns)
  for i, col in enumerate(columnas):
    align = (
        "text-center"
        if i == 0 or "ESTATUS" in col or "NACIONALIAD" in col
        else (
            "text-right" if "ATENCIONES" in col or "VALOR" in col else "text-left"
        )
    )
    w_class = "w-16" if i == 0 else ""
    html += (
        f'<th scope="col" class="px-6 py-4 font-bold text-white {align}'
        f' {w_class}">{col}</th>'
    )

  html += """
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800">
    """

  for index, row in df.iterrows():
    html += '<tr class="transition-colors hover:bg-slate-900/80 group">'
    for i, col in enumerate(columnas):
      val = str(row[col]) if pd.notna(row[col]) else ""

      if i == 0:
        html += (
            '<td class="px-6 py-4 text-center font-bold text-white">'
            f'{val.zfill(2) if val.isdigit() else val}</td>'
        )
      elif "ESTATUS" in col.upper():
        if val.upper() == "ACTIVO":
          badge_style = (
              "background-color: rgba(16, 185, 129, 0.3); color: #34d399;"
              " border: 1px solid #34d399;"
          )
        else:
          badge_style = (
              "background-color: rgba(239, 68, 68, 0.3); color: #f87171;"
              " border: 1px solid #f87171;"
          )
        html += (
            '<td class="px-6 py-4 text-center"><span class="inline-flex'
            f' items-center px-3 py-1 rounded-full text-xs font-bold"'
            f' style="{badge_style}">{val}</span></td>'
        )
      elif "ATENCIONES" in col.upper() or "VALOR" in col.upper():
        html += (
            '<td class="px-6 py-4 text-right font-mono text-cyan-300'
            f' font-bold">{formatear_numero(val)}</td>'
        )
      else:
        align_cls = (
            "text-center"
            if "NACIONAL" in col.upper() or "PAIS" in col.upper()
            else "text-left"
        )
        html += f'<td class="px-6 py-4 {align_cls} font-medium text-white">{val}</td>'

    html += "</tr>"

  html += """
        </tbody>
      </table>
    </div>
    """
  return html


ARCHIVO_RESUMEN = "mis_datos.csv"


def guardar_en_github(archivo_local):
  try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["GITHUB_REPO"]
    g = Github(token)
    repo = g.get_repo(repo_name)
    with open(archivo_local, "r", encoding="utf-8") as file:
      contenido = file.read()
    try:
      contents = repo.get_contents(archivo_local)
      repo.update_file(
          contents.path,
          "Actualización datos Puesto Comando",
          contenido,
          contents.sha,
      )
    except:
      repo.create_file(
          archivo_local, "Creación datos Puesto Comando", contenido
      )
    return True
  except Exception as e:
    st.warning(
        "Aviso: Los datos se guardaron localmente, pero falló el respaldo en"
        f" GitHub. (Detalle: {e})"
    )
    return False


if "admin_logueado" not in st.session_state:
  st.session_state.admin_logueado = False


def inicializar_resumen():
  if not os.path.exists(ARCHIVO_RESUMEN):
    data = {
        "ALTAS MÉDICAS": ["0"],
        "FALLECIDOS": ["0"],
        "TRASLADOS": ["0"],
        "CAMAS OCUPADAS": ["0"],
        "CAMAS DISPONIBLES": ["0"],
        "HOSPITALIZACIONES": ["0"],
        "INTERVENCIONES Q.": ["0"],
    }
    pd.DataFrame(data).to_csv(ARCHIVO_RESUMEN, index=False)


inicializar_resumen()

with st.sidebar:
  st.header("📋 Registros")
  seleccion = st.radio(
      "Seleccionar categoría:",
      [
          "Resumen General",
          "Red Sanitaria Militar",
          "Hospitales de Campaña",
          "Sistema de Salud Tradicional",
          "Campamentos Transitorios",
          "Campamentos Itinerantes",
          "Inmunización",
          "Saneamiento Ambiental",
          "Programas de Salud",
          "Ruta Epidemiológica",
          "Daños de Infraestructura",
          "I Jornada Médica",
          "II Jornada Médica",
          "III Jornada Médica",
          "IV Jornada Médica",
      ],
  )

jornadas_map = {
    "I Jornada Médica": ("i", "I"),
    "II Jornada Médica": ("ii", "II"),
    "III Jornada Médica": ("iii", "III"),
    "IV Jornada Médica": ("iv", "IV"),
}

if st.session_state.admin_logueado:
  st.header(f"📝 Edición: {seleccion}")

  if seleccion in jornadas_map:
    suf, num_romano = jornadas_map[seleccion]
    tab_ed1, tab_ed2, tab_ed3 = st.tabs(
        ["🩺 Atenciones por Especialidad", "🤝 Apoyo Social", "👥 Demografía (Personas)"]
    )

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

      df_esp_edit = st.data_editor(
          df_esp.reindex(columns=cols_maestras, fill_value="0"),
          use_container_width=True,
          num_rows="dynamic",
          key=f"esp_{suf}",
      )

      if st.button(
          "💾 Guardar Especialidades y Autosumar", key=f"btn_esp_{suf}"
      ):
        df_esp_edit.to_csv(archivo_esp, index=False)
        try:
          vals_esp = (
              pd.to_numeric(
                  df_esp_edit["ATENCIONES"]
                  .astype(str)
                  .str.replace(".", "", regex=False),
                  errors="coerce",
              )
              .fillna(0)
          )
          suma_especialidades = int(vals_esp.sum())

          if os.path.exists(archivo_meta):
            df_m = pd.read_csv(archivo_meta, dtype=str)
          else:
            df_m = pd.DataFrame(
                {"FECHA_JORNADA": [""], "TOTAL_ATENCIONES": ["0"]}
            )

          dt_red = obtener_hora_red()
          fecha_hora_actualizada = formatear_fecha_venezuela(dt_red)

          df_m.loc[0, "TOTAL_ATENCIONES"] = str(suma_especialidades)
          df_m.loc[0, "FECHA_JORNADA"] = fecha_hora_actualizada
          df_m.to_csv(archivo_meta, index=False)
          guardar_en_github(archivo_meta)
        except Exception as e:
          st.error(f"Error al autosumar y actualizar fecha: {e}")

        guardar_en_github(archivo_esp)
        st.success(
            "¡Especialidades guardadas, Total de Atenciones actualizado a"
            f" {suma_especialidades} y Fecha/Hora sincronizada!"
        )

    with tab_ed2:
      st.markdown(f"### Tabla: Apoyo Social ({seleccion})")
      cols_apoyo = ["Nº", "CATEGORIA_APOYO", "VALOR"]
      if not os.path.exists(archivo_apo):
        pd.DataFrame(columns=cols_apoyo).to_csv(archivo_apo, index=False)
      df_apo = pd.read_csv(archivo_apo, dtype=str)
      df_apo_edit = st.data_editor(
          df_apo.reindex(columns=cols_apoyo, fill_value="0"),
          use_container_width=True,
          num_rows="dynamic",
          key=f"apo_{suf}",
      )

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
        st.success("Apoyo social guardado y hora actualizada.")

    with tab_ed3:
      st.markdown(f"### Desglose Demográfico ({seleccion})")
      if not os.path.exists(archivo_demo):
        pd.DataFrame({
            "MUJERES": ["0"],
            "HOMBRES": ["0"],
            "NIÑAS": ["0"],
            "NIÑOS": ["0"],
        }).to_csv(archivo_demo, index=False)
      df_demo = pd.read_csv(archivo_demo, dtype=str)
      df_demo_edit = st.data_editor(
          df_demo, use_container_width=True, num_rows="fixed", key=f"demo_{suf}"
      )

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
    archivo_a_editar = (
        ARCHIVO_RESUMEN
        if seleccion == "Resumen General"
        else (
            f"{seleccion.lower().replace(' ', '_').replace('\'', '').replace('“', '').replace('”', '')}.csv"
        )
    )

    if seleccion == "Resumen General":
      cols_maestras = [
          "ALTAS MÉDICAS",
          "FALLECIDOS",
          "TRASLADOS",
          "CAMAS OCUPADAS",
          "CAMAS DISPONIBLES",
          "HOSPITALIZACIONES",
          "INTERVENCIONES Q.",
      ]
    elif seleccion == "Red Sanitaria Militar":
      cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "ATENCIONES"]
    elif seleccion == "Campamentos Itinerantes":
      cols_maestras = ["Nº", "NOMBRE", "UBICACIÓN", "RESPONSABLE", "ATENCIONES"]
    elif seleccion in [
        "Campamentos Transitorios",
        "Sistema_de_Salud_Tradicional",
        "Sistema de Salud Tradicional",
        "Inmunización",
        "Saneamiento Ambiental",
        "Programas de Salud",
    ]:
      cols_maestras = ["Nº", "NOMBRE", "ATENCIONES"]
    elif seleccion == "Ruta Epidemiológica":
      cols_maestras = [
          "Nº",
          "GRUPO ETARIO",
          "SEXO",
          "PUNTO/RUTA",
          "DIÁNOSTICO",
          "ACCIONES",
          "RESULTADO",
          "NIVEL DE PRIORIDAD",
          "DIRECCIÓN DEL PACIENTE",
          "TELEFONO",
          "FECHA",
      ]
    else:
      cols_maestras = [
          "Nº",
          "NOMBRE",
          "UBICACIÓN",
          "ESTATUS",
          "NACIONALIAD",
          "PAIS RESPONSABLE",
          "ATENCIONES",
      ]

    if not os.path.exists(archivo_a_editar):
      df_actual = pd.DataFrame(columns=cols_maestras)
    else:
      df_actual = pd.read_csv(archivo_a_editar, dtype=str)
      df_actual = df_actual.loc[:, df_actual.columns.isin(cols_maestras)]
      df_actual = df_actual.dropna(how="all")

    df_editado = st.data_editor(
        df_actual.reindex(columns=cols_maestras, fill_value="0"),
        use_container_width=True,
        num_rows="dynamic",
    )

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
      encoded_string = base64.b64encode(img_bytes).decode("utf-8")
      html_img = (
          f'<img src="data:image/jpeg;base64,{encoded_string}"'
          ' class="logo-custom">'
      )
      st.markdown(html_img, unsafe_allow_html=True)
  except Exception:
    pass

st.markdown(
    '<div class="marquee-container"><h2'
    ' class="marquee-text">AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA'
    " GUAIRA</h2></div>",
    unsafe_allow_html=True,
)

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


if seleccion == "Resumen General":
  st.subheader("🧑‍⚕️ ATENCIONES")

  categorias = {
      "Red Sanitaria Militar": "red_sanitaria_militar.csv",
      "Inmunización": "inmunización.csv",
      "Saneamiento Ambiental": "saneamiento_ambiental.csv",
      "Programas de Salud": "programas_de_salud.csv",
      "Sistema de Salud Tradicional": "sistema_de_salud_tradicional.csv",
      "Campamentos Transitorios": "campamentos_transitorios.csv",
      "Campamentos Itinerantes": "campamentos_itinerantes.csv",
  }

  totales = {}
  total_general = 0

  for cat, archivo in categorias.items():
    val = 0
    if os.path.exists(archivo):
      df_cat = cargar_datos_cache(archivo)
      if not df_cat.empty and "ATENCIONES" in df_cat.columns:
        vals = (
            pd.to_numeric(
                df_cat["ATENCIONES"].astype(str).str.replace(".", "", regex=False),
                errors="coerce",
            )
            .fillna(0)
        )
        val = int(vals.sum())
    totales[cat] = val
    total_general += val

  hosp_nac = 0
  hosp_ext = 0
  archivo_hosp = "hospitales_de_campaña.csv"
  if os.path.exists(archivo_hosp):
    df_hosp = cargar_datos_cache(archivo_hosp)
    if (
        not df_hosp.empty
        and "ATENCIONES" in df_hosp.columns
        and "NACIONALIAD" in df_hosp.columns
    ):
      df_hosp["ATENCIONES"] = (
          pd.to_numeric(
              df_hosp["ATENCIONES"].astype(str).str.replace(".", "", regex=False),
              errors="coerce",
          )
          .fillna(0)
      )
      df_hosp["NACIONALIAD"] = (
          df_hosp["NACIONALIAD"].astype(str).str.upper().str.strip()
      )
      resumen = df_hosp.groupby("NACIONALIAD")["ATENCIONES"].sum()
      hosp_nac = int(resumen.get("NACIONAL", 0))
      hosp_ext = int(resumen.get("EXTRANJERO", 0))

  totales["Red Sanitaria Militar"] = totales.get("Red Sanitaria Militar", 0)
  totales["HOSP. DE CAMPAÑA NACIONALES"] = hosp_nac
  totales["HOSP. DE CAMPAÑA INTERNACIONALES"] = hosp_ext
  totales["Sistema de Salud Tradicional"] = totales.get(
      "Sistema de Salud Tradicional", 0
  )
  totales["Campamentos Transitorios"] = totales.get(
      "Campamentos Transitorios", 0
  )
  totales["Campamentos Itinerantes"] = totales.get("Campamentos Itinerantes", 0)
  totales["Inmunización"] = totales.get("Inmunización", 0)
  totales["Saneamiento Ambiental"] = totales.get("Saneamiento Ambiental", 0)
  totales["Programas de Salud"] = totales.get("Programas de Salud", 0)

  total_general += hosp_nac + hosp_ext

  orden_tarjetas = [
      "Red Sanitaria Militar",
      "HOSP. DE CAMPAÑA NACIONALES",
      "HOSP. DE CAMPAÑA INTERNACIONALES",
      "Sistema de Salud Tradicional",
      "Campamentos Transitorios",
      "Campamentos Itinerantes",
      "Inmunización",
      "Saneamiento Ambiental",
      "Programas de Salud",
  ]

  fila1 = orden_tarjetas[:4]
  fila2 = orden_tarjetas[4:]

  cols1 = st.columns(4)
  for i, cat in enumerate(fila1):
    with cols1[i]:
      st.markdown(
          f"""
           <div class="strat-card">
               <div class="strat-title">{cat.upper()}</div>
               <div class="strat-value">{formatear_numero(totales.get(cat, 0))}</div>
           </div>
           """,
          unsafe_allow_html=True,
      )

  cols2 = st.columns(len(fila2) if len(fila2) > 0 else 4)
  for i, cat in enumerate(fila2):
    with cols2[i]:
      st.markdown(
          f"""
           <div class="strat-card">
               <div class="strat-title">{cat.upper()}</div>
               <div class="strat-value">{formatear_numero(totales.get(cat, 0))}</div>
           </div>
           """,
          unsafe_allow_html=True,
      )

  st.markdown(
      f"""
    <div style="text-align: center; margin: 15px 0;">
        <div class="total-card" style="width: 50%; margin: auto;">
            <div class="total-title">TOTAL ATENCIONES</div>
            <div class="total-value">{formatear_numero(total_general)}</div>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.subheader("🏥 RESUMEN OPERATIVO")
  df = cargar_datos_cache(ARCHIVO_RESUMEN)
  iconos = {
      "ALTAS MÉDICAS": "✅",
      "TRASLADOS": "🚑",
      "CAMAS OCUPADAS": "🛌",
      "CAMAS DISPONIBLES": "🛏️",
      "INTERVENCIONES Q.": "🔪",
  }
  cols_mostrar = [
      "ALTAS MÉDICAS",
      "TRASLADOS",
      "CAMAS OCUPADAS",
      "CAMAS DISPONIBLES",
      "INTERVENCIONES Q.",
  ]

  cols = st.columns(4)
  idx = 0
  for col_name in cols_mostrar:
    if not df.empty and col_name in df.columns:
      with cols[idx % 4]:
        st.markdown(
            f'<div class="compact-card"><div class="card-title">'
            f'{iconos.get(col_name, "📊")} {col_name}</div><div'
            f' class="card-value">{df[col_name].iloc[0]}</div></div>',
            unsafe_allow_html=True,
        )
      idx += 1

  st.subheader("📍UBICACIONES EN TIEMPO REAL")
  st.components.v1.html(
      f"""
        <div id="map-container-general" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS('map-container-general')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ⛶ Pantalla Completa
            </button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
        </div>
        {js_fullscreen}
    """,
      height=510,
  )

elif seleccion == "Ruta Epidemiológica":
  st.subheader(f"📋 Detalle: {seleccion}")
  archivo_detalle = "ruta_epidemiológica.csv"
  if os.path.exists(archivo_detalle):
    df_detalle = cargar_datos_cache(archivo_detalle)

    if not df_detalle.empty:
      st.markdown(
          f"""
           <div class="total-tab">
               <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">TOTAL REGISTROS {seleccion.upper()}: </span>
               <span style="color: #ffffff; font-size: 20px; font-weight: 900; margin-left: 10px;">{formatear_numero(len(df_detalle))}</span>
           </div>
           """,
          unsafe_allow_html=True,
      )

    st.components.v1.html(
        renderizar_tabla_html_pro(df_detalle), height=350, scrolling=True
    )

    st.download_button(
        "📥 Descargar Reporte en Excel",
        data=convertir_df_a_excel(df_detalle),
        file_name=f"{seleccion}.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )

  st.markdown("### 📍UBICACIÓN DEL PACIENTE")
  st.components.v1.html(
      f"""
        <div id="map-container-ruta" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS('map-container-ruta')" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
                ⛶ Pantalla Completa
            </button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1yl45t_HdDytdAAzsaOcMJzM3ICa5bPk" width="100%" height="100%" frameborder="0" allowfullscreen="true" allow="fullscreen"></iframe>
        </div>
        {js_fullscreen}
    """,
      height=510,
  )

elif seleccion == "Hospitales de Campaña":
  st.markdown(
      """
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #00d2ff; padding-bottom: 8px; margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800;">📊 REGISTROS INSTITUCIONALES: <span style="color: #00d2ff;">HOSPITALES DE CAMPAÑA</span></h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

  archivo_cat = "hospitales_de_campaña.csv"
  if os.path.exists(archivo_cat):
    df_cat_vista = cargar_datos_cache(archivo_cat)
    if not df_cat_vista.empty:
      if "ATENCIONES" in df_cat_vista.columns:
        df_cat_vista["ATENCIONES_NUM"] = (
            pd.to_numeric(
                df_cat_vista["ATENCIONES"]
                .astype(str)
                .str.replace(".", "", regex=False),
                errors="coerce",
            )
            .fillna(0)
        )
      else:
        df_cat_vista["ATENCIONES_NUM"] = 0

      if "NACIONALIAD" in df_cat_vista.columns:
        df_cat_vista["NACIONALIAD_LOWER"] = (
            df_cat_vista["NACIONALIAD"].astype(str).str.upper().str.strip()
        )
      else:
        df_cat_vista["NACIONALIAD_LOWER"] = ""

      val_total = int(df_cat_vista["ATENCIONES_NUM"].sum())
      val_nac = int(
          df_cat_vista[df_cat_vista["NACIONALIAD_LOWER"] == "NACIONAL"][
              "ATENCIONES_NUM"
          ].sum()
      )
      val_ext = int(
          df_cat_vista[df_cat_vista["NACIONALIAD_LOWER"] == "EXTRANJERO"][
              "ATENCIONES_NUM"
          ].sum()
      )

      tab_h1, tab_h2, tab_h3 = st.tabs(
          ["TOTAL ATENCIONES", "NACIONALES", "EXTRANJEROS"]
      )

      cols_limpias = [
          c
          for c in df_cat_vista.columns
          if c not in ["ATENCIONES_NUM", "NACIONALIAD_LOWER"]
      ]

      with tab_h1:
        st.markdown(
            f"""
             <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                 <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
                     <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">TOTAL ATENCIONES</span>
                     <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{formatear_numero(val_total)}</span>
                 </div>
             </div>
             """,
            unsafe_allow_html=True,
        )

        st.components.v1.html(
            renderizar_tabla_html_pro(df_cat_vista[cols_limpias]),
            height=380,
            scrolling=True,
        )

      with tab_h2:
        st.markdown(
            f"""
             <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                 <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
                     <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">NACIONALES</span>
                     <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{formatear_numero(val_nac)}</span>
                 </div>
             </div>
             """,
            unsafe_allow_html=True,
        )

        df_nac_filtrado = df_cat_vista[
            df_cat_vista["NACIONALIAD_LOWER"] == "NACIONAL"
        ]
        st.components.v1.html(
            renderizar_tabla_html_pro(df_nac_filtrado[cols_limpias]),
            height=320,
            scrolling=True,
        )

      with tab_h3:
        st.markdown(
            f"""
             <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                 <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
                     <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">EXTRANJEROS</span>
                     <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{formatear_numero(val_ext)}</span>
                 </div>
             </div>
             """,
            unsafe_allow_html=True,
        )

        df_ext_filtrado = df_cat_vista[
            df_cat_vista["NACIONALIAD_LOWER"] == "EXTRANJERO"
        ]
        st.components.v1.html(
            renderizar_tabla_html_pro(df_ext_filtrado[cols_limpias]),
            height=250,
            scrolling=True,
        )

      col_dl1, col_dl2 = st.columns([2, 8])
      with col_dl1:
        st.download_button(
            "📥 Descargar Reporte en Excel",
            data=convertir_df_a_excel(df_cat_vista),
            file_name="Hospitales_de_Campana.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
        )
    else:
      st.info(
          "No hay registros guardados actualmente en Hospitales de Campaña."
      )
  else:
    st.info(
        "Aún no se ha creado el archivo de datos para Hospitales de Campaña."
    )

elif seleccion in jornadas_map:
  suf, num_romano = jornadas_map[seleccion]
  st.markdown(
      f"""
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #00d2ff; padding-bottom: 8px; margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800;">📊 REGISTROS INSTITUCIONALES: <span style="color: #00d2ff;">{seleccion.upper()}</span></h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

  archivo_esp = f"{suf}_especialidades_venezuela_renace.csv"
  archivo_apo = f"{suf}_apoyo_social_venezuela_renace.csv"
  archivo_demo = f"{suf}_demografia_venezuela_renace.csv"
  archivo_meta = f"{suf}_meta_venezuela_renace.csv"

  # Cargar metadatos si existen para mostrar la última fecha y total sincronizados
  total_atenciones_jornada = 0
  fecha_actualizacion_jornada = "Sin registrar"
  if os.path.exists(archivo_meta):
    try:
      df_meta_v = pd.read_csv(archivo_meta, dtype=str)
      if not df_meta_v.empty:
        total_atenciones_jornada = formatear_numero(
            df_meta_v.loc[0, "TOTAL_ATENCIONES"]
            if "TOTAL_ATENCIONES" in df_meta_v.columns
            else "0"
        )
        fecha_actualizacion_jornada = (
            df_meta_v.loc[0, "FECHA_JORNADA"]
            if "FECHA_JORNADA" in df_meta_v.columns
            else "Sin registrar"
        )
    except:
      pass

  st.markdown(
      f"""
    <div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
        <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
            <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">TOTAL ATENCIONES ({num_romano} JORNADA)</span>
            <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{total_atenciones_jornada}</span>
        </div>
        <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #31333f; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
            <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">📅 FECHA Y HORA DE ACTUALIZACIÓN</span>
            <span style="color: #00d2ff; font-size: 18px; font-weight: 800;">{fecha_actualizacion_jornada}</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  tab_v1, tab_v2, tab_v3 = st.tabs(
      [
          "🩺 Atenciones por Especialidad",
          "🤝 Apoyo Social",
          "👥 Demografía (Personas)",
      ]
  )

  with tab_v1:
    st.markdown("### Atenciones por Especialidad")
    if os.path.exists(archivo_esp):
      df_esp_v = cargar_datos_cache(archivo_esp)
      if not df_esp_v.empty:
        st.components.v1.html(
            renderizar_tabla_html_pro(df_esp_v), height=350, scrolling=True
        )
        st.download_button(
            "📥 Descargar Especialidades en Excel",
            data=convertir_df_a_excel(df_esp_v),
            file_name=f"{seleccion}_Especialidades.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            key=f"dl_esp_{suf}",
        )
      else:
        st.info("No hay registros de especialidades cargados.")
    else:
      st.info("Aún no se ha creado el archivo de especialidades.")

  with tab_v2:
    st.markdown("### Apoyo Social")
    if os.path.exists(archivo_apo):
      df_apo_v = cargar_datos_cache(archivo_apo)
      if not df_apo_v.empty:
        st.components.v1.html(
            renderizar_tabla_html_pro(df_apo_v), height=350, scrolling=True
        )
        st.download_button(
            "📥 Descargar Apoyo Social en Excel",
            data=convertir_df_a_excel(df_apo_v),
            file_name=f"{seleccion}_Apoyo_Social.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            key=f"dl_apo_{suf}",
        )
      else:
        st.info("No hay registros de apoyo social cargados.")
    else:
      st.info("Aún no se ha creado el archivo de apoyo social.")

  with tab_v3:
    st.markdown("### Desglose Demográfico")
    if os.path.exists(archivo_demo):
      df_demo_v = cargar_datos_cache(archivo_demo)
      if not df_demo_v.empty:
        st.components.v1.html(
            renderizar_tabla_html_pro(df_demo_v), height=200, scrolling=False
        )
        st.download_button(
            "📥 Descargar Demografía en Excel",
            data=convertir_df_a_excel(df_demo_v),
            file_name=f"{seleccion}_Demografia.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            key=f"dl_demo_{suf}",
        )
      else:
        st.info("No hay registros demográficos cargados.")
    else:
      st.info("Aún no se ha creado el archivo demográfico.")

elif seleccion not in jornadas_map:
  st.markdown(
      f"""
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #00d2ff; padding-bottom: 8px; margin-bottom: 20px;">
        <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800;">📊 REGISTROS INSTITUCIONALES: <span style="color: #00d2ff;">{seleccion.upper()}</span></h2>
    </div>
    """,
      unsafe_allow_html=True,
  )

  archivo_cat = f"{seleccion.lower().replace(' ', '_').replace('\'', '').replace('“', '').replace('”', '')}.csv"

  if os.path.exists(archivo_cat):
    df_cat_vista = cargar_datos_cache(archivo_cat)

    if not df_cat_vista.empty:
      suma_atenciones_cat = 0
      if "ATENCIONES" in df_cat_vista.columns:
        vals_cat = (
            pd.to_numeric(
                df_cat_vista["ATENCIONES"]
                .astype(str)
                .str.replace(".", "", regex=False),
                errors="coerce",
            )
            .fillna(0)
        )
        suma_atenciones_cat = int(vals_cat.sum())

      st.markdown(
          f"""
           <div style="display: flex; gap: 15px; margin-bottom: 15px;">
               <div style="background: linear-gradient(135deg, #1f3044 0%, #16222a 100%); padding: 12px 20px; border-radius: 8px; border: 1px solid #00d2ff; box-shadow: 0 4px 10px rgba(0,210,255,0.2);">
                   <span style="color: #b0b3b8; font-size: 12px; font-weight: bold; text-transform: uppercase; display: block;">TOTAL ATENCIONES</span>
                   <span style="color: #ffffff; font-size: 26px; font-weight: 900;">{formatear_numero(suma_atenciones_cat)}</span>
               </div>
           </div>
           """,
          unsafe_allow_html=True,
      )

      st.components.v1.html(
          renderizar_tabla_html_pro(df_cat_vista), height=380, scrolling=True
      )

      col_dl1, col_dl2 = st.columns([2, 8])
      with col_dl1:
        st.download_button(
            "📥 Descargar Reporte en Excel",
            data=convertir_df_a_excel(df_cat_vista),
            file_name=f"{seleccion.replace(' ', '_')}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            use_container_width=True,
        )
    else:
      st.info(f"No hay registros guardados actualmente en {seleccion}.")
  else:
    st.info(
        f"Aún no se ha creado el archivo de datos para {seleccion}. Puede"
        " agregarlos desde el panel de administración."
    )
