import pydicom
import numpy as np
import cv2
from PIL import Image
import io

class DICOMHandler:
    def __init__(self):
        pass
    
    def load_image(self, file):
        """Cargar archivo (DICOM o JPEG/PNG)"""
        if file.name.lower().endswith('.dcm'):
            return self.load_dicom(file)
        else:
            return self.load_standard_image(file)
    
    def load_dicom(self, file_path):
        """Cargar archivo DICOM"""
        dicom_data = pydicom.dcmread(file_path)
        return dicom_data
    
    def load_standard_image(self, file):
        """Cargar imagen JPEG/PNG"""
        image = Image.open(file)
        # Convertir a numpy array
        image_array = np.array(image)
        # Si es imagen en color, convertir a escala de grises
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        return image_array
    
    def convert_to_numpy(self, image_data):
        """Convertir datos a array numpy"""
        if isinstance(image_data, pydicom.dataset.FileDataset):
            # Es DICOM
            image_array = image_data.pixel_array
            # Aplicar ventana/nivel si está disponible
            if hasattr(image_data, 'WindowCenter') and hasattr(image_data, 'WindowWidth'):
                window_center = image_data.WindowCenter
                window_width = image_data.WindowWidth
                
                if isinstance(window_center, pydicom.multival.MultiValue):
                    window_center = window_center[0]
                if isinstance(window_width, pydicom.multival.MultiValue):
                    window_width = window_width[0]
                    
                image_array = self.apply_window_level(image_array, window_center, window_width)
        else:
            # Es JPEG/PNG
            image_array = image_data
            
        return image_array
    
    def apply_window_level(self, image, center, width):
        """Aplicar ventana y nivel a la imagen"""
        img_min = center - width / 2
        img_max = center + width / 2
        windowed_img = np.clip(image, img_min, img_max)
        windowed_img = (windowed_img - img_min) / (img_max - img_min)
        windowed_img = (windowed_img * 255).astype(np.uint8)
        return windowed_img
    
    def apply_colormap(self, image, colormap="gray"):
        """Aplicar mapa de color"""
        colormaps = {
            "gray": cv2.COLORMAP_GRAY,
            "calor": cv2.COLORMAP_HOT,
            "hueso": cv2.COLORMAP_BONE,
            "frío": cv2.COLORMAP_COOL,
            "viridis": cv2.COLORMAP_VIRIDIS
        }
        
        if colormap in colormaps:
            colored_img = cv2.applyColorMap(image, colormaps[colormap])
            return colored_img
        return image