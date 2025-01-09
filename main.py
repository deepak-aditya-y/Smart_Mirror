import speech_recognition as sr
import tkinter as tk
from tkinter import messagebox
import threading
import pyttsx3
import pywhatkit
import time
import wikipedia
from PIL import Image, ImageTk
import cv2
from Weather import *  # Ensure this is defined correctly
from Emotion_Detection import emotion_detection
from Emotion_Detection import get_emotion  # Import the updated emotion detection function
from Schedule import *  # Ensure this is defined correctly

API_KEY = read_api_key('Security/Weater_API_Key.txt')  # Update the path if necessary
CITY = "Bangalore"

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Initialize speech recognizer
listener = sr.Recognizer()

# Global variables for webcam and emotion detection
cap = None
webcam_canvas = None
emotion_mode = False
Flag = True
last_emotion_time = 0


# GUI Functions
def talk(text):
    """Convert text to speech and display it in the output box."""
    add_message(text)
    engine.say(text)
    engine.runAndWait()


def add_message(text):
    """Add a message to the GUI output box."""
    output_box.insert(tk.END, text + '\n')
    output_box.see(tk.END)


def update_webcam_feed():
    """Update the webcam feed on the GUI."""
    global cap, webcam_canvas, emotion_mode, last_emotion_time

    ret, frame = cap.read()
    if not ret:
        return

    # If in emotion detection mode, process the frame
    if emotion_mode:
        frame, _ = emotion_detection(frame, last_emotion_time)

    # Define the desired canvas dimensions
    canvas_width = 900
    canvas_height = 700

    # Get frame dimensions and calculate aspect ratio
    frame_height, frame_width, _ = frame.shape
    frame_aspect = frame_width / frame_height
    canvas_aspect = canvas_width / canvas_height

    # Resize the frame while maintaining aspect ratio
    if frame_aspect > canvas_aspect:
        new_width = canvas_width
        new_height = int(canvas_width / frame_aspect)
    else:
        new_height = canvas_height
        new_width = int(canvas_height * frame_aspect)

    resized_frame = cv2.resize(frame, (new_width, new_height))

    # Add padding to center the resized frame in the canvas
    padded_frame = cv2.copyMakeBorder(
        resized_frame,
        top=(canvas_height - new_height) // 2,
        bottom=(canvas_height - new_height) // 2,
        left=(canvas_width - new_width) // 2,
        right=(canvas_width - new_width) // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=[0, 0, 0]
    )

    # Convert frame to RGB and update the canvas
    frame = cv2.cvtColor(padded_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    webcam_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
    webcam_canvas.imgtk = imgtk

    # Schedule the next update
    webcam_canvas.after(10, update_webcam_feed)


def start_emotion_detection():
    """Enable emotion detection mode."""
    global emotion_mode
    emotion_mode = True
    talk("Emotion detection started.")

    threading.Timer(10, stop_emotion_detection).start()


def stop_emotion_detection():
    """Disable emotion detection mode."""
    global emotion_mode
    emotion_mode = False
    talk("Emotion detection stopped.")


def listen_for_hotword():
    """Waits until it hears 'Jarvis'."""
    global last_activity_time
    last_activity_time = time.time()
    add_message("Waiting for hotword 'alexa'...")
    while True:
        try:
            with sr.Microphone(device_index=0) as source:
                listener.adjust_for_ambient_noise(source)
                add_message("Listening.........")
                voice = listener.listen(source, timeout=5)
                command = listener.recognize_google(voice).lower()
                if 'alexa' in command:
                    talk("Yes?")
                    return
                if (time.time() - last_activity_time) > 40:
                    talk("No activity detected. Shutting down.")
                    exit()
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            talk("Sorry, my speech service is down.")
        except Exception as e:
            add_message(f"Error: {e}")


def take_command():
    """Listens for and returns a command after hearing the hotword."""
    try:
        with sr.Microphone(device_index=0) as source:
            listener.adjust_for_ambient_noise(source)
            add_message("Listening.....")
            voice = listener.listen(source, timeout=5)
            command = listener.recognize_google(voice).lower()
            add_message(f"Command: {command}")
            return command
    except sr.UnknownValueError:
        talk("Sorry, I did not catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        talk("Sorry, my speech service is down.")
        return ""
    except Exception as e:
        add_message(f"Error: {e}")
        return ""


def start_assistant():
    """Continuously listens for hotword and runs the assistant."""
    while Flag:
        listen_for_hotword()
        run_jarvis()


def start_assistant_thread():
    Flag = True
    """Starts the assistant in a separate thread."""
    threading.Thread(target=start_assistant, daemon=True).start()


def run_jarvis():
    """Process commands after hotword activation."""
    global last_activity_time
    command = take_command()
    last_activity_time = time.time()

    if not command:
        return

    if 'play' in command:  # To Play Music
        song = command.replace('play', '').strip()
        talk(f'Playing {song}')
        pywhatkit.playonyt(song)

    elif 'date' in command:  # For Date
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        talk(f'Today\'s date is {current_date}')

    elif 'time' in command:  # For Time
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f'The current time is {current_time}')

    elif 'weather' in command:  # For Weather
        weather_data = get_weather(CITY, API_KEY)
        if isinstance(weather_data, dict):
            weather_desc = weather_data["description"]
            temp = weather_data["temperature"]
            humidity = weather_data["humidity"]
            wind_speed = weather_data["wind_speed"]
            talk(
                f"The current weather in {CITY} is: {weather_desc}. "
                f"The temperature is {temp} degrees Celsius. "
                f"The humidity is {humidity} percent, which means it's {'humid' if humidity > 60 else 'dry'}. "
                f"The wind speed is {wind_speed} meters per second, which indicates {'breezy conditions' if wind_speed > 10 else 'calm air'}."
            )
        else:
            talk(weather_data)

    elif 'stop emotion detection' in command:  # Stop Emotion Detection
        stop_emotion_detection()

    elif 'start emotion detection' in command:  # Run Emotion Detection
        start_emotion_detection()


    elif 'who is' in command:  # Search in Wikipedia
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, sentences=1)
            talk(info)
        except wikipedia.exceptions.PageError:
            talk("I couldn't find information on that person. Please try again.")
        except wikipedia.exceptions.DisambiguationError as e:
            talk(f"That name is too ambiguous. Please be more specific. Some options are: {', '.join(e.options[:3])}")
        except Exception as e:
            talk(f"An error occurred: {e}")

    elif 'outfit' in command:  # Recommend Outfit
        weather_data = get_weather(CITY, API_KEY)
        if isinstance(weather_data, dict):
            outfits = recommend_outfit(weather_data)
            talk(f"Based on the weather in {CITY}, I recommend the following outfit:")
            talk(outfits)
        else:
            talk("I'm unable to retrieve the weather data right now, so I can't recommend an outfit.")

    elif 'search for' in command:  # Search on Google
        search_term = command.replace('search for', '').strip()
        talk(f'Searching for {search_term}')
        pywhatkit.search(search_term)

    elif 'schedule' in command:  # Get Today's Schedule
        schedule_data = get_schedule_for_today()
        if isinstance(schedule_data, list):
            # talk("Here’s your schedule for today:")
            for event in schedule_data:
                talk(event)
        else:
            talk("I'm unable to retrieve your schedule right now, please try again later.")

    elif 'shutdown' in command or 'exit' in command:  # Shutdown Assistant
        talk("Shutting down. Goodbye!")
        exit()


