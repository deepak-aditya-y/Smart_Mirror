# weather.py
import requests

# Base URL for OpenWeatherMap API
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# Function to read the API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()  # Read the first line and strip any whitespace

# Function to get weather information
def get_weather(city, api_key):
    # Construct the full API URL
    url = BASE_URL + "q=" + city + "&appid=" + api_key + "&units=metric"
    response = requests.get(url)

    # Print the request URL and response status
    print(f"Request URL: {url}")
    print(f"Response Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description'].capitalize()  # Capitalize the first letter
        temperature = data['main']['temp']
        return f"{weather}  |  {temperature}°C"  # Added space and formatting
    else:
        print(f"Error: {response.json()}")  # Print error message
        return "Weather data not available"
