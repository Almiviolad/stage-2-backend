🌍 Country Currency & Exchange API
Table of Contents
 * Overview
 * Features
 * Technology Stack
 * Setup and Installation
 * Running the Application
 * API Endpoints
1. Overview
This project is a high-performance RESTful API built to fetch country and currency data from external sources, process it (including dynamic GDP calculation), and cache the results in a database for fast retrieval, filtering, and sorting.
The primary function is the caching mechanism (POST /countries/refresh) which implements robust Update-or-Insert (UPSERT) logic to maintain data integrity and concurrency, replacing the entire cache on demand.
2. Features
 * Caching & Refresh: Implement a full cache refresh using a single, efficient SQLAlchemy ON CONFLICT UPSERT transaction.
 * Data Processing: Computes estimated_gdp based on population, a random multiplier, and USD exchange rates.
 * CRUD Operations: Full support for retrieving, filtering, sorting, and deleting cached country data.
 * Dynamic Image Generation: Generates and serves a summary image (/countries/image) showing cache statistics and top countries by GDP using Matplotlib.
 * Robust Error Handling: Consistent JSON error responses for 400 Bad Request, 404 Not Found, and 503 Service Unavailable (for external API failures).
3. Technology Stack
| Component | Library / Technology | Purpose |
|---|---|---|
| Framework | FastAPI | High-performance, asynchronous web serving and automatic validation. |
| Data Validation | Pydantic V2 | Enforces data schemas for API requests and responses. |
| Database | MySQL (Required for Submission) | Production-grade relational database for persistence and concurrency. |
| ORM | SQLAlchemy | Object-Relational Mapper for interacting with MySQL/SQLite. |
| HTTP Client | httpx & asyncio | Asynchronous, concurrent fetching from external APIs. |
| Image Generation | Matplotlib | Generating the summary.png chart file. |
4. Setup and Installation
A. Prerequisites
 * Python 3.10+ installed.
 * MySQL Server (or a local substitute like Docker/XAMPP) running.
B. Project Setup
 * Clone the repository:
   git clone [YOUR_REPO_LINK]
cd [YOUR_REPO_NAME]

 * Create and activate a virtual environment:
   python -m venv env
source env/bin/activate  # Use env\Scripts\activate on Windows

 * Install dependencies:
   pip install -r requirements.txt # (Assuming you created this file)
# OR: pip install fastapi uvicorn[standard] python-dotenv httpx sqlalchemy mysql-connector-python matplotlib pandas

 * Configure Environment Variables:
   Create a file named .env in the root directory and add your MySQL connection string:
   # .env
# CRUCIAL: Replace with your actual MySQL credentials
DB_CONNECTION_URL="mysql+mysqlconnector://user:password@localhost:3306/country_db"

5. Running the Application
 * Start the server:
   The application will automatically create the database tables upon startup using the @app.on_event("startup") hook.
   uvicorn main:app --reload

   The API will be available at http://127.0.0.1:8000.
 * Access Documentation:
   * Swagger UI: http://127.0.0.1:8000/docs
   * ReDoc: http://127.0.0.1:8000/redoc
6. API Endpoints
| Method | Path | Description |
|---|---|---|
| POST | /countries/refresh | Fetches all countries, calculates GDP, performs UPSERT logic on the DB, and generates the summary image. (Must be run first) |
| GET | /countries | Retrieves all cached countries. |
| GET | /countries?region=X&sort=Y | Retrieves countries with optional filtering (region, currency) and sorting (gdp_desc, population_asc). |
| GET | /countries/{name} | Retrieves a single country by name (case-insensitive). |
| DELETE | /countries/{name} | Deletes a country record from the cache. |
| GET | /status | Shows the total number of cached countries and the last_refreshed_at timestamp. |
| GET | /countries/image | Serves the generated summary.png chart file. |
