import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (if running locally)
load_dotenv()

# API Keys & Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PIXAZO_API_KEY = os.getenv("PIXAZO_API_KEY", "b38ee7a3d7464c4fb3d1210c1a36b35f")
GOOGLE_SHEET_WEBAPP_URL = os.getenv("GOOGLE_SHEET_WEBAPP_URL", "")

# Directory Structures
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
ARTICLES_JSON_PATH = FRONTEND_DIR / "public" / "data" / "articles.json"
ASSETS_DIR = FRONTEND_DIR / "public" / "assets"

# Ensure directories exist
ARTICLES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Default niches list in case Google Sheets doesn't have any input niches yet
DEFAULT_NICHES = ["Tech", "Artificial Intelligence", "AI Tools"]

# RSS Feeds to scrape trending topics from
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=technology+OR+artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/hackernews",
    "https://wired.com/feed/rss"
]

# Smart Affiliate Link Injection Mapping
# Structure: "keyword/phrase": {"url": "your_affiliate_link", "text": "Affiliate Display Name"}
# You can easily edit these URLs below to start earning money immediately!
AFFILIATE_LINKS = {
    "hostinger": {
        "url": "https://www.hostinger.com/?referral=placeholder_id",
        "text": "Hostinger Premium Web Hosting"
    },
    "web hosting": {
        "url": "https://www.hostinger.com/?referral=placeholder_id",
        "text": "Premium Web Hosting Solutions"
    },
    "nordvpn": {
        "url": "https://go.nordvpn.net/aff_c?offer_id=placeholder_id",
        "text": "NordVPN Security Suite"
    },
    "vpn": {
        "url": "https://go.nordvpn.net/aff_c?offer_id=placeholder_id",
        "text": "Secure VPN Service"
    },
    "chatgpt": {
        "url": "https://openai.com/blog/chatgpt",
        "text": "ChatGPT Plus"
    },
    "jasper": {
        "url": "https://www.jasper.ai/?utm_source=affiliate&fp_ref=placeholder_id",
        "text": "Jasper AI Copywriter"
    },
    "copy.ai": {
        "url": "https://www.copy.ai/?fp_ref=placeholder_id",
        "text": "Copy.ai Writing Tool"
    },
    "flux": {
        "url": "https://huggingface.co/black-forest-labs/FLUX.1-schnell",
        "text": "FLUX.1 Image Engine"
    }
}
