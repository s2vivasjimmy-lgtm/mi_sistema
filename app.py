import streamlit as st
import pandas as pd
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Puesto de Comando", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PARA EL MODO PANTALLA COMPLETA ---
st.markdown("""
    <style>
    .block-container { padding-top: 0rem !important; }
    .stApp { background-color: #0E1117 !important; }
    #MainMenu, footer, header { visibility: hidden !important; }
    
    .compact-card { background-color: #1a1c23; padding: 10px; border-radius: 8px; border: 1px solid #31333f; color: white; margin-bottom: 5px; text-align: center; }
    .card-title { font-size: 11px; text-transform: uppercase; color: #b0b3b8; font-weight: bold; margin-bottom: 2px; }
    .card-value { font-size: 20px; font-weight: 800; color: #ffffff; }
    .floating-btn-container { position: fixed; top: 10px; left: 10px; z-index: 9999; }
    
    /* Overlay para pantalla completa */
    .fullscreen-overlay {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: #0E1117; z-index: 99999; padding: 20px;
    }
    </style>
""", unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_datos.csv"

# --- LÓGICA DE ESTADO ---
if "mostrar_mapa" not in st.session_state: st.session_state.mostrar_mapa = False
if "admin_logueado" not in st.session_state: st.session_state.admin_logueado = False

# --- LÓGICA DE VISTAS ---
if st.session_state.mostrar_mapa:
    # Capa de pantalla completa
    st.markdown('<div class="fullscreen-overlay">', unsafe_allow_html=True)
    if st.button("⬅️ CERRAR MAPA Y VOLVER"):
        st.session_state.mostrar_mapa = False
        st.rerun()
    st.components.v1.html("""
        <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" 
        width="100%" height="90%" frameborder="0"></iframe>
    """, height=800)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Interfaz Principal
    if st.session_state.admin_logueado:
        st.header("📝 Panel de Edición")
        # ... (Tu lógica de edición se mantiene igual)
    else:
        # Botones y tarjetas (Se mantiene igual)
        if st.button("🌐 VER MAPA EN PANTALLA COMPLETA"):
            st.session_state.mostrar_mapa = True
            st.rerun()
        
        # Mapa principal (reducido)
        st.components.v1.html("""
            <iframe src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg" 
            width="100%" height="400" frameborder="0"></iframe>
        """, height=410)
