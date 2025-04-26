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

# Define the Azure functions that calls API for sentiment analysis 
def get_azure_sentiment(text: str) -> dict:
    header = {'X-API-KEY: 31808209eea7171b1f014836'}
    data = {'text' : text}
    url = "https://cent.ischool-iot.net/api/azure/sentiment"
    response = request.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()

# Define the azure function that calls API for key phrase extraction
def get_azure_key_phrase_extraction(text: str) -> dict:
    header = {'X-API-KEY: 31808209eea7171b1f014836'}
    data = {'text' : text}
    url = "https://cent.ischool-iot.net/api/azure/keyphrasextraction"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()  

# Define the azure function that calls API for named entity recognition
def get_azure_named_entity_recognition(text: str) -> dict:
    header = {'X-API-KEY: 31808209eea7171b1f014836'}
    data = {'text' : text}
    url = "https://cent.ischool-iot.net/api/azure/entityrecognition"
    response = requests.post(url, headers=header, data=data)
    response.raise_for_status()
    return response.json()

# Define geocode function that calls API for geocoding
def geocode(place:str) -> dict:
    '''
    Given a place name, return the latitude and longitude of the place.
    Written for example_etl.py
    '''
    header = { 'X-API-KEY: 31808209eea7171b1f014836' }
    params = { 'location': place }
    url = "https://cent.ischool-iot.net/api/google/geocode"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json() # Return the JSON response as a dictionary


def get_weather(lat: float, lon: float) -> dict:
    '''
    Given a latitude and longitude, return the current weather at that location.
    written for example_etl.py
    '''
    header = { 'X-API-KEY: 31808209eea7171b1f014836' }
    params = { 'lat': lat, 'lon': lon, 'units': 'imperial' }
    url = "https://cent.ischool-iot.net/api/weather/current"
    response = requests.get(url, headers=header, params=params)
    response.raise_for_status()
    return response.json()  # Return the JSON response as a dictionary