import requests  
import os        
from dotenv import load_dotenv  

# Loading environment variables from the .env file
load_dotenv()

# Retrieving the API key from the environment variables
api_key = os.getenv("TMDB_API_KEY") 

# Defining the base URL for TMDB API
base_url = "https://api.themoviedb.org/3/"

# Searching endpoint to search for movies
search_url = f"{base_url}search/movie"

# Setting the parameters for the API request
params = {
    "api_key": api_key,  
    "query": "Inception"  
}

# Making teh API request using GET method
response = requests.get(search_url, params=params)

# Checking if the request was successful
if response.status_code == 200:
    # Converting the JSON response to a Python dictionary
    movie_data = response.json()

    # Checking to see if works
    if movie_data['results']:
        print(f"Title: {movie_data['results'][0]['title']}")
        print(f"Release Date: {movie_data['results'][0]['release_date']}")
        print(f"Overview: {movie_data['results'][0]['overview']}")
    else:
        print("No movies found.")
else:
    # Printing the error status, If teh code doesn't work
    print(f"Error: {response.status_code} - {response.text}")
