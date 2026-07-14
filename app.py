import streamlit as st
import sqlite3
import pandas as pd

# Configuración de base de datos
conn = sqlite3.connect('mis_datos.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS registros (nombre TEXT, cantidad INTEGER)')
conn.commit()
conn.close()

st.title("Mi Sistema de Registros")
nombre = st.text_input("Nombre del ítem:")
cantidad = st.number_input("Cantidad:", min_value=0, step=1)

if st.button("Guardar"):
    conn = sqlite3.connect('mis_datos.db')
    c = conn.cursor()
    c.execute('INSERT INTO registros VALUES (?, ?)', (nombre, cantidad))
    conn.commit()
    conn.close()
    st.success("Guardado")

st.subheader("Datos")
conn = sqlite3.connect('mis_datos.db')
df = pd.read_sql('SELECT * FROM registros', conn)
st.table(df)
conn.close()