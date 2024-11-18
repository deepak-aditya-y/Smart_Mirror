import tkinter as tk
from tkinter import messagebox
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import time
import wikipedia
from Weather import *
from Emotion_Detection import emotion_detection
from Schedule import *

API_KEY = read_api_key('Security/Weater_API_Key.txt')  # Update the path if necessary
CITY = "Bangalore"

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Male voice
last_activity_time = time.time()

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

def listen_for_hotword():
    """Waits until it hears 'Jarvis'."""
    global last_activity_time
    last_activity_time = time.time()
    add_message("Waiting for hotword 'Jarvis'...")
    while True:
        try:
            with sr.Microphone(device_index=0) as source:
                listener.adjust_for_ambient_noise(source)
                add_message("Listening.........")
                voice = listener.listen(source, timeout=5)
                command = listener.recognize_google(voice).lower()
                if 'jarvis' in command:
                    talk("Yes?")
                    return
                if (time.time() - last_activity_time) > 40:
                    talk("No activity detected. Shutting down.")
                    main_window.quit()
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
            talk(weather_data)  # Handle error messages from get_weather

    elif 'emotion detection' in command:  # Run Emotion Detection
        talk("Starting emotion detection.")
        emotion_detection(talk)  # Call the emotion detection function

    elif 'who is' in command:  # Search in Wikipedia
        person = command.replace('who is', '').strip()
        try:
            info = wikipedia.summary(person, sentences=1)
            print(info)
            talk(info)
        except wikipedia.exceptions.PageError:
            talk("I couldn't find information on that person. Please try again.")
        except wikipedia.exceptions.DisambiguationError as e:
            talk(f"That name is too ambiguous. Please be more specific. Some options are: {', '.join(e.options[:3])}")
        except Exception as e:
            talk(f"An error occurred: {e}")

    elif 'search for' in command:  # Search on Google
        search_term = command.replace('search for', '').strip()
        talk(f'Searching for {search_term}')
        pywhatkit.search(search_term)

    elif 'outfit' in command:  # Recommend Outfit
        weather_data = get_weather(CITY, API_KEY)
        if isinstance(weather_data, dict):
            outfits = recommend_outfit(weather_data)
            talk(f"Based on the weather in {CITY}, I recommend the following outfit:")
            for outfit in outfits:
                talk(outfit)
        else:
            talk("I'm unable to retrieve the weather data right now, so I can't recommend an outfit.")

    elif 'schedule' in command:  # Get Today's Schedule
        schedule_data = get_schedule_for_today()
        if isinstance(schedule_data, list):
            talk("Here’s your schedule for today:")
            for event in schedule_data:
                talk(event)
        else:
            talk("I'm unable to retrieve your schedule right now, please try again later.")

    elif 'shutdown' in command or 'exit' in command:  # Shutdown Assistant
        talk("Shutting down. Goodbye!")
        exit()

def start_assistant_thread():
    """Starts the assistant in a separate thread."""
    threading.Thread(target=start_assistant, daemon=True).start()

def start_assistant():
    """Continuously listens for hotword and runs the assistant."""
    while True:
        listen_for_hotword()
        run_jarvis()

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
    global main_window, output_box

    # Main Window
    main_window = tk.Tk()
    main_window.title("Voice Assistant")
    main_window.geometry("800x600")

    output_box = tk.Text(main_window, wrap=tk.WORD, height=25, width=70, font=("Helvetica", 12))
    output_box.pack(pady=20)

    start_button = tk.Button(main_window, text="Start Assistant", command=start_assistant_thread, font=("Helvetica", 14))
    start_button.pack(pady=10)

    main_window.mainloop()

# Login Window
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
