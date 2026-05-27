import requests
import pandas as pd
from datetime import datetime

# EXTRACT
def get_top_stories():
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    response = requests.get(url)
    story_ids = response.json()[:30]

    stories = []
    for story_id in story_ids:
        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
        story = requests.get(story_url).json()
        stories.append(story)
        print(f"Fetched: {story.get('title', 'No title')}")

    return stories
# TRANSFORM
def transform(stories):
    df = pd.DataFrame(stories)

    # Keep only useful columns
    df = df[['id', 'title', 'score', 'by', 'descendants', 'time', 'url']].copy()

    # Rename columns to be cleaner
    df.rename(columns={'by': 'author', 'descendants': 'comments'}, inplace=True)

    # Convert Unix timestamp to readable date
    df['posted_at'] = pd.to_datetime(df['time'], unit='s')
    df.drop(columns=['time'], inplace=True)

    # Fill missing values
    df['comments'] = df['comments'].fillna(0).astype(int)
    df['score'] = df['score'].fillna(0).astype(int)
    df['url'] = df['url'].fillna('self post')

    # Add engagement score (score + comments combined)
    df['engagement'] = df['score'] + df['comments']

    # Add extracted date for filtering
    df['date_fetched'] = datetime.now().strftime('%Y-%m-%d')

    return df

# MAIN
if __name__ == "__main__":
    print("Extracting stories...\n")
    stories = get_top_stories()

    print("\nTransforming data...")
    df = transform(stories)

    print("\nLoading to database...")
    from database import load_to_db, query_top_stories
    load_to_db(df)

    print("\nTop 10 stories by engagement:")
    print(query_top_stories().to_string(index=False))