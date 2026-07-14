import streamlit as st

st.set_page_config(page_title="Admin", layout="centered")
st.title("⚙️ Panel de Control")

st.warning("Zona restringida. Solo para uso administrativo.")

password = st.text_input("Contraseña", type="password")
if password == "1234":
    st.success("Acceso concedido.")
    st.write("Aquí podrás editar los datos en el futuro.")
elif password != "":
    st.error("Contraseña incorrecta")
