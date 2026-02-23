import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Float, LargeBinary, Text
from sqlalchemy.ext.declarative import declarative_base
import pydicom  # Importación añadida
import numpy as np  # Importación añadida
import cv2  # Importación añadida

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    clinical_data = Column(Text)

class ImageRecord(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer)
    modality = Column(String)
    image_data = Column(LargeBinary)
    thumbnail = Column(LargeBinary)
    image_metadata = Column(Text)

class DatabaseManager:
    def __init__(self, db_name="medvision.db"):
        self.engine = create_engine(f'sqlite:///{db_name}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
    def save_image(self, image_data, patient_name, modality, file_type="dcm"):
        session = self.Session()
        
        # Convertir imagen a thumbnail
        if isinstance(image_data, pydicom.dataset.FileDataset):
            # Es DICOM
            image_array = image_data.pixel_array
            thumbnail = self._create_thumbnail(image_array)
            metadata = str(image_data.__dict__)
        else:
            # Es JPEG/PNG
            image_array = image_data
            thumbnail = self._create_thumbnail(image_array)
            metadata = f"Formato: {file_type}, Dimensiones: {image_array.shape}"
        
        # Guardar imagen
        image_record = ImageRecord(
            patient_id=self._get_patient_id(patient_name),
            modality=modality,
            image_data=self._array_to_blob(image_array),
            thumbnail=self._array_to_blob(thumbnail),
            image_metadata=metadata
        )
        session.add(image_record)
        session.commit()
        session.close()
    
    def get_images(self, patient_name, modality):
        session = self.Session()
        patient_id = self._get_patient_id(patient_name)
        images = session.query(ImageRecord).filter_by(patient_id=patient_id, modality=modality).all()
        session.close()
        return [{"image": self._blob_to_array(img.image_data), 
                 "thumbnail": self._blob_to_array(img.thumbnail)} 
                for img in images]
    
    def get_patients(self):
        session = self.Session()
        patients = session.query(Patient).all()
        session.close()
        return pd.DataFrame([(p.name, p.age, p.gender) for p in patients], 
                          columns=['name', 'age', 'gender'])
    
    def get_patient_data(self, patient_name):
        session = self.Session()
        patient = session.query(Patient).filter_by(name=patient_name).first()
        session.close()
        return {
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "clinical_data": patient.clinical_data
        }
    
    def _get_patient_id(self, name):
        session = self.Session()
        patient = session.query(Patient).filter_by(name=name).first()
        if not patient:
            patient = Patient(name=name, age=0, gender="Unknown", clinical_data="{}")
            session.add(patient)
            session.commit()
        session.close()
        return patient.id
    
    def _create_thumbnail(self, image_array):
        # Crear thumbnail reducido
        thumbnail = cv2.resize(image_array, (100, 100))
        return thumbnail
    
    def _array_to_blob(self, array):
        is_success, buffer = cv2.imencode(".png", array)
        if is_success:
            return buffer.tobytes()
        return None
    
    def _blob_to_array(self, blob):
        nparr = np.frombuffer(blob, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)