import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="expanded")

# --- CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: block !important; }
    .block-container { padding-top: 1rem !important; }
    .stApp { background-color: #0E1117 !important; }
    h1, h2, h3, h4, h5, h6 { color: #ffffff !important; }
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 15px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 2px; }
    .card-value { font-size: 20px; font-weight: 800; color: #ffffff; }
    .floating-btn-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    </style>
""", unsafe_allow_html=True)

# --- ARCHIVOS ---
ARCHIVOS = {
    "Resumen General": "datos_resumen.csv",
    "Hospitales de Campaña": "datos_hospitales.csv",
    "Campamentos Transitorios": "datos_campamentos.csv",
    "Puntos de Inmunización": "datos_inmunizacion.csv"
}

def inicializar():
    if not os.path.exists(ARCHIVOS["Resumen General"]):
        pd.DataFrame({"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                      "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                      "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}).to_csv(ARCHIVOS["Resumen General"], index=False)
    for cat in ["Hospitales de Campaña", "Campamentos Transitorios", "Puntos de Inmunización"]:
        if not os.path.exists(ARCHIVOS[cat]):
            pd.DataFrame(columns=["Nº", "NOMBRE", "UBICACIÓN", "ESTATUS", "NACIONALIDAD", "PAIS RESPONSABLE"]).to_csv(ARCHIVOS[cat], index=False)

inicializar()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Registros")
    seleccion = st.radio("Seleccionar categoría:", list(ARCHIVOS.keys()))

# --- LÓGICA ---
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

if st.session_state.admin_logueado:
    st.header(f"📝 Edición: {seleccion}")
    archivo = ARCHIVOS[seleccion]
    df = pd.read_csv(archivo, dtype=str)
    df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Guardar"):
        df_editado.to_csv(archivo, index=False)
        st.rerun()
    if st.button("❌ Salir"):
        st.session_state.admin_logueado = False
        st.rerun()
else:
    # Botón acceso admin
    with st.container():
        with st.popover("⚙️"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                if user == "Admin" and pwd == "diges12..":
                    st.session_state.admin_logueado = True
                    st.rerun()

    if seleccion == "Resumen General":
        df = pd.read_csv(ARCHIVOS["Resumen General"], dtype=str)
        cols = st.columns(4)
        for i, col in enumerate(df.columns):
            with cols[i % 4]:
                st.markdown(f'<div class="compact-card"><div class="card-title">{col}</div><div class="card-value">{df[col].iloc[0]}</div></div>', unsafe_allow_html=True)
        
        st.subheader("📍 UBICACIONES EN TIEMPO REAL")
        st.components.v1.html("""
        <div id="map-container" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
            <button onclick="toggleFS()" style="position: absolute; top: 10px; right: 10px; z-index: 1000; padding: 8px 12px; cursor: pointer; background: #ffffff; border: none; border-radius: 5px; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">⛶ Pantalla Completa</button>
            <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
        </div>
        <script>
            function toggleFS() {
                var elem = document.getElementById("map-container");
                if (!document.fullscreenElement) { elem.requestFullscreen(); } else { document.exitFullscreen(); }
            }
        </script>
        """, height=510)
    else:
        st.subheader(f"📊 Detalle: {seleccion}")
        st.table(pd.read_csv(ARCHIVOS[seleccion], dtype=str))
