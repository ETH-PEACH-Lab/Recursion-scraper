"""
Configuration settings for the LeetCode scraper.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# LeetCode URLs
LEETCODE_BASE_URL = "https://leetcode.com"
LEETCODE_API_URL = "https://leetcode.com/graphql"
LEETCODE_PROBLEMS_URL = "https://leetcode.com/problem-list/recursion/"

# Headers - Simpler configuration that works
HEADERS = {
    "User-Agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}

# Session cookie (if needed for premium content)
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION", "")
CSRF_TOKEN = os.getenv("CSRF_TOKEN", "")

# Don't add cookies to HEADERS - they will be added to session.cookies instead

# Scraping settings
DELAY_BETWEEN_REQUESTS = int(os.getenv("DELAY_BETWEEN_REQUESTS", 2))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
TIMEOUT = int(os.getenv("TIMEOUT", 30))

# Output settings
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# Search criteria
TOPIC_TAG = "recursion"
KEYWORD_FILTER = "recursion"  # Filter solutions containing this keyword
REQUIRE_MEDIA = True  # Only get solutions with video or images
