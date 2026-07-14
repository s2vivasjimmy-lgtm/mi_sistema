import streamlit as st
import pandas as pd
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Sala Situacional", layout="wide")

url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_Np_DS4r1_ICdu3Yh0Xh41cH_vTf2KMABcRVbB1Vfowe5IBcf3ty7ulOnyfplAJiFwMRjxGmzuWc7/pub?output=csv"

# Diccionario de íconos SVG para máxima compatibilidad
svg_icons = {
    "ATENCIONES": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>',
    "ALTAS MÉDICAS": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    "FALLECIDOS": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>',
    "TRASLADOS": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M20 8h-3V6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z"/></svg>',
    "CAMAS OCUPADAS": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M20 10V7c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v3c-1.1 0-2 .9-2 2v5h1.33L4 19h1l.67-2h10.66L17 19h1l.67-2H22v-5c0-1.1-.9-2-2-2zm-2 5H6v-3h12v3z"/></svg>',
    "CAMAS DISPONIBLES": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M11 11V5h2v6h6v2h-6v6h-2v-6H5v-2h6z"/></svg>',
    "HOSPITALIZACIONES": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/></svg>',
    "INMUNIZACIONES": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M18.54 9l1.41-1.41-1.13-1.13-1.41 1.41-1.41-1.41-1.13 1.13L16.3 9l-3.54 3.54 4.24 4.24 3.54-3.54-1.13-1.13-1.41 1.41-1.41-1.41-1.13-1.13L16.3 9zM6 18.77l9.19-9.19 1.41 1.41L7.41 20.18 6 18.77z"/></svg>',
    "INTERVENCIONES Q.": '<svg viewBox="0 0 24 24" width="30" height="30" fill="#4a90e2"><path d="M14.59 7.41L18 10.83l-1.41 1.41-3.41-3.42L14.59 7.41zM11 12.24l-3.76 3.76-1.41-1.41L9.59 10.83 11 12.24z"/></svg>'
}

st.title("🛡️ Monitoreo de Gestión de Salud")

try:
    df = pd.read_csv(f"{url}&nocache={time.time()}")
    
    # Renderizado seguro de tarjetas
    html_cards = '<div style="display: flex; flex-wrap: wrap; gap: 20px;">'
    for col in df.columns:
        svg = svg_icons.get(col, "")
        val = df[col].iloc[0]
        html_cards += f"""
        <div style="background:#1c202a; padding:15px; border-radius:12px; border:1px solid #31333F; display:flex; align-items:center; width:320px;">
            {svg}
            <div style="margin-left:15px;">
                <div style="color:#808495; font-size:10px; text-transform:uppercase; font-weight:bold;">{col}</div>
                <div style="color:#ffffff; font-size:22px; font-weight:bold;">{val}</div>
            </div>
        </div>"""
    html_cards += "</div>"
    components.html(html_cards, height=150)
    
    st.caption(f"🕒 Última actualización: {time.strftime('%H:%M:%S')}")

except:
    st.error("Error al cargar los datos.")

st.subheader("📍 Mapa de Afectaciones")

# Mapa con botón de pantalla completa integrado
mapa_html = f"""
<div id="map-container" style="position: relative; width: 100%; height: 550px;">
    <button onclick="document.getElementById('myMap').requestFullscreen()" 
            style="position: absolute; top: 10px; right: 10px; z-index: 999; padding: 10px; cursor: pointer; background: white; border-radius: 5px; border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
        ⛶ Pantalla Completa
    </button>
    <iframe id="myMap" src="https://www.google.com/maps/d/embed?mid=1mOUOQ2t-N_BrEWYqqySXGBW5MQuZQIg&ehbc=2E312F" 
            width="100%" height="100%" frameborder="0" allowfullscreen></iframe>
</div>
"""
components.html(mapa_html, height=560)
