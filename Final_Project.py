import requests  
import os        
from dotenv import load_dotenv  

# Loading API keys from the .env file
load_dotenv()

class MovieSearch:
    def __init__(self, tmdb_api_key, nyt_api_key):
        # Initializing the class with the API keys
        self.tmdb_api_key = tmdb_api_key
        self.nyt_api_key = nyt_api_key
        self.tmdb_base_url = "https://api.themoviedb.org/3/"
        self.nyt_base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    def search_movie(self, movie_name):
        """Search for a movie using the TMDB API"""
        # Creating the URL to search for the movie
        search_url = f"{self.tmdb_base_url}search/movie"
        
        # Parameters to send in the API request
        params = {
            "api_key": self.tmdb_api_key,  #  TMDB API key
            "query": movie_name  
        }

        # Sending a GET request to TMDB API
        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            movie_data = response.json()

            # Checking if the movie was found
            if movie_data['results']:
                print(f"Title: {movie_data['results'][0]['title']}")
                print(f"Release Date: {movie_data['results'][0]['release_date']}")
                print(f"Overview: {movie_data['results'][0]['overview']}")
                return movie_data['results'][0]['title'] 
            else:
                print("No movies found.")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def search_movie_reviews(self, movie_name):
        """Search for movie reviews using the NYT Article Search API"""
        # Parameters to send in the API request to search for movie reviews
        params = {
            "q": movie_name, 
            "fq": 'section_name:"Movies" AND type_of_material:"Review"',  
            "api-key": self.nyt_api_key,  
            "page": 0  
        }

        # Sending a GET request to NYT API
        response = requests.get(self.nyt_base_url, params=params)

        if response.status_code == 200:
            # If the request was successful
            review_data = response.json()

            # Checking if reviews are available
            if review_data['response']['docs']:
                print("\nMovie Reviews:")
                # Loop through each article
                for article in review_data['response']['docs']:
                    print(f"Title: {article['headline']['main']}")
                    print(f"Snippet: {article['snippet']}")
                    print(f"URL: {article['web_url']}")
                    print("-------------")
            else:
                print("No reviews found.")
        else:
            print(f"Error: {response.status_code} - {response.text}")

class MovieReview:
    def __init__(self, tmdb_api_key, nyt_api_key):
        self.movie_search = MovieSearch(tmdb_api_key, nyt_api_key)

    def run(self, movie_name):
        movie_title = self.movie_search.search_movie(movie_name)

        # If the movie is found, search for reviews
        if movie_title:
            self.movie_search.search_movie_reviews(movie_title)

if __name__ == "__main__":
    # Retrieving the API keys from environment variables
    tmdb_api_key = os.getenv("TMDB_API_KEY") 
    nyt_api_key = os.getenv("NYT_API_KEY")

    # Creating an instance of the app and running it
    app = MovieReview(tmdb_api_key, nyt_api_key)
    app.run("Inception")  
