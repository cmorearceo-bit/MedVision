import streamlit as st
import pandas as pd
import numpy as np
import pydicom
import cv2
from PIL import Image
import io
import base64
from database import DatabaseManager
from dicom_handler import DICOMHandler
from utils.image_processing import ImageProcessor
from utils.annotations import AnnotationTool

# Inicialización
db = DatabaseManager()
dicom_handler = DICOMHandler()
image_processor = ImageProcessor()
annotation_tool = AnnotationTool()

# Configuración de la página
st.set_page_config(layout="wide", page_title="MedVision - Visor Médico")

# --- Base de Datos ---
@st.cache_resource
def init_db():
    return db

db = init_db()

# --- Interfaz Principal ---
st.title("MedVision - Visor de Imágenes Médicas")

# --- Panel de Navegación ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.subheader("Pacientes")
    patients = db.get_patients()
    selected_patient = st.selectbox("Seleccionar paciente", patients["name"].tolist())
    
with col2:
    st.subheader("Modalidades")
    modalities = ["RX", "CT", "MRI", "Ultrasound", "General"]
    selected_modality = st.selectbox("Modalidad", modalities)
    
with col3:
    st.subheader("Vistas")
    view_modes = ["1×1", "1×2", "2×2"]
    selected_view = st.selectbox("Modo de vista", view_modes)

# --- Carga de Imágenes ---
st.subheader("Cargar Imágenes")
uploaded_files = st.file_uploader("Subir imágenes (DICOM, JPG, PNG)", 
                               type=["dcm", "jpg", "jpeg", "png"], 
                               accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        # Cargar imagen según tipo de archivo
        image_data = dicom_handler.load_image(file)
        
        # Guardar en la base de datos
        db.save_image(image_data, selected_patient, selected_modality, file_type=file.name.split('.')[-1])

# --- Visualización de Imágenes ---
st.subheader("Visor de Imágenes")
images = db.get_images(selected_patient, selected_modality)

if images:
    # Miniaturas
    cols = st.columns(5)
    for i, img_data in enumerate(images[:5]):
        with cols[i]:
            st.image(img_data["thumbnail"], caption=f"Img {i+1}", use_column_width=True)
    
    # Visor principal
    if selected_view == "1×1":
        st.image(images[0]["image"], use_column_width=True)
    elif selected_view == "1×2":
        col1, col2 = st.columns(2)
        with col1:
            st.image(images[0]["image"], use_column_width=True)
        with col2:
            st.image(images[1]["image"] if len(images) > 1 else images[0]["image"], use_column_width=True)
    else:  # 2×2
        cols = st.columns(2)
        for i in range(4):
            with cols[i % 2]:
                st.image(images[i]["image"] if i < len(images) else images[0]["image"], use_column_width=True)

# --- Herramientas de Visualización ---
st.subheader("Herramientas de Visualización")
col1, col2, col3 = st.columns(3)
with col1:
    brightness = st.slider("Brillo", -100, 100, 0)
with col2:
    contrast = st.slider("Contraste", 0, 200, 100)
with col3:
    colormap = st.selectbox("Mapa de Color", ["Gris", "Calor", "Hueso", "Frío", "Viridis"])

# --- Herramientas de Anotación ---
st.subheader("Herramientas de Anotación")
tool = st.radio("Seleccionar herramienta", ["Regla", "ROI", "Flecha", "Texto"])

if tool == "Regla":
    st.text("Herramienta de medición activada - Arrastrar para medir distancias")
elif tool == "ROI":
    st.text("Herramienta ROI activada - Dibujar regiones de interés")
elif tool == "Flecha":
    st.text("Herramienta de flecha activada - Marcar áreas importantes")

# --- Datos del Paciente ---
st.subheader("Panel del Paciente")
patient_data = db.get_patient_data(selected_patient)
st.json(patient_data)

# --- Comparación Lado a Lado ---
st.subheader("Comparación")
if len(images) >= 2:
    col1, col2 = st.columns(2)
    with col1:
        st.image(images[0]["image"], caption="Imagen 1")
    with col2:
        st.image(images[1]["image"], caption="Imagen 2")

if __name__ == "__main__":
    st.sidebar.title("MedVision")
    st.sidebar.info("Software de Visor Médico")