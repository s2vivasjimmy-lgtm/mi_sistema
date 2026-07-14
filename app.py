import streamlit as st

# Configuración de página profesional
st.set_page_config(page_title="Sala Situacional", page_icon="🏥", layout="wide")

# Estilo CSS para que se vea como portal profesional
st.markdown("""
    <style>
    [data-testid="stSidebar"] {background-color: #f8f9fa;}
    .css-1r6slp0 {padding-top: 0rem;}
    </style>
    """, unsafe_allow_html=True)

# SIDEBAR PROFESIONAL
with st.sidebar:
    st.title("🏥 Sala Situacional")
    st.write("---")
    opcion = st.radio("Navegación", ["Panel Principal", "Registrar Datos", "Reportes"])
    st.write("---")
    st.info("Usuario: Administrador")

# LÓGICA DE PÁGINAS
if opcion == "Panel Principal":
    st.title("📊 Panel de Indicadores")
    
    # Tarjetas de resumen (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Atenciones", "124", "+12%")
        st.metric("Camas ocupadas", "45", "80%")
    with col2:
        st.metric("Altas Médicas", "89", "+5%")
        st.metric("Camas disponibles", "15", "-10%")
    with col3:
        st.metric("Fallecidos", "2", "0%")
        st.metric("Hospitalizaciones", "56", "+2%")
        
    st.subheader("Otras métricas")
    c1, c2, c3 = st.columns(3)
    c1.metric("Traslados", "12")
    c2.metric("Inmunizaciones", "205")
    c3.metric("Int. Quirúrgicas", "8")

elif opcion == "Registrar Datos":
    st.title("📝 Registro")
    st.write("Formulario de carga de datos...")
    # Aquí irá tu formulario luego
