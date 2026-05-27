import sqlite3
import pandas as pd

def load_to_db(df, db_name="hacker_news.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY,
            title TEXT,
            score INTEGER,
            author TEXT,
            comments INTEGER,
            engagement INTEGER,
            url TEXT,
            posted_at TEXT,
            date_fetched TEXT
        )
    """)

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR IGNORE INTO stories 
            (id, title, score, author, comments, engagement, url, posted_at, date_fetched)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row['id'], row['title'], row['score'], row['author'],
            row['comments'], row['engagement'], row['url'],
            str(row['posted_at']), row['date_fetched']
        ))

    conn.commit()
    conn.close()
    print(f"✓ {len(df)} stories loaded into {db_name}")

def query_top_stories(db_name="hacker_news.db"):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("""
        SELECT title, score, comments, engagement 
        FROM stories 
        ORDER BY engagement DESC 
        LIMIT 10
    """, conn)
    conn.close()
    return df