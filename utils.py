"""
Utility functions for the scraper.
"""
import time
import logging
import json
import csv
from pathlib import Path
from typing import List
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Back to INFO level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_output_dir():
    """Create output directory if it doesn't exist."""
    output_path = Path(config.OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_path.absolute()}")
    return output_path


def save_to_json(data: List[dict], filename: str):
    """Save data to JSON file."""
    output_path = setup_output_dir()
    filepath = output_path / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(data)} items to {filepath}")


def save_to_csv(data: List[dict], filename: str):
    """Save data to CSV file."""
    if not data:
        logger.warning("No data to save to CSV")
        return
    
    output_path = setup_output_dir()
    filepath = output_path / filename
    
    keys = data[0].keys()
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    
    logger.info(f"Saved {len(data)} items to {filepath}")


def rate_limit(delay: float = None):
    """Add delay between requests to respect rate limits."""
    delay = delay or config.DELAY_BETWEEN_REQUESTS
    time.sleep(delay)


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text.strip()
