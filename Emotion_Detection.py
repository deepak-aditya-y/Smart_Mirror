import cv2
import time
from fer import FER
import threading
import pyttsx3

# Original code from Emotion_Detection.py
# Initialize pyttsx3 engine
engine = pyttsx3.init()

current_emotion_text = ""
comment = ""
dominant_emotion = ""

# Emotion comments dictionary
emotion_comments = {
    "": "nothing",
    "happy": "Keep smiling! It brightens up your day.",
    "sad": "It's okay to feel down sometimes. Things will get better.",
    "angry": "Take a deep breath. Calmness is key.",
    "surprise": "Wow! Something caught you off guard?",
    "disgust": "Not a fan of that, huh?",
    "fear": "Everything's fine. Stay strong!",
    "neutral": 'Looking composed and steady.'
}


# Function to speak the detected emotion
def talk(text):
    def speak():
        engine.say(text)
        engine.runAndWait()

    threading.Thread(target=speak, daemon=True).start()


# Emotion detection function
# Emotion detection function
def emotion_detection(frame, last_emotion_time):
    global current_emotion_text
    global dominant_emotion  # Global variable to hold the detected emotion text

    detector = FER()
    emotion_analysis = detector.detect_emotions(frame)

    for analysis in emotion_analysis:
        # Extract bounding box and emotions
        x, y, w, h = analysis['box']
        emotions = analysis['emotions']
        dominant_emotion = max(emotions, key=emotions.get)

        # Draw bounding box and emotion label
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Update the detected emotion text for GUI display
        current_emotion_text = f"Detected Emotion: {dominant_emotion.capitalize()}"

        # Announce the emotion every 15 seconds
        current_time = time.time()
        if current_time - last_emotion_time >= 5:
            comment = emotion_comments.get(dominant_emotion, "Emotion detected!")
            talk(comment)
            print(comment)
            last_emotion_time = current_time

    return frame, last_emotion_time


def get_emotion():
    comment = emotion_comments.get(dominant_emotion, "Emotion detected!")
    return current_emotion_text, comment


# Main execution logic to run for 20 seconds
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

last_emotion_time = 0
start_time = time.time()

print("Starting emotion detection for 10 seconds...")

while time.time() - start_time < 10:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    frame, last_emotion_time = emotion_detection(frame, last_emotion_time)

    # Display the frame with detected emotions
    cv2.imshow("Emotion Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Emotion detection completed.")