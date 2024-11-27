import requests

# Base URL for OpenWeatherMap API
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"

# Function to read the API key from a file
def read_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.readline().strip()

# Function to get weather information
def get_weather(city, api_key):
    url = BASE_URL + "q=" + city + "&appid=" + api_key + "&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather = {
            "description": data['weather'][0]['description'].capitalize(),
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "wind_speed": data['wind']['speed']
        }
        return weather
    elif response.status_code == 404:
        return "City not found. Please check the city name."
    elif response.status_code == 401:
        return "Invalid API key. Please check your API key."
    else:
        return f"Error: {response.status_code}"

# Function to display weather information
def display_weather_info(city, weather_data):
    print(f"\nWeather in {city}: {weather_data['description']} | {weather_data['temperature']}°C")
    print(f"Humidity: {weather_data['humidity']}% | Wind Speed: {weather_data['wind_speed']} m/s")

# Function to recommend outfits based on weather
def recommend_outfit(weather):
    temp = weather["temperature"]
    condition = weather["description"].lower()
    wind_speed = weather["wind_speed"]

    outfit = []

    if temp > 25:
        outfit.append("Light clothing, such as t-shirts and shorts")
        outfit.append("Sunglasses and a hat")
        if "rain" in condition:
            outfit.append("Carry a light raincoat or umbrella")
    elif 15 < temp <= 25:
        outfit.append("Moderate clothing, such as jeans and a light jacket")
        if "cloud" in condition or wind_speed > 10:
            outfit.append("A windbreaker or light sweater")
    elif 5 < temp <= 15:
        outfit.append("Warm clothing, like sweaters or hoodies")
        if "rain" in condition:
            outfit.append("A waterproof jacket and boots")
    else:
        outfit.append("Heavy winter clothing, such as coats, gloves, and scarves")
        if "snow" in condition:
            outfit.append("Wear insulated and waterproof gear, including snow boots")

    # Specific recommendations for misty weather
    if "mist" in condition:
        outfit.append("Wear layers to stay warm in the damp air")
        outfit.append("Use a scarf to protect against the chill")
        outfit.append("Consider reflective or bright clothing for low visibility")

    if "haze" in condition:
        outfit.append("Wear light, long-sleeve clothing to protect your skin from dust particles.")
        outfit.append("Opt for breathable fabrics to stay comfortable in the humid air.")
        outfit.append("Consider wearing sunglasses to reduce glare and protect your eyes from haze.")
        outfit.append("A face mask or scarf can be helpful to protect your respiratory system from dust.")

    if wind_speed > 15:
        outfit.append("Add a wind-resistant jacket")

    return outfit

# Main block
if __name__ == "__main__":
    # Read the API key
    API_KEY = read_api_key('Security/APIKey.txt')

    # Get city input from user
    city = input("Enter the city name: ").strip()
    weather_data = get_weather(city, API_KEY)

    # Display weather information and outfit recommendations
    if isinstance(weather_data, dict):
        display_weather_info(city, weather_data)
        print("\nRecommended Outfit:")
        outfits = recommend_outfit(weather_data)
        for item in outfits:
            print(f"- {item}")
    else:
        print(weather_data)
