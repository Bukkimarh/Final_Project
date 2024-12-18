import os
import asyncio
import aiohttp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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

    async def get_genre_id(self, session, genre_name):
        """Fetch the TMDb ID for a given genre name."""
        url = f"{self.base_url}genre/movie/list"
        params = {"api_key": self.api_key, "language": "en-US"}
        async with session.get(url, params=params) as response:
            if response.status == 200:
                genres = (await response.json()).get("genres", [])
                for genre in genres:
                    if genre["name"].lower() == genre_name.lower():
                        return genre["id"]
        raise ValueError(f"Genre '{genre_name}' not found.")

    async def fetch_movies(self, session, genre_id, page, start_year, end_year):
        """Fetch movies by genre ID for a specific range of years on a specific page."""
        url = f"{self.base_url}discover/movie"
        params = {
            "api_key": self.api_key,
            "with_genres": genre_id,
            "primary_release_date.gte": f"{start_year}-01-01",
            "primary_release_date.lte": f"{end_year}-12-31",
            "page": page,
            "sort_by": "popularity.desc",
            "vote_count.gte": 1
        }
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Error fetching movies: {response.status}")

class NYTAPI(APIBase):
    """Class to interact with the New York Times API"""
    def __init__(self, api_key):
        super().__init__("https://api.nytimes.com/svc/search/v2/articlesearch.json", api_key)

    async def fetch_mentions(self, session, query, start_year, end_year):
        """Fetch the number of mentions of a keyword in NYT articles with rate-limiting."""
        total_mentions = 0
        for year in range(start_year, end_year + 1):
            url = self.base_url
            params = {
                "q": query,
                "api-key": self.api_key,
                "facet": "false",
                "begin_date": f"{year}0101",
                "end_date": f"{year}1231",
            }
            retry_attempts = 3  # Number of retries for each request
            while retry_attempts > 0:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        total_mentions += data.get('response', {}).get('meta', {}).get('hits', 0)
                        break
                    elif response.status == 429:  # Too Many Requests
                        print(f"Rate limit hit. Retrying for {query} in {year} after a delay...")
                        await asyncio.sleep(10)  # Wait 10 seconds before retrying
                        retry_attempts -= 1
                    else:
                        print(f"Error fetching mentions for {query} in {year}: {response.status}")
                        break
        return total_mentions

class MultiYearGenreCalculator:
    """Class to calculate ratings and mentions for multiple years and genres."""
    def __init__(self, tmdb_api_key, nyt_api_key):
        self.tmdb = TMDBAPI(tmdb_api_key)
        self.nyt = NYTAPI(nyt_api_key)

    async def calculate_ratings_and_mentions(self, genres, year_ranges, sample_pages):
        """Calculate ratings and mentions for multiple genres and year ranges."""
        async with aiohttp.ClientSession() as session:
            results = []
            seen_results = set()  # To track unique entries
            for start_year, end_year in year_ranges:
                print(f"\nCalculating ratings and mentions for years {start_year}-{end_year}...")
                for genre in genres:
                    print(f"Processing genre: {genre}")
                    try:
                        genre_id = await self.tmdb.get_genre_id(session, genre)
                        avg_rating = await self._calculate_ratings_for_range(
                            session, genre_id, start_year, end_year, sample_pages
                        )
                        mentions = await self.nyt.fetch_mentions(session, genre, start_year, end_year)
                        result = (genre, f"{start_year}-{end_year}", avg_rating, mentions)
                        if result not in seen_results:  # Avoid duplicates
                            seen_results.add(result)
                            results.append({
                                "Genre": genre,
                                "YearRange": f"{start_year}-{end_year}",
                                "AverageRating": avg_rating,
                                "Mentions": mentions
                            })
                    except ValueError as e:
                        print(e)
            return results

    async def _calculate_ratings_for_range(self, session, genre_id, start_year, end_year, sample_pages):
        """Helper method to calculate average ratings for a specific range."""
        total_rating = 0
        total_movies = 0
        tasks = [
            self.tmdb.fetch_movies(session, genre_id, page, start_year, end_year)
            for page in range(1, sample_pages + 1)
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                print(response)
                continue
            movies = response.get("results", [])
            for movie in movies:
                total_rating += movie.get("vote_average", 0)
                total_movies += 1

        if total_movies > 0:
            return total_rating / total_movies
        return None

async def main():
    genres = ["Action", "Drama", "Comedy"]
    year_ranges = [(2020, 2021), (2021, 2022), (2022, 2023), (2023, 2024)]
    sample_pages = 5  # Number of pages to sample

    calculator = MultiYearGenreCalculator(TMDB_API_KEY, NYT_API_KEY)
    ratings_and_mentions = await calculator.calculate_ratings_and_mentions(genres, year_ranges, sample_pages)

    # Convert results to DataFrame for visualization
    df = pd.DataFrame(ratings_and_mentions).drop_duplicates()  # Drop duplicates
    print("\nRatings and Mentions DataFrame:")
    print(df)

    # Filter out rows with missing data
    df = df.dropna(subset=["AverageRating"])

    # Plotting with Seaborn
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 8))
    sns.lineplot(
        data=df,
        x="YearRange",
        y="AverageRating",
        hue="Genre",
        marker="o"
    )
    plt.title("Average Movie Ratings by Genre Over Time")
    plt.xlabel("Year Range")
    plt.ylabel("Average Rating")
    plt.legend(title="Genre")
    plt.tight_layout()
    plt.show()

    # Mentions Plot
    plt.figure(figsize=(12, 8))
    sns.barplot(
        data=df,
        x="YearRange",
        y="Mentions",
        hue="Genre"
    )
    plt.title("Mentions by Genre in NYT Over Time")
    plt.xlabel("Year Range")
    plt.ylabel("Mentions")
    plt.legend(title="Genre")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())

