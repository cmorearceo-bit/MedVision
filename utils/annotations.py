import cv2
import numpy as np

class AnnotationTool:
    def __init__(self):
        self.drawing = False
        self.mode = None
        self.start_point = None
        self.end_point = None
        self.annotations = []
    
    def start_drawing(self, mode):
        """Iniciar herramienta de dibujo"""
        self.mode = mode
        self.drawing = True
        self.annotations = []
    
    def draw_annotation(self, image, start_point, end_point):
        """Dibujar anotación en la imagen"""
        if self.mode == "regla":
            # Dibujar línea con distancia
            cv2.line(image, start_point, end_point, (0, 255, 0), 2)
            distance = np.sqrt((end_point[0] - start_point[0])**2 + 
                            (end_point[1] - start_point[1])**2)
            cv2.putText(image, f"{distance:.1f}mm", 
                       (end_point[0], end_point[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif self.mode == "roi":
            # Dibujar ROI y calcular área
            cv2.rectangle(image, start_point, end_point, (0, 255, 0), 2)
            width = abs(end_point[0] - start_point[0])
            height = abs(end_point[1] - start_point[1])
            area = width * height
            cv2.putText(image, f"Área: {area} px²", 
                       (start_point[0], start_point[1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        elif self.mode == "flecha":
            # Dibujar flecha
            cv2.arrowedLine(image, start_point, end_point, (0, 0, 255), 2)
        
        return image
    
    def get_annotations(self):
        """Obtener lista de anotaciones"""
        return self.annotations