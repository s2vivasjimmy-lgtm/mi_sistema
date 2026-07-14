import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Sala Situacional", layout="wide")

st.title("📊 Sala Situacional - Panel de Control")

# Definimos las métricas
metricas = [
    "Atenciones", "Altas Medicas", "Fallecidos", 
    "Traslados", "Camas ocupadas", "Camas disponibles", 
    "Hospitalizaciones", "Inmunizaciones", "Intervenciones Quirurgicas"
]

# Creamos 3 filas de 3 columnas cada una
for i in range(0, 9, 3):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=metricas[i], value=0)
    with col2:
        st.metric(label=metricas[i+1], value=0)
    with col3:
        st.metric(label=metricas[i+2], value=0)

st.divider()
st.subheader("Registro de Datos")
