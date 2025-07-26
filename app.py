import streamlit as st
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import pandas as pd
import os

# Librerías para Google Sheets
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image

# --- CONFIG GOOGLE SHEETS ---
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Pon aquí el nombre exacto del JSON que descargaste
SPREADSHEET_ID ='1wa7-hNnzUcfdkE1tbTjUg6oWHzmLxl6GxbwfcdZvIhg'  # Aquí va el ID de tu hoja de cálculo

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# --- STREAMLIT APP ---

st.title("🏏 Entrenamiento de Béisbol - Firma de Asistencia")

hoy = datetime.now().strftime('%Y-%m-%d')
st.subheader(f"Fecha: {hoy}")

nombre = st.text_input("Nombre completo")
categoria = st.selectbox("Categoría", ["Infantil", "Juvenil", "Mayor"])
asistio = st.radio("¿Asistió hoy al entrenamiento?", ["Sí", "No"])

st.markdown("### Firma aquí abajo:")

canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#ffffff",
    height=150,
    width=400,
    drawing_mode="freedraw",
    key="canvas",
)

def guardar_firma_y_subir():
    if not os.path.exists("firmas"):
        os.makedirs("firmas")

    fecha_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    firma_path = f"firmas/{nombre.replace(' ', '_')}_{fecha_hora}.png"
    img = Image.fromarray((canvas_result.image_data[:, :, :3]).astype("uint8"))
    img.save(firma_path)
    return firma_path

def escribir_google_sheets(fila):
    try:
        values = [[fila["Fecha"], fila["Nombre"], fila["Categoría"], fila["Asistió"], fila["FirmaArchivo"]]]
        body = {'values': values}
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="A:E",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return True
    except HttpError as error:
        st.error(f"Error al guardar en Google Sheets: {error}")
        return False

if st.button("✅ Registrar asistencia con firma"):
    if not nombre.strip():
        st.error("⚠️ Por favor ingrese su nombre.")
    elif canvas_result.image_data is None:
        st.error("⚠️ Por favor firme en el recuadro.")
    else:
        firma_guardada = guardar_firma_y_subir()
        fila = {
            "Fecha": hoy,
            "Nombre": nombre,
            "Categoría": categoria,
            "Asistió": asistio,
            "FirmaArchivo": firma_guardada
        }
        if escribir_google_sheets(fila):
            st.success("✅ Asistencia y firma guardadas correctamente.")
