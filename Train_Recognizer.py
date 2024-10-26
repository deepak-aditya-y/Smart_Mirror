import cv2
import numpy as np
from PIL import Image
import os

# Initialize the recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Path to the dataset
path = "Datasets"

def getImageID(path):
    imagePath = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    ids = []
    for imagePaths in imagePath:
        faceImage = Image.open(imagePaths).convert('L')  # Convert to grayscale
        faceNP = np.array(faceImage)  # Convert to numpy array
        Id = int(os.path.split(imagePaths)[-1].split(".")[1])  # Extract ID
        faces.append(faceNP)
        ids.append(Id)
        cv2.imshow("Training", faceNP)  # Show the image being trained on
        cv2.waitKey(1)
    return ids, faces

# Get the IDs and face data
IDs, facedata = getImageID(path)

# Train the recognizer
recognizer.train(facedata, np.array(IDs))
recognizer.write("Security/Trainer.yml")  # Save the trained model
cv2.destroyAllWindows()
print("Training Completed............")
