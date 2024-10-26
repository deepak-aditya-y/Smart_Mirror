import cv2
import numpy as np
import pyttsx3
import time

# Initialize the video capture
video = cv2.VideoCapture(0)

# Load the Haar cascade for face detection
facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Initialize the face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("Trainer.yml")  # Load the trained model

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Define a list of names corresponding to IDs
name_list = ["", "Saurav", "Deepak", "Allan",]  # Updated names

# Dictionary to store last greeting time for users
last_greeting_time = {}
greeting_duration = 20  # Time limit in seconds (10 minutes)

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale
    faces = facedetect.detectMultiScale(gray, 1.3, 5)  # Detect faces

    for (x, y, w, h) in faces:
        serial, conf = recognizer.predict(gray[y:y+h, x:x+w])  # Recognize face
        current_time = time.time()  # Get the current time

        print(serial)
        if 31 < conf < 48:  # Confidence threshold
            user_name = name_list[serial]

            # Check if the user has been greeted in the last 10 minutes
            if user_name not in last_greeting_time or (current_time - last_greeting_time[user_name] > greeting_duration):
                # Welcome the user
                engine.say(f"Welcome {user_name}!")
                engine.runAndWait()

                # Update the last greeting time for the user
                last_greeting_time[user_name] = current_time

            # Recognized face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            cv2.putText(frame, user_name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        else:
            # Unknown face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.imshow("Frame", frame)  # Show the frame


    k = cv2.waitKey(1)  # Wait for key press
    if k == ord("q"):  # Quit the application
        break

video.release()
cv2.destroyAllWindows()
