import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
from Emotion_Detection import emotion_detection  # Import the function
from Weather import *

# Read API key from the file
API_KEY = read_api_key('Security/APIKey.txt')  # Update the path if necessary
CITY = "Bangalore"  # City for which to get weather information

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# List available voices and set a male voice
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def talk(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def read_contacts(filename='contacts.txt'):
    """Read contacts from a file and return as a dictionary."""
    contacts = {}
    with open(filename, 'r') as file:
        for line in file:
            name, number = line.strip().split(',')
            contacts[name.strip().title()] = number.strip()
    return contacts

contacts = read_contacts()  # Load contacts

def listen_for_hotword():
    """Waits until it hears 'Jarvis'."""
    while True:
        try:
            with sr.Microphone(device_index=19) as source:
                listener.adjust_for_ambient_noise(source)
                print("Waiting for hotword 'Jarvis'...")
                voice = listener.listen(source, timeout=5)
                command = listener.recognize_google(voice).lower()
                if 'jarvis' in command:
                    talk("Yes?")
                    return
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            talk("Sorry, my speech service is down.")
        except Exception as e:
            print(f"Error: {e}")

def take_command():
    """Listens for and returns a command after hearing the hotword."""
    try:
        with sr.Microphone(device_index=19) as source:
            listener.adjust_for_ambient_noise(source)
            print("Listening for a command...")
            voice = listener.listen(source, timeout=5)
            command = listener.recognize_google(voice).lower()
            print(f"Command: {command}")
            return command
    except sr.UnknownValueError:
        talk("Sorry, I did not catch that. Could you repeat?")
        return ""
    except sr.RequestError:
        talk("Sorry, my speech service is down.")
        return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

def ask_for_contact():
    """Ask the user for a valid contact up to 5 times."""
    attempts = 5
    available_contacts = ', '.join(contacts.keys())

    for _ in range(attempts):
        talk(f"Available contacts are: {available_contacts}. Who would you like to message?")
        recipient_name = take_command().strip().title()

        if recipient_name in contacts:
            return recipient_name  # Valid contact found

    talk("Sorry, I couldn't find a valid contact. Please try again later.")
    return None  # Return None if no valid contact after 5 attempts

def run_jarvis():
    """Process commands after hotword activation."""
    command = take_command()

    if not command:
        return

    if 'play' in command:
        song = command.replace('play', '').strip()
        talk(f'Playing {song}')
        pywhatkit.playonyt(song)

    elif 'date' in command:
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        talk(f'Today\'s date is {current_date}')

    elif 'who is' in command:
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

    elif 'joke' in command:
        joke = pyjokes.get_joke()
        print(joke)
        talk(joke)

    elif 'search for' in command:
        search_term = command.replace('search for', '').strip()
        talk(f'Searching for {search_term}')
        pywhatkit.search(search_term)

    elif 'emotion detection' in command:  # Added command
        talk("Starting emotion detection.")
        emotion_detection(talk)  # Call the emotion detection function

    elif 'time' in command:
        current_time = datetime.datetime.now().strftime('%I:%M %p')
        talk(f'The current time is {current_time}')

    elif 'weather' in command:
        weather_info = get_weather(CITY, API_KEY)
        talk(f"The current weather in {CITY} is: {weather_info}")

    elif 'message' in command:  # WhatsApp messaging with confirmation and retries
        talk("To whom would you like to send a message?")
        recipient_name = take_command().strip().title()

        # Check if the contact is available, if not, ask up to 5 times.
        if recipient_name not in contacts:
            recipient_name = ask_for_contact()

        if recipient_name:
            recipient_number = contacts[recipient_name]

            while True:
                talk("What message would you like to send?")
                message = take_command()
                talk(f"You said: {message}. Is that correct?")
                confirmation = take_command().strip().lower()

                if 'yes' in confirmation:
                    pywhatkit.sendwhatmsg_instantly(f"+{recipient_number}", message)
                    talk(f"Message sent to {recipient_name}.")
                    break
                elif 'no' in confirmation:
                    talk("Okay, please say the message again.")
                else:
                    talk("Sorry, I didn't understand. Please confirm again.")

        else:
            talk("Exiting message sending. No valid contact found.")

    else:
        talk("I'm not sure about that. Please try again.")

# Main loop to wait for hotword and execute commands
if __name__ == "__main__":
    while True:
        listen_for_hotword()
        run_jarvis()
