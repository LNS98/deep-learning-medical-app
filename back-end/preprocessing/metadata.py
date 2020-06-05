import os
import pandas as pd
import numpy as np
from enum import Enum
import SimpleITK as sitk

class SeriesTypes(Enum):
    AXIAL = 'Axial T2'
    CORONAL = 'Coronal T2'
    AXIAL_POSTCON = 'Axial Postcon'

class Patient:
    def __init__(self, group, index):
        self.group = group
        self.index = index

    def get_id(self):
        return self.group + str(self.index)

    def set_paths(self, axial, coronal='', axial_postcon=''):
        self.axial = axial
        self.coronal = coronal
        self.axial_postcon = axial_postcon

    def set_severity(self, severity):
        self.severity = severity

    def set_images(self, axial_image=None):
        self.axial_image = axial_image

    def set_ileum_coordinates(self, coords):
        self.ileum = coords

    def load_image_data(self):
        axial_path = self.axial
        if os.path.isfile(axial_path):
            self.set_images(sitk.ReadImage(axial_path))

    def __str__(self):
        return f'{self.get_id()}: {self.axial}, {self.coronal}, {self.axial_postcon}'

class Metadata:
    def form_path(self, patient, series_type):
        folder = patient.group
        if self.dataset_tag:
            folder += self.dataset_tag
        path = os.path.join(self.data_path, folder, f'{patient.get_id()} {series_type}{self.dataset_tag}')
        for ext in self.data_extensions:
            full_path = f'{path}.{ext}'
            if os.path.isfile(full_path):
                return full_path
        return -1

    def file_list(self, patients):
        for patient in patients:
            axial = self.form_path(patient, SeriesTypes.AXIAL.value)
            coronal = self.form_path(patient, SeriesTypes.CORONAL.value)
            axial_postcon = self.form_path(patient, SeriesTypes.AXIAL_POSTCON.value)
            patient.set_paths(axial, coronal, axial_postcon)
        return patients

    def label_set(self, patients, labels):
        for patient in patients:
            patient_labels = labels.loc[labels['Case ID'] == patient.get_id()]
            patient.set_severity(np.array(patient_labels['Terminal ileal Inflammation level'])[0])
            patient.set_ileum_coordinates(np.array(patient_labels[['coronal', 'sagittal', 'axial']])[0])
        return patients

    def __init__(self, data_path, label_path, abnormal_cases, healthy_cases, dataset_tag=''):
        print('Forming metadata')
        self.data_path = data_path
        self.data_extensions = ['nii', 'nii.gz']
        self.dataset_tag = dataset_tag

        abnormal_patients = [Patient('A', i + 1) for i in abnormal_cases]
        healthy_patients = [Patient('I', i + 1) for i in healthy_cases]

        self.patients = self.file_list(abnormal_patients + healthy_patients)

        ileum_labels = pd.read_csv(os.path.join(label_path, 'terminal_ileum'), delimiter='\t', header=0)
        self.patients = self.label_set(self.patients, ileum_labels)
