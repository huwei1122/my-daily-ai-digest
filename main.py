import feedparser
import datetime
import os
from openai import OpenAI

# Simple RSS-based AI daily digest demo
# Replace with your own RSS sources
RSS_URLS = ['https://hnrss.org/frontpage', 'https://feeds.bbci.co.uk/news/technology/rss.xml']
OUTPUT_FILE = 'daily_digest.md'

client = OpenAI(
    api_key=os.environ.get('OPENAI_API_KEY', 'your-api-key')
)

def fetch_news(urls):
    items = []
    for url in urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            items.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', datetime.date.today().isoformat())
            })
    return items

def summarize_with_llm(text):
    if not text:
        return "No content"
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a concise news summarizer."},
                {"role": "user", "content": f"Summarize in one sentence: {text[:200]}"}
            ],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary failed: {e}"

def generate_digest(news_items):
    digest_lines = [f"# Daily AI Digest - {datetime.date.today().isoformat()}\n"]
    for item in news_items:
        title = item['title']
        link = item['link']
        published = item['published'][:10] if item['published'] else ''
        summary = summarize_with_llm(title)
        digest_lines.append(f"## {title}\n- **Link:** {link}\n- **Published:** {published}\n- **Summary:** {summary}\n")
    return "\n".join(digest_lines)

if __name__ == '__main__':
    print("Fetching RSS feeds...")
    news = fetch_news(RSS_URLS)
    print(f"Fetched {len(news)} items.")
    digest = generate_digest(news)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(digest)
    print(f"Digest written to {OUTPUT_FILE}")
