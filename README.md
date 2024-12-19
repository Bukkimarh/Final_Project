# Final Project - sonyl pls give me a 100 plsplsplsplsplsplsplsplspls
# Movie Performance Analysis: Post-COVID Era

## Project Description
In the post-COVID era, the film industry has evolved with streaming platforms, shifting audience preferences, and box office dynamics. This project, by Bukola and Jeremiah, analyzes patterns in movie performance using data from **TMDb** and **NYT**. We explore:
- **Genres**: Trends in popularity and critical reception.
- **A-list actors**: Impact on movie success.
- **Release platforms**: Influence on audience reception.

---

## Features

### Genre Analysis
- Tracks TMDb ratings and NYT mentions for Action, Drama, and Comedy genres.
- Evaluates trends over time (2020-2024).

### Actor Analysis
- Analyzes movies by A-list actors (e.g., Will Smith, Adam Sandler).
- Measures average TMDb ratings and NYT reviews.

### Visualization
- Line plots for genre trends.
- Bar charts comparing actor performance.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bukkimarh/Final_Project.git
   cd Final_Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add API keys to `.env`:
   ```
   TMDB_API_KEY=your_tmdb_api_key
   NYT_API_KEY=your_nyt_api_key
   ```

4. Run the project:
   ```bash
   python Final_Project.py
   ```

---

## Usage
- Calculates TMDb ratings and NYT mentions for genres.
- Analyzes A-list actors' movie performances.
- Visualizations include:
  - **Line plots**: Genre ratings over time.
  - **Bar charts**: Actor performance metrics.

---

## APIs Used
1. **TMDb API**:
   - Fetches genre and movie details.
   - [TMDb API Docs](https://www.themoviedb.org/documentation/api).

2. **NYT API**:
   - Retrieves article mentions and reviews.
   - [NYT API Docs](https://developer.nytimes.com/).

---

## Visualization Examples

### Genre Analysis
![Line Plot Example](example_line_plot.png)

### Actor Analysis
![Bar Plot Example](example_actor_analysis.png)

---

## Contributing
Contributions are welcome! Open an issue or submit a pull request.

---

## License
Licensed under the MIT License. See `LICENSE` for details.
