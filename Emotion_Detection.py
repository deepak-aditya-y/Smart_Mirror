import cv2
from fer import FER
import time

def emotion_detection(talk):
    # Initialize the emotion detector
    detector = FER()

    # Start capturing video from the webcam
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Error: Could not open webcam.")
        return

    end_time = time.time() + 20  # Run for 1 minute
    last_emotion_time = 0  # Track when the last emotion was announced

    while time.time() < end_time:
        # Read a frame from the webcam
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Detect emotions in the current frame
        emotion_analysis = detector.detect_emotions(frame)

        # Draw bounding boxes and display detected emotions
        for analysis in emotion_analysis:
            # Get bounding box and emotions
            x, y, w, h = analysis['box']
            emotions = analysis['emotions']

            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Get the dominant emotion
            dominant_emotion = max(emotions, key=emotions.get)

            # Display the dominant emotion on the frame
            cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Announce the detected emotion every 20 seconds
            current_time = time.time()
            if current_time - last_emotion_time >= 5:  # Check if 20 seconds have passed
                talk(dominant_emotion)  # Use the talk function from your main assistant
                last_emotion_time = current_time  # Update the last announced time

        # Display the resulting frame
        cv2.imshow('Webcam Emotion Detection', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close windows
    video_capture.release()
    cv2.destroyAllWindows()
