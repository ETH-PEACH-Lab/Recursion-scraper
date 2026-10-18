# LeetCode Recursion Scraper

A Python web scraper for collecting LeetCode problems tagged with "recursion", including their tutorials and solutions.

## Features

- 🔍 Scrapes all LeetCode problems from the recursion problem list
- 📚 Fetches problem details, content, and official tutorials
- 🎯 **Filters solutions containing "recursion" keyword**
- 🎬 **Only collects solutions with video or images**
- 💾 Exports data to both JSON and CSV formats
- ⏱️ Rate limiting to respect LeetCode's servers
- 📊 Progress tracking with tqdm
- 🔐 Support for premium content (with session cookie)

## Project Structure

```
recursion_scraper/
├── scraper.py          # Main scraper implementation
├── models.py           # Data models for problems and solutions
├── utils.py            # Utility functions (saving, logging, etc.)
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
├── .gitignore         # Git ignore rules
├── output/            # Output directory for scraped data
└── README.md          # This file
```

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd recursion_scraper
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **⚠️ IMPORTANT: Configure LeetCode login (Required)**
   
   Community solutions require authentication. Follow the detailed guide:
   
   **→ 查看详细中文指南：[获取Cookie指南.md](获取Cookie指南.md)**
   
   Quick steps:
   - Log into LeetCode in your browser
   - Open DevTools (F12), go to Application/Storage → Cookies
   - Copy `LEETCODE_SESSION` and `csrftoken` values
   - Create `.env` file and add them:
     ```bash
     cp .env.example .env
     # Edit .env with your cookie values
     ```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python scraper.py
```

This will:
1. Fetch all recursion problems from LeetCode's problem list
2. Get detailed information for each problem
3. **Fetch community solutions that:**
   - Contain the keyword "recursion"
   - Include video or images
4. Save results to:
   - `output/recursion_problems.json` - Full problem details with filtered solutions
   - `output/recursion_problems.csv` - Problem summary
   - `output/filtered_solutions.json` - All filtered solutions details
   - `output/filtered_solutions.csv` - Solutions summary table

### Configuration

- `KEYWORD_FILTER`: Keyword to filter solutions (default: "recursion")
- `REQUIRE_MEDIA`: Only get solutions with video/images (default: True)
Edit `.env` file or `config.py` to customize:

- `DELAY_BETWEEN_REQUESTS`: Delay between API calls (default: 2 seconds)
- `MAX_RETRIES`: Maximum retry attempts for failed requests
- `TIMEOUT`: Request timeout in seconds
- `OUTPUT_FORMAT`: Output format (json/csv)
- `OUTPUT_DIR`: Output directory path

### Authentication Setup

**Community solutions require login credentials.**

See detailed guide: **[获取Cookie指南.md](获取Cookie指南.md)** (Chinese)

Quick summary:
1. Log into LeetCode in browser
2. Open DevTools (F12) → Application/Storage → Cookies
3. Copy `LEETCODE_SESSION` and `csrftoken` values
4. Add to `.env` file

Without authentication, the scraper will not be able to access community solutions.

## Output Format

### JSON Output (`recursion_problems.json`)

Full detailed information for each problem:

```json
[
  {
    "title": "Climbing Stairs",
    "title_slug": "climbing-stairs",
    "question_id": "70",
    "difficulty": "Easy",
    "topic_tags": ["Math", "Dynamic Programming", "Recursion"],
    "url": "https://leetcode.com/problems/climbing-stairs/",
    "content": "...",
    "tutorial": "...",
    "solutions": []
  }
]
```

### CSV Output (`recursion_problems.csv`)

Simplified table format: solutions_count | solutions_with_media |
|-------------|-------|------------|-----|--------------|-----------------|----------------------|
| 70 | Climbing Stairs | Easy | https://... | true | 3 | 3 |

### Filtered Solutions Output

**`filtered_solutions.json`** - All solutions that match the filters (contain "recursion" + have video/images)

**`filtered_solutions.csv`** - Solution summary table with:
- Problem information (ID, title, URL)
- Solution details (ID, title, author)
- Media indicators (has_video, has_image)
- Engagement metrics (votes, created_at)
- Content previewial |
|-------------|-------|------------|-----|--------------|
| 70 | Climbing Stairs | Easy | https://... | true |

## Dependencies

- **Solutions are filtered to only include:**
  - Solutions containing the "recursion" keyword
  - Solutions with video or images embedded
- **beautifulsoup4**: HTML parsing (for solutions)
- **lxml**: Fast XML/HTML parser
- **pandas**: Data manipulation (optional)
- **python-dotenv**: Environment variable management
- **tqdm**: Progress bars
- **selenium/playwright**: Browser automation (optional, for JS-heavy pages)

## Notes

- The scraper respects rate limits with configurable delays between requests
- Some features (like community solutions) may require browser automation
- Premium content requires a valid session cookie
- Be respectful of LeetCode's terms of service and rate limits

## Troubleshooting

**No problems found:**
- Check your internet connection
- Verify LeetCode's API endpoint hasn't changed
- Check if you need authentication

**Premium content not accessible:**
- Verify your `LEETCODE_SESSION` cookie is valid
- Try logging out and back in to get a fresh cookie

**Rate limiting errors:**
- Increase `DELAY_BETWEEN_REQUESTS` in config
- Reduce the number of concurrent requests

## License

This project is for educational purposes only. Please respect LeetCode's terms of service and robots.txt.

## Contributing

Feel free to submit issues and enhancement requests!


## Recursion Diagram Atlas

`atlas/` holds an interactive design space for recursion diagrams built on this scrape (vote ≥ 5 recursive solutions) plus textbook figures. Open `atlas/index.html` in a browser. See `atlas/README.md` for what is inside, and `output/classified_solutions.html` for the per-image classification it builds on.
