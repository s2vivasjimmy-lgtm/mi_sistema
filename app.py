import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Puesto de Comando", layout="wide")

# --- ARCHIVO DE DATOS LOCAL ---
ARCHIVO_DATOS = "mis_datos.csv"

def inicializar_datos():
    if not os.path.exists(ARCHIVO_DATOS):
        # Datos iniciales si no existe el archivo
        data = {"ATENCIONES": ["0"], "ALTAS MÉDICAS": ["0"], "FALLECIDOS": ["0"], 
                "TRASLADOS": ["0"], "CAMAS OCUPADAS": ["0"], "CAMAS DISPONIBLES": ["0"],
                "HOSPITALIZACIONES": ["0"], "INMUNIZACIONES": ["0"], "INTERVENCIONES Q.": ["0"]}
        pd.DataFrame(data).to_csv(ARCHIVO_DATOS, index=False)

inicializar_datos()

# --- LÓGICA DE ACCESO ---
def check_password():
    def password_entered():
        if st.session_state["username"] == "Admin" and st.session_state["password"] == "diges12..":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: white;'>Acceso al Puesto de Comando</h2>", unsafe_allow_html=True)
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password", on_change=password_entered)
        return False
    return st.session_state["password_correct"]

# --- INTERFAZ ---
if check_password():
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117 !important; }
        #MainMenu, footer, header { visibility: hidden !important; }
        .full-width-logo { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; margin-bottom: 25px; }
        .moving-title { width: 100%; overflow: hidden; white-space: nowrap; font-size: 1.8rem; font-weight: 700; color: #ffffff; margin: 30px 0; border-top: 1px solid #4a90e2; border-bottom: 1px solid #4a90e2; padding: 12px 0; }
        .moving-title span { display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite; }
        @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
        </style>
    """, unsafe_allow_html=True)

    # Navegación
    menu = st.sidebar.radio("Menú", ["Vista de Comando", "Panel de Registros"])

    if menu == "Vista de Comando":
        if os.path.exists("logo_institucional.jpg"):
            st.markdown('<div class="full-width-logo">', unsafe_allow_html=True)
            st.image("logo_institucional.jpg", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="moving-title"><span>AUTORIDAD ÚNICA DE SALUD MILITAR DEL ESTADO LA GUAIRA</span></div>', unsafe_allow_html=True)

        df = pd.read_csv(ARCHIVO_DATOS, dtype=str)
        iconos = {"ATENCIONES": "📋", "ALTAS MÉDICAS": "✅", "FALLECIDOS": "🥀", "TRASLADOS": "🚑", "CAMAS OCUPADAS": "🛌", "CAMAS DISPONIBLES": "🛏️", "HOSPITALIZACIONES": "🏥", "INMUNIZACIONES": "💉", "INTERVENCIONES Q.": "🔪"}
        
        cols = st.columns(3)
        for i, col in enumerate(df.columns):
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background-color: #1a1c23; padding: 20px; border-radius: 12px; border: 1px solid #31333f; margin-bottom: 20px; color: white;">
                        <div style="font-size: 14px; text-transform: uppercase; color: #b0b3b8;">{iconos.get(col, '📊')} {col}</div>
                        <div style="font-size: 28px; font-weight: 800;">{df[col].iloc[0]}</div>
                    </div>
                """, unsafe_allow_html=True)

    else:
        st.header("📝 Panel de Registros")
        df_actual = pd.read_csv(ARCHIVO_DATOS, dtype=str)
        # Editor interactivo
        df_editado = st.data_editor(df_actual, use_container_width=True)
        
        if st.button("Guardar Cambios"):
            df_editado.to_csv(ARCHIVO_DATOS, index=False)
            st.success("¡Datos guardados con éxito!")
            st.rerun()

    # Mapa (Visible en ambos)
    st.subheader("📍 Mapa de Afectaciones")
    st.components.v1.html("""
    <div id="map-container" style="position: relative; width: 100%; height: 500px; border: 1px solid #31333f; border-radius: 12px; overflow: hidden;">
        <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" width="100%" height="100%" frameborder="0"></iframe>
    </div>
    """, height=510)
