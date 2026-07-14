import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# --- LÓGICA DE ACCESO ---
def check_password():
    def password_entered():
        if st.session_state["username"] == "Admin" and st.session_state["password"] == "diges12..":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: white;'>Acceso al Puesto de Comando</h2>", unsafe_allow_html=True)
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password", on_change=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.error("Usuario o contraseña incorrectos")
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password", on_change=password_entered)
        return False
    else:
        return True

# --- INICIO DE LA APLICACIÓN ---
if check_password():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117 !important; }
        #MainMenu, footer, header { visibility: hidden !important; }
        .full-width-logo {
            width: 100vw; position: relative; left: 50%; right: 50%; 
            margin-left: -50vw; margin-right: -50vw; margin-bottom: 25px;
        }
        .moving-title { 
            width: 100%; overflow: hidden; white-space: nowrap; 
            font-size: 1.8rem; font-weight: 700; color: #ffffff; 
            margin: 30px 0; border-top: 1px solid #4a90e2; 
            border-bottom: 1px solid #4a90e2; padding: 12px 0; 
        }
        .moving-title span { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }
        @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
        </style>
    """, unsafe_allow_html=True)

    ruta_logo = "logo_institucional.jpg"
    if os.path.exists(ruta_logo):
        st.markdown('<div class="full-width-logo">', unsafe_allow_html=True)
        st.image(ruta_logo, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</span></div>', unsafe_allow_html=True)

    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"
    iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛏️", "CAMAS DISPONIBLES": "🛌", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}

    try:
        df = pd.read_csv(f"{url}&nocache={time.time()}")
        cols = st.columns(3)
        for i, col in enumerate(df.columns):
            icono = iconos.get(col, "📊")
            valor = df[col].iloc[0]
            with cols[i % 3]:
                # FORMA ROBUSTA: Icono e información integrados directamente
                st.markdown(f"""
                    <div style="background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #31333f; margin-bottom: 20px; color: white;">
                        <div style="font-size: 14px; text-transform: uppercase; color: #b0b3b8; letter-spacing: 1px;">
                            {icono} {col}
                        </div>
                        <div style="font-size: 28px; font-weight: 800; margin-top: 5px;">
                            {valor}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    except:
        st.error("Error al cargar los datos.")

    st.subheader("📍 Mapa de Afectaciones")
    mapa_html = """
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
    """
    st.components.v1.html(mapa_html, height=510)
