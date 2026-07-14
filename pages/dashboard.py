import streamlit as st
import time

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("🛡️ Monitoreo de Gestión de Salud")

datos = [
    ("Atenciones", "1.240"), ("Altas Médicas", "950"), ("Fallecidos", "12"),
    ("Traslados", "45"), ("Camas Ocupadas", "320"), ("Camas Disponibles", "85"),
    ("Hospitalizaciones", "210"), ("Inmunizaciones", "540"), ("Intervenciones Q.", "35")
]

for i in range(0, 9, 3):
    cols = st.columns(3)
    for j in range(3):
        with cols[j]:
            titulo, valor = datos[i+j]
            st.markdown(f"""
                <div style="background-color: #1c202a; padding: 20px; border-radius: 10px; border: 1px solid #31333F; margin-bottom: 10px;">
                    <div style="color: #808495; font-size: 14px; text-transform: uppercase;">{titulo}</div>
                    <div style="color: #ffffff; font-size: 28px; font-weight: bold;">{valor}</div>
                </div>
            """, unsafe_allow_html=True)

st.subheader("📍 Mapa de Afectaciones")
url_mapa = f"https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&t={time.time()}"
st.components.v1.iframe(url_mapa, width=1200, height=500)
