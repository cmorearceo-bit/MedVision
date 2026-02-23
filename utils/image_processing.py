import cv2
import numpy as np

class ImageProcessor:
    def __init__(self):
        pass
    
    def adjust_brightness_contrast(self, image, brightness=0, contrast=100):
        """Ajustar brillo y contraste"""
        brightness = brightness / 100.0
        contrast = contrast / 100.0
        
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 1
            else:
                shadow = 0
                highlight = 1 + brightness
            alpha_b = (highlight - shadow) / (1 - shadow)
            gamma_b = shadow
            buf = cv2.addWeighted(image, alpha_b, image, 0, gamma_b)
        else:
            buf = image.copy()
        
        if contrast != 0:
            f = 131 * (contrast + 127) / (127 * (131 - contrast))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
        
        return buf
    
    def zoom_image(self, image, zoom_factor):
        """Zoom de la imagen"""
        height, width = image.shape[:2]
        new_height, new_width = int(height * zoom_factor), int(width * zoom_factor)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    
    def pan_image(self, image, x_offset, y_offset):
        """Desplazar imagen (pan)"""
        # Implementación básica de pan
        return image
    
    def calculate_hu_value(self, pixel_value, slope, intercept):
        """Calcular valor HU (Hounsfield Unit)"""
        return pixel_value * slope + intercept