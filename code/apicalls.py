# Import the requests library to make HTTP requests
import requests

# This is the authentication key required to access the CENT Ischool IoT APIs
APIKEY = "d4937e5ce33a6b2c739c4fe2"

def get_google_place_details(google_place_id: str) -> dict:
    """
    Retrieves details about a Google Place using its place ID.
    
    Args:
        google_place_id (str): The unique identifier for a Google Place
        
    Returns:
        dict: A dictionary containing the place details from Google Places API
        
    Raises:
        HTTPError: If the API request fails (status code >= 400)
    """
    header = { 'X-API-KEY': APIKEY }  # Authentication header
    params = { 'place_id': google_place_id }  # Query parameters
    url = "https://cent.ischool-iot.net/api/google/places/details"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()  # Raise exception for bad status codes
    return response.json()  # Return the JSON response as a dictionary


def get_azure_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of the given text using Azure's Text Analytics.
    
    Args:
        text (str): The text to analyze for sentiment
        
    Returns:
        dict: A dictionary containing sentiment analysis results
              (likely including sentiment score and classification)
              
    Raises:
        HTTPError: If the API request fails
    """
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }  # Request body with the text to analyze
    url = "https://cent.ischool-iot.net/api/azure/sentiment"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()


def get_azure_key_phrase_extraction(text: str) -> dict:
    """
    Extracts key phrases from the given text using Azure's Text Analytics.
    
    Args:
        text (str): The text to analyze for key phrases
        
    Returns:
        dict: A dictionary containing the extracted key phrases
        
    Raises:
        HTTPError: If the API request fails
    """
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }
    url = "https://cent.ischool-iot.net/api/azure/keyphrasextraction"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()


def get_azure_named_entity_recognition(text: str) -> dict:
    """
    Identifies named entities in the text using Azure's Text Analytics.
    
    Args:
        text (str): The text to analyze for named entities
        
    Returns:
        dict: A dictionary containing recognized entities (people, places, etc.)
        
    Raises:
        HTTPError: If the API request fails
    """
    header = { 'X-API-KEY': APIKEY }
    data = { "text" : text }
    url = "https://cent.ischool-iot.net/api/azure/entityrecognition"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()


def geocode(place: str) -> dict:
    """
    Converts a place name or address into geographic coordinates (geocoding).
    
    Args:
        place (str): The location/address to geocode
        
    Returns:
        dict: A dictionary containing geographic coordinates and address details
        
    Raises:
        HTTPError: If the API request fails
    """
    header = { 'X-API-KEY': APIKEY }
    params = { 'location': place }  # Location to geocode
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()


def get_weather(lat: float, lon: float) -> dict:
    """
    Retrieves current weather data for the given coordinates.
    
    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate
        
    Returns:
        dict: A dictionary containing current weather data
              (temperature, conditions, etc. in imperial units)
              
    Raises:
        HTTPError: If the API request fails
    """
    header = { 'X-API-KEY': APIKEY }
    params = { 
        'lat': lat, 
        'lon': lon, 
        'units': 'imperial'  # Request weather data in imperial units
    }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()