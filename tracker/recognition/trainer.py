#!/usr/local/bin/python3

import os

import cv2
import numpy as np

from tracker.recognition import face_cascade


class Trainer:
    """
    The trainer class is the responsible of reading datasets, training them, and exporting the trained model
    """
    def __init__(self, photos, export):
        """
        Initialization of attributes
        :param photos: The directory containing photos to be trained on
        :param export: The path where the trained model will be saved
        """
        self.photos = photos
        self.export = export

    def get_nbr_photos(self):
        return len(os.listdir(self.photos))

    def get_radius(self, x, y, w, h):
        return w * h

    def get_max_area(self):
        image_paths = [os.path.join(self.photos, f) for f in os.listdir(self.photos)]
        width = height = _x = _y = _w = _h = 0
        for image_path in image_paths:
            gray = cv2.imread(image_path, cv2.COLOR_BGR2GRAY)
            # gray = cv2.cvtColor(image_pil, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            try:
                x, y, w, h = faces[0]
                if self.get_radius(x, y, w, h) >= self.get_radius(_x, _y, _w, _h):
                    width, height = w, h
            except: continue
        return width, height

    def get_images_and_labels(self, same_size=False):
        image_paths = [os.path.join(self.photos, f) for f in os.listdir(self.photos)]
        images, labels = [], []
        if same_size:
            width, height = self.get_max_area()
        for image_path in image_paths:
            image_pil = cv2.imread(image_path)
            try: nbr = int(os.path.split(image_path)[1].split("_")[0])
            except: continue
            gray = cv2.cvtColor(image_pil, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            image = np.array(gray, 'uint8')
            for x, y, w, h in faces:
                if same_size:
                    images.append(cv2.resize(image[y:y + h, x:x + w], (width, height)))
                else: images.append(image[y:y+h, x:x+w])
                labels.append(nbr)
        return images, labels

    def train(self):
        """
        Trains a model from dataset, saves the file to export path
        This process may take several minutes, make sure you have an SSD!
        :return: 
        """
        # create the face recognizer object
        lbph_rec = cv2.face.createLBPHFaceRecognizer()
        eigenface_rec = cv2.face.createEigenFaceRecognizer()
        fisherface_rec = cv2.face.createFisherFaceRecognizer()

        # Train LBPH recognizer
        images, labels = self.get_images_and_labels()
        lbph_rec.train(images, np.array(labels))
        lbph_rec.save(self.export + '_lbph.yml')

        # Train other two recognizers
        images, labels = self.get_images_and_labels(same_size=True)
        for recognizer, name in zip((eigenface_rec, fisherface_rec), ('eigenface', 'fisherface')):
            recognizer.train(images, np.array(labels))
            recognizer.save(self.export+'_'+name+'.yml')
