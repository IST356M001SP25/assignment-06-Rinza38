curl -X 'GET' \
  'https://cent.ischool-iot.net/api/google/geocode?location=Syracuse%2C%20NY' \
  -H 'accept: application/json' \
  -H 'X-API-KEY: 31808209eea7171b1f014836'


import requests

# Put your CENT Ischool IoT Portal API KEY here.
APIKEY = "API31808209eea7171b1f014836"

# Define the get_google functions that will call the APIs
def get_google_place_details(ChIJDZqXv5vz2YkRRZWt1-IM1QA: str) -> dict:
    header = {'X-API-KEY: 31808209eea7171b1f014836'}
    par = {'place_id: ChIJDZqXv5vz2YkRRZWt1-IM1QA'}
    url = "https://cent.ischool-iot.net/api/google/places/details"
    response = requests.get(url, headers=header, par=par)
    response.raise_for_status() 
    return response.json() 

# Define the Azure functions that will call the APIs   
def get_azure_sentiment(text: str) -> dict:
    header = {'X-API-KEY: 31808209eea7171b1f014836'}
    data = {'text' : text}
    url = "https://cent.ischool-iot.net/api/azure/sentiment"
    response = request.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()

def get_azure_key_phrase_extraction(text: str) -> dict:
    pass # Implement this function

def get_azure_named_entity_recognition(text: str) -> dict:
    pass # Implement this function


def geocode(place:str) -> dict:
    '''
    Given a place name, return the latitude and longitude of the place.
    Written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'location': place }
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary


def get_weather(lat: float, lon: float) -> dict:
    '''
    Given a latitude and longitude, return the current weather at that location.
    written for example_etl.py
    '''
    header = { 'X-API-KEY': APIKEY }
    params = { 'lat': lat, 'lon': lon, 'units': 'imperial' }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary