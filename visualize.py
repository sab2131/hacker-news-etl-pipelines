import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from database import query_top_stories
import pandas as pd
import sqlite3
import textwrap

# ── Custom blue/purple colormap ─────────────────────────
DARK_BG = '#0d0d1a'
CARD_BG = '#13132b'
ACCENT1 = '#7b5ea7'
ACCENT2 = '#4e9af1'
TEXT = '#e0e0ff'
SUBTEXT = '#9999cc'

custom_cmap = LinearSegmentedColormap.from_list('bluepurple', ['#4e9af1', '#7b5ea7', '#c471ed'])

def get_full_data(db_name="hacker_news.db"):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("""
        SELECT title, score, comments, engagement, author, posted_at
        FROM stories
        ORDER BY engagement DESC
    """, conn)
    conn.close()
    df['posted_at'] = pd.to_datetime(df['posted_at'])
    df['hour'] = df['posted_at'].dt.hour
    return df

def style_ax(ax):
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=SUBTEXT, labelsize=9)
    ax.xaxis.label.set_color(SUBTEXT)
    ax.yaxis.label.set_color(SUBTEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor('#2a2a4a')

def shorten(title, width=35):
    # Smart shortening — keep most meaningful part
    words = title.split()
    short = textwrap.shorten(title, width=width, placeholder='...')
    return short

def plot_top_stories():
    df = get_full_data()
    top10 = df.head(10).copy()
    top10['label'] = top10['title'].apply(lambda x: shorten(x, 38))

    fig = plt.figure(figsize=(20, 12), facecolor=DARK_BG)
    fig.suptitle('Hacker News: Top Stories Engagement Analysis',
                 fontsize=18, fontweight='bold', color=TEXT, y=0.98)

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35,
                           left=0.22, right=0.96, top=0.92, bottom=0.08)

    ax1 = fig.add_subplot(gs[:, 0])   # Bar chart — full left column
    ax2 = fig.add_subplot(gs[0, 1])   # Scatter — top right
    ax3 = fig.add_subplot(gs[1, 1])   # Hour analysis — bottom right

    # ── Chart 1: Horizontal bar chart ──────────────────
    style_ax(ax1)
    norm_vals = (top10['engagement'] - top10['engagement'].min()) / \
                (top10['engagement'].max() - top10['engagement'].min())
    bar_colors = [custom_cmap(v) for v in norm_vals]

    bars = ax1.barh(top10['label'], top10['engagement'],
                    color=bar_colors, edgecolor='none', height=0.6)

    for bar, val in zip(bars, top10['engagement']):
        ax1.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
                f'{val}', va='center', ha='left', color=TEXT,
                fontsize=9, fontweight='bold')

    ax1.invert_yaxis()
    ax1.set_xlabel('Engagement Score (Upvotes + Comments)', color=SUBTEXT)
    ax1.set_title('Top 10 Stories by Engagement', fontsize=12, pad=10)
    ax1.set_xlim(0, top10['engagement'].max() * 1.15)
    ax1.tick_params(axis='y', labelsize=8.5, colors=TEXT)

    # ── Chart 2: Scatter plot ───────────────────────────
    style_ax(ax2)
    scatter = ax2.scatter(top10['score'], top10['comments'],
                          c=top10['engagement'], cmap=custom_cmap,
                          s=180, alpha=0.9, edgecolors='white', linewidth=0.5)

    top5 = top10.head(5)
    for _, row in top5.iterrows():
        short = shorten(row['title'], 22)
        ax2.annotate(short, (row['score'], row['comments']),
                    xytext=(8, 4), textcoords='offset points',
                    fontsize=7.5, color=TEXT,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#1e1e3f', alpha=0.8))

    cbar = plt.colorbar(scatter, ax=ax2, pad=0.02)
    cbar.set_label('Engagement', color=SUBTEXT, fontsize=8)
    cbar.ax.yaxis.set_tick_params(color=SUBTEXT)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=SUBTEXT, fontsize=7)

    ax2.set_xlabel('Score (Upvotes)', color=SUBTEXT)
    ax2.set_ylabel('Number of Comments', color=SUBTEXT)
    ax2.set_title('Score vs Comments', fontsize=12, pad=10)

    # ── Chart 3: Posts by hour ──────────────────────────
    style_ax(ax3)
    hour_counts = df.groupby('hour')['engagement'].mean().reset_index()

    ax3.fill_between(hour_counts['hour'], hour_counts['engagement'],
                     alpha=0.3, color=ACCENT2)
    ax3.plot(hour_counts['hour'], hour_counts['engagement'],
             color=ACCENT2, linewidth=2.5, marker='o', markersize=5)

    ax3.set_xlabel('Hour Posted (UTC)', color=SUBTEXT)
    ax3.set_ylabel('Average Engagement', color=SUBTEXT)
    ax3.set_title('Average Engagement by Hour Posted', fontsize=12, pad=10)
    ax3.set_xticks(range(0, 24, 2))

    # ── Summary stats panel ─────────────────────────────
    total_stories = len(df)
    avg_score = int(df['score'].mean())
    avg_comments = int(df['comments'].mean())
    top_author = df['author'].value_counts().idxmax()
    peak_hour = int(hour_counts.loc[hour_counts['engagement'].idxmax(), 'hour'])

    stats_text = (
        f"  📊  Stories Analyzed: {total_stories}      "
        f"⬆️  Average Score: {avg_score}      "
        f"💬  Average Comments: {avg_comments}      "
        f"👤  Top Author: {top_author}      "
        f"🕐  Peak Hour: {peak_hour}:00 UTC"
    )

    fig.text(0.5, 0.01, stats_text, ha='center', fontsize=9.5,
             color=TEXT, bbox=dict(boxstyle='round,pad=0.5',
             facecolor=CARD_BG, edgecolor=ACCENT1, alpha=0.9))

    plt.savefig('data/hacker_news_trends.png', dpi=150,
                bbox_inches='tight', facecolor=DARK_BG)
    plt.show()
    print("✓ Chart saved to data/hacker_news_trends.png")

if __name__ == "__main__":
    plot_top_stories()