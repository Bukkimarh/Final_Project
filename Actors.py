import os
import asyncio
import aiohttp
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
NYT_API_KEY = os.getenv("NYT_API_KEY")

class APIBase:
    """Base class to interact with APIs asynchronously"""
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

class TMDBAPI(APIBase):
    """Class to interact with the TMDb API asynchronously"""
    def __init__(self, api_key):
        super().__init__("https://api.themoviedb.org/3/", api_key)

    async def get_person_id(self, session, person_name):
        """Fetch the TMDb ID for a given person."""
        url = f"{self.base_url}search/person"
        params = {"api_key": self.api_key, "query": person_name}
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    if results:
                        return results[0]['id']
                    else:
                        raise ValueError(f"No person found for {person_name}.")
                else:
                    raise Exception(f"Error fetching person ID: {response.status}")
        except Exception as e:
            print(f"Error occurred in TMDBAPI.get_person_id: {e}")

    async def fetch_movies(self, session, person_id, start_year, end_year):
        """Fetch movies starring a specific person within a time frame."""
        url = f"{self.base_url}discover/movie"
        params = {
            "api_key": self.api_key,
            "with_cast": person_id,
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
            "sort_by": "release_date.asc",
        }
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Error fetching movies: {response.status}")
        except Exception as e:
            print(f"Error occurred in TMDBAPI.fetch_movies: {e}")

class NYTAPI(APIBase):
    """Class to interact with the New York Times API asynchronously"""
    def __init__(self, api_key):
        super().__init__("https://api.nytimes.com/svc/search/v2/articlesearch.json", api_key)

    async def fetch_nyt_reviews(self, session, movie_title):
        """Fetch the number of NYT reviews for a specific movie title."""
        url = self.base_url
        params = {
            "q": movie_title,
            "fq": 'section_name:"Movies" AND type_of_material:"Review"',
            "api-key": self.api_key
        }
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    review_data = await response.json()
                    return len(review_data['response']['docs'])  # Count of reviews
                elif response.status == 429:
                    print(f"Rate limit hit for {movie_title}. Retrying after delay...")
                    await asyncio.sleep(5)  # Pause to prevent further rate limits
                    return await self.fetch_nyt_reviews(session, movie_title)
                else:
                    raise Exception(f"Error fetching NYT reviews for {movie_title}: {response.status}")
        except Exception as e:
            print(f"Error occurred in NYTAPI.fetch_nyt_reviews: {e}")

class ActorAnalysis:
    """Class to analyze movies of a specific actor with error handling."""
    def __init__(self, tmdb_api_key, nyt_api_key):
        self.tmdb = TMDBAPI(tmdb_api_key)
        self.nyt = NYTAPI(nyt_api_key)

    async def analyze_actor(self, actor_name, start_year, end_year):
        """Analyze movies of a specific actor within a time period."""
        async with aiohttp.ClientSession() as session:
            try:
                # Get person ID from TMDB
                person_id = await self.tmdb.get_person_id(session, actor_name)
                if not person_id:
                    print(f"No person found for {actor_name}.")
                    return []

                # Fetch movies for the actor
                movies_data = await self.tmdb.fetch_movies(session, person_id, start_year, end_year)
                if not movies_data:
                    print(f"No movies found for {actor_name}.")
                    return []

                analysis_results = []
                for movie in movies_data.get('results', []):
                    title = movie.get('title', 'Unknown Title')
                    rating = movie.get('vote_average', 0.0)
                    nyt_reviews = await self.nyt.fetch_nyt_reviews(session, title)
                    analysis_results.append({
                        "title": title,
                        "rating": rating,
                        "nyt_reviews": nyt_reviews
                    })
                return analysis_results
            except Exception as e:
                print(f"Error occurred in ActorAnalysis.analyze_actor: {e}")

async def main():
    actor_names = ["Will Smith", "Adam Sandler"]
    start_year, end_year = 2020, 2024

    analysis = ActorAnalysis(TMDB_API_KEY, NYT_API_KEY)

    results_summary = {}
    for actor in actor_names:
        print(f"\nAnalyzing {actor} from {start_year} to {end_year}...\n")
        results = await analysis.analyze_actor(actor, start_year, end_year)

        if results:
            num_movies = len(results)
            avg_rating = sum(movie['rating'] for movie in results) / num_movies if num_movies > 0 else 0
            total_nyt_reviews = sum(movie['nyt_reviews'] for movie in results)

            results_summary[actor] = {
                "num_movies": num_movies,
                "avg_rating": avg_rating,
                "nyt_reviews": total_nyt_reviews,
            }

            print(f"Analysis for {actor} ({start_year}-{end_year}):")
            print(f"Number of Movies and events: {num_movies}")
            print(f"Average TMDB Rating: {avg_rating:.2f}")
            print(f"Total NYT Reviews: {total_nyt_reviews}")
            print("\nDetailed Results:")
            for movie in results:
                print(f"{movie['title']} - Rating: {movie['rating']} - NYT Reviews: {movie['nyt_reviews']}")
        else:
            print(f"No data found for {actor}.")

    # Visualization
    actors = list(results_summary.keys())
    num_movies = [results_summary[actor]['num_movies'] for actor in actors]
    avg_ratings = [results_summary[actor]['avg_rating'] for actor in actors]
    nyt_reviews = [results_summary[actor]['nyt_reviews'] for actor in actors]

    x = np.arange(len(actors))
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - bar_width, num_movies, bar_width, label="Number of Movies", color="skyblue")
    bars2 = ax.bar(x, avg_ratings, bar_width, label="Average Rating", color="lightgreen")
    bars3 = ax.bar(x + bar_width, nyt_reviews, bar_width, label="NYT Reviews", color="salmon")

    ax.set_xlabel("Actors", fontsize=12)
    ax.set_ylabel("Values", fontsize=12)
    ax.set_title("Actor Analysis (2020-2024)", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(actors, fontsize=10)
    ax.legend(fontsize=10)

    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
