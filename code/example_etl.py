# Import required libraries
import streamlit as st  # For creating web apps (though not heavily used here)
import pandas as pd  # For data manipulation and analysis
import json  # For working with JSON data (though not directly used)
from apicalls import get_weather, geocode  # Custom API functions for weather and geocoding

'''
This is a sample Multi-step data pipeline. 
Given a list of places it will provide the current weather conditions for each place.

Data Processing Steps:
    1. locations -> geocode -> location, lat, lon
    2. location, lat, lon -> weather -> location, lat, lon, temp, precip

Pipeline Design Principle:
    Each step should accept either a file path (str) or DataFrame as input,
    and return both a cached file AND DataFrame as output
'''

# Define cache file paths for pipeline outputs
LOCATION_SOURCE_FILE = "cache/locations.csv"  # Source file containing location names
GEOCODE_CACHE_FILE = "cache/geocoded_locations.csv"  # Output from geocoding step
WEATHER_CACHE_FILE = "cache/weather_locations.csv"  # Final output with weather data

def geocode_step(locations: str|pd.DataFrame) -> pd.DataFrame:
    '''
    Step 1: Convert location names to geographic coordinates (geocoding)
    
    Input: Either a file path (str) to CSV or DataFrame containing:
        - location: Name/address of places to geocode
        
    Output: DataFrame and cached CSV with columns:
        - location: Original location name
        - lat: Latitude coordinate
        - lon: Longitude coordinate
        
    Process:
        1. Load input data
        2. Call geocode API for each location
        3. Extract coordinates from API response
        4. Return and cache results
    '''

    # Handle input - accept either file path or DataFrame
    if isinstance(locations, str):
        locations_df = pd.read_csv(locations)
    else:
        locations_df = locations

    # Geocode each location
    geocoded = []
    for index, row in locations_df.iterrows():
        geo = geocode(row['location'])  # Call geocoding API
        
        # Extract coordinates from API response
        lat = geo['results'][0]['geometry']['location']['lat']
        lon = geo['results'][0]['geometry']['location']['lng']
        
        # Create output record
        geo_item = {
            'location': row['location'],  # Preserve original name
            'lat': lat,
            'lon': lon
        }
        geocoded.append(geo_item)
    
    # Convert results to DataFrame
    geocoded_locations_df = pd.DataFrame(geocoded)

    # Cache results to CSV and return DataFrame
    geocoded_locations_df.to_csv(GEOCODE_CACHE_FILE, index=False, header=True)
    return geocoded_locations_df

def weather_step(geocoded_locations: str|pd.DataFrame) -> pd.DataFrame:
    '''
    Step 2: Get current weather data for geocoded locations
    
    Input: Either a file path (str) or DataFrame containing:
        - location: Place name
        - lat: Latitude
        - lon: Longitude
        
    Output: DataFrame and cached CSV with columns:
        - location: Place name
        - lat, lon: Coordinates
        - temp: Current temperature
        - precip: Current precipitation
        
    Process:
        1. Load input data
        2. Call weather API for each coordinate pair
        3. Extract weather metrics from API response
        4. Return and cache results
    '''

    # Handle input - accept either file path or DataFrame
    if isinstance(geocoded_locations, str):
        geocoded_locations_df = pd.read_csv(geocoded_locations)
    else:
        geocoded_locations_df = geocoded_locations

    # Get weather for each location
    weather_locations = []
    for index, row in geocoded_locations_df.iterrows():
        weather = get_weather(row['lat'], row['lon'])  # Call weather API
        
        # Extract weather data from API response
        temp = weather['current']['temperature_2m']
        precip = weather['current']['precipitation']
        
        # Create output record
        weather_item = {
            'location': row['location'],  # Preserve location info
            'lat': row['lat'],  # Preserve coordinates
            'lon': row['lon'],
            'temp': temp,  # Current temperature
            'precip': precip  # Current precipitation
        }
        weather_locations.append(weather_item)
    
    # Convert results to DataFrame
    weather_locations_df = pd.DataFrame(weather_locations)

    # Cache results to CSV and return DataFrame
    weather_locations_df.to_csv(WEATHER_CACHE_FILE, index=False, header=True)
    return weather_locations_df

if __name__ == '__main__':
    # File-based pipeline execution
    geocode_step(LOCATION_SOURCE_FILE)  # Step 1 (reads/writes files)
    weather_step(GEOCODE_CACHE_FILE)  # Step 2 (reads/writes files)
    weather_locations = pd.read_csv(WEATHER_CACHE_FILE)  # Load final results
    print("File-based pipeline results:")
    print(weather_locations)