# Login GUI
def login():
    username = username_entry.get()
    password = password_entry.get()
    if username == "admin" and password == "password":
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("Login Failed", "Incorrect Username or Password")


def open_main_window():
    global main_window, output_box, webcam_canvas, cap

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        tk.messagebox.showerror("Error", "Unable to access the webcam.")
        return

    # Function to update date, time, weather, and outfit recommendations
    def update_datetime_weather():
        current_date = time.strftime('%Y-%m-%d')
        current_time = time.strftime('%I:%M:%S %p')

        # Fetch weather data
        weather_text = "Fetching weather..."
        outfit_text = "Fetching outfit recommendations..."
        weather_data = get_weather(CITY, API_KEY)
        emotion_data, comment_text = get_emotion()
        if isinstance(weather_data, dict):
            weather_desc = weather_data["description"]
            temp = weather_data["temperature"]
            weather_text = f"{weather_desc}, {temp}\u00b0C"
            # Generate outfit recommendations
            outfits = recommend_outfit(weather_data)
            outfit_text = f"Recommended Outfit:\n {outfits}"
        else:
            weather_text = "Weather unavailable"
            outfit_text = "Unable to fetch outfit recommendations"

        # Update labels
        date_label.config(text=f"Date: {current_date}")
        time_label.config(text=f"Time: {current_time}")
        weather_label.config(text=f"Weather: {weather_text}")
        outfit_label.config(text=f"{outfit_text}")
        emotion_label.config(text=f"{emotion_data}\n{comment_text}")

        # Schedule next update
        main_window.after(1000, update_datetime_weather)

    # Main Window
    main_window = tk.Tk()
    main_window.title("Voice Assistant")
    main_window.geometry("1000x700")

    # Webcam canvas for live feed (Left side, taking 3/4th of the window)
    webcam_canvas = tk.Canvas(main_window, width=900, height=700, bg="black")
    webcam_canvas.place(x=0, y=0)

    # Date, Time, Weather, and Outfit Recommendation Labels (Top right corner)
    info_frame = tk.Frame(main_window)
    info_frame.place(x=950, y=10, width=1000)

    date_label = tk.Label(info_frame, text="", font=("Helvetica", 12), anchor="w", justify="left")
    date_label.pack(anchor="w")
    time_label = tk.Label(info_frame, text="", font=("Helvetica", 12), anchor="w", justify="left")
    time_label.pack(anchor="w")
    weather_label = tk.Label(info_frame, text="", font=("Helvetica", 12), anchor="w", justify="left")
    weather_label.pack(anchor="w")
    emotion_label = tk.Label(info_frame, text="", font=("Helvetica", 12), anchor="w", justify="left")
    emotion_label.pack(anchor="w")

    # Create a customized frame for the outfit recommendations
    outfit_frame = tk.Frame(main_window, bg="lightblue", bd=2, relief="ridge", width=230, height=175)
    outfit_frame.place(x=950, y=150)

    # Prevent resizing by child widgets
    outfit_frame.pack_propagate(False)

    # Add a styled label inside the frame
    outfit_label = tk.Label(
        outfit_frame,
        text="",
        font=("Verdana", 12, "bold"),
        bg="lightblue",
        fg="darkblue",
        wraplength=210,
        anchor="center",
        justify="center"
    )
    outfit_label.pack(padx=10, pady=10)

    # Output Box (Bottom right corner)
    output_box = tk.Text(main_window, wrap=tk.WORD, height=15, width=30, font=("Helvetica", 12))
    output_box.place(x=950, y=350)

    # Start Assistant Button (Below the output box)
    start_button = tk.Button(main_window, text="Start Assistant", command=start_assistant_thread,
                             font=("Helvetica", 14))
    start_button.place(x=1000, y=650)

    # Start updating the webcam feed
    update_webcam_feed()

    # Start updating date, time, weather, and outfit recommendations
    update_datetime_weather()

    main_window.mainloop()

    # Release the webcam when the window is closed
    cap.release()
    cv2.destroyAllWindows()


# Login GUI
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

tk.Label(login_window, text="Username", font=("Helvetica", 12)).pack(pady=5)
username_entry = tk.Entry(login_window)
username_entry.pack(pady=5)

tk.Label(login_window, text="Password", font=("Helvetica", 12)).pack(pady=5)
password_entry = tk.Entry(login_window, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", command=login, font=("Helvetica", 12))
login_button.pack(pady=20)

login_window.mainloop()