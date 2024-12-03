from dotenv import load_dotenv 
import os                      
import requests               

# Loading environment variables from .env file
load_dotenv()

# Retrieving API key from environment variables
api_key = os.getenv("OMDB_API_KEY")

# Base URL for OMDb API
base_url = "http://www.omdbapi.com/"

# Tesing to see if the code works
params = {
    "t": "Inception",  # Movie title
    "apikey": api_key  
}

# Making the API request
response = requests.get(base_url, params=params)

# Checking the response status
if response.status_code == 200:
    movie_data = response.json()
    print(movie_data)  
else:
    print(f"Error: {response.status_code}")  