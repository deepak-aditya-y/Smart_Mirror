import cv2
from fer import FER
import time
import pyttsx3
import threading

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Function to speak the detected emotion
def talk(text):
    def speak():
        # Ensure pyttsx3 is initialized only once
        engine.say(text)
        engine.runAndWait()

    # Run speak function in a separate thread to prevent blocking the main thread
    threading.Thread(target=speak, daemon=True).start()

def emotion_detection():
    # Initialize the emotion detector
    detector = FER()

    # Start capturing video from the webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not open webcam.")
        return

    end_time = time.time() + 60  # Run for 60 seconds
    last_emotion_time = 0  # Track when the last emotion was announced

    while time.time() < end_time:
        # Read a frame from the webcam
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Detect emotions in the current frame
        emotion_analysis = detector.detect_emotions(frame)

        for analysis in emotion_analysis:
            # Get bounding box and emotions
            x, y, w, h = analysis['box']
            emotions = analysis['emotions']

            # Get the dominant emotion
            dominant_emotion = max(emotions, key=emotions.get)

            # Print to check detected emotion
            print(f"Detected emotion: {dominant_emotion}")
            talk(dominant_emotion)  # Use the talk function to speak the emotion

            # Announce the detected emotion every 15 seconds
            current_time = time.time()
            if current_time - last_emotion_time >= 15:
                talk(dominant_emotion)  # Use the talk function to provide a response
                last_emotion_time = current_time

        # Display the resulting frame with bounding boxes
        for analysis in emotion_analysis:
            x, y, w, h = analysis['box']
            dominant_emotion = max(analysis['emotions'], key=analysis['emotions'].get)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Show the frame with detected emotions
        cv2.imshow('Webcam Emotion Detection', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    video_capture.release()
    cv2.destroyAllWindows()

# Call the emotion_detection function when needed, e.g., via a button press or command.
