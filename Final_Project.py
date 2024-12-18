import requests
import os
import time
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import numpy as np

# Load API keys from .env file
load_dotenv()

class ActorAnalysis:
    def __init__(self, tmdb_api_key, nyt_api_key):
        """Initialize the ActorAnalysis class with TMDB and NYT API keys."""
        self.tmdb_api_key = tmdb_api_key
        self.nyt_api_key = nyt_api_key
        self.tmdb_base_url = "https://api.themoviedb.org/3/"
        self.nyt_base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"

    def get_person_id(self, person_name):
        """Fetch the TMDB ID for a given person."""
        params = {"api_key": self.tmdb_api_key, "query": person_name}
        response = requests.get(f"{self.tmdb_base_url}search/person", params=params)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if results:
                print(f"Found person ID: {results[0]['id']} for {person_name}")
                return results[0]['id']
            else:
                print(f"No person found for {person_name}.")
                return None
        else:
            print(f"Error fetching person ID: {response.status_code}")
            return None

    def fetch_movies_by_person(self, person_id, start_year, end_year):
        """Fetch movies starring a specific person between start_year and end_year."""
        movies = []
        params = {
            "api_key": self.tmdb_api_key,
            "language": "en-US",
            "sort_by": "release_date.asc",
            "include_adult": False,
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
            "with_cast": person_id,
        }
        response = requests.get(f"{self.tmdb_base_url}discover/movie", params=params)
        if response.status_code == 200:
            data = response.json()
            for movie in data['results']:
                release_date = movie.get("release_date", "Unknown Date")
                rating = movie.get("vote_average", 0.0)
                title = movie.get("title", "Unknown Title")
                movies.append({"title": title, "rating": rating, "release_date": release_date})
        else:
            print(f"Error fetching movies: {response.status_code}")
        return movies

    def fetch_nyt_reviews(self, movie_title):
        """Fetch the number of NYT reviews for a specific movie title."""
        params = {
            "q": movie_title,
            "fq": 'section_name:"Movies" AND type_of_material:"Review"',
            "api-key": self.nyt_api_key
        }
        response = requests.get(self.nyt_base_url, params=params)
        if response.status_code == 200:
            review_data = response.json()
            return len(review_data['response']['docs'])  # Count of reviews
        elif response.status_code == 429:
            print(f"Rate limit hit for {movie_title}. Retrying after delay...")
            time.sleep(5)  # Pause to prevent further rate limits
            return self.fetch_nyt_reviews(movie_title)
        else:
            print(f"Error fetching NYT reviews for {movie_title}: {response.status_code}")
            return 0

    def analyze_actor(self, actor_name, start_year, end_year):
        """Analyze movies of a specific actor within a time period."""
        person_id = self.get_person_id(actor_name)
        if not person_id:
            return []

        movies = self.fetch_movies_by_person(person_id, start_year, end_year)
        analysis_results = []

        for movie in movies:
            title = movie['title']
            rating = movie['rating']
            nyt_reviews = self.fetch_nyt_reviews(title)
            analysis_results.append({"title": title, "rating": rating, "nyt_reviews": nyt_reviews})

        return analysis_results

if __name__ == "__main__":
    # Load API keys from environment variables
    tmdb_api_key = os.getenv("TMDB_API_KEY")
    nyt_api_key = os.getenv("NYT_API_KEY")

    # Ensure API keys are loaded
    if not tmdb_api_key or not nyt_api_key:
        print("Error: Missing API keys! Please check your .env file.")
    else:
        print("API keys loaded successfully!")

        # Create an instance of ActorAnalysis
        analysis = ActorAnalysis(tmdb_api_key, nyt_api_key)

        # Analyze Will Smith and Adam Sandler movies between 2010 and 2020
        actors = ["Will Smith", "Adam Sandler"]
        start_year, end_year = 2010, 2020

        results_summary = {}
        for actor in actors:
            print(f"\nFetching data for {actor}...\n")
            results = analysis.analyze_actor(actor, start_year, end_year)

            # Calculate metrics
            num_movies = len(results)
            avg_rating = sum(movie['rating'] for movie in results) / num_movies if num_movies > 0 else 0
            total_nyt_reviews = sum(movie['nyt_reviews'] for movie in results)

            results_summary[actor] = {
                "num_movies": num_movies,
                "avg_rating": avg_rating,
                "nyt_reviews": total_nyt_reviews,
            }

            print(f"Analysis for {actor} ({start_year}-{end_year}):")
            print(f"Number of Movies: {num_movies}")
            print(f"Average TMDB Rating: {avg_rating:.2f}")
            print(f"Total NYT Reviews: {total_nyt_reviews}")
            print("\nDetailed Results:")
            for movie in results:
                print(f"{movie['title']} - Rating: {movie['rating']} - NYT Reviews: {movie['nyt_reviews']}")

        # Visualization
actors = ['Will Smith', 'Adam Sandler']
average_ratings = [5.59, 6.10]  # Replace with actual averages
nyt_reviews = [139, 127]       # Replace with actual totals

# Create a side-by-side bar chart
x = np.arange(len(actors))  # Actor positions
width = 0.35  # Bar width

fig, ax = plt.subplots(figsize=(10, 6))
bar1 = ax.bar(x - width/2, average_ratings, width, label='Average TMDB Ratings', color='steelblue')
bar2 = ax.bar(x + width/2, nyt_reviews, width, label='NYT Review Counts', color='coral')

# Add labels, title, and legend
ax.set_xlabel('Actors')
ax.set_ylabel('Values')
ax.set_title('Comparison of Ratings and NYT Reviews (2010-2020)')
ax.set_xticks(x)
ax.set_xticklabels(actors)
ax.legend()

# Add values on top of bars
def add_values(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', 
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Offset text
                    textcoords="offset points",
                    ha='center', va='bottom')

add_values(bar1)
add_values(bar2)
plt.tight_layout()
plt.show()
