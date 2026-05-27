# HACKER NEWS ETL PIPELINE
An end-to-end ETL (Extract, Transform, Load) pipeline that pulls trending stories from the Hacker News API, cleans and transforms the data, stores it in a SQLite database, and visualizes engagement trends.

## Pipeline Architecture
Extract -> Transform -> Load -> Visualize

## Features
- Extracts top 30 trending stories in real time from the Hacker News API
- Cleans and transforms raw data including null handling, type casting, 
  and Unix timestamp conversion
- Calculates a custom engagement score (upvotes + comments) per story
- Loads structured data into a SQLite database with duplicate prevention
- Visualizes trends across 3 charts: top stories by engagement, 
  score vs comments scatter plot, and average engagement by hour posted
- Summary stats panel showing total stories, average score, peak posting hour and top author

## Tech Stack
- Python, Pandas, SQLite, Matplotlib, SQLAlchemy, Requests

## Project Structure
- `etl.py` — Extract and Transform logic
- `database.py` — Load to SQLite and query functions
- `visualize.py` — Dashboard visualization
- `data/` — Stored charts and database

## How To Use
1. Clone Repository
2. Install dependencies (pandas, matplotlib, sqlalchemy, requests)
3. Run pipleline using etl.py file
3. Generate visualization useing visualize.py file

