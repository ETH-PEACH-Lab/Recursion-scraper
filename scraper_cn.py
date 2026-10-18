"""
LeetCode CN Recursion Scraper

Uses Playwright to bypass Cloudflare, then fetches via the browser's fetch API.
Output: output/recursion_problems_cn.json
"""
import asyncio
import json
import re
import logging
import os
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from tqdm import tqdm

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - cn_scraper - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

BASE_URL     = "https://leetcode.cn"
OUTPUT_FILE  = Path("output/recursion_problems_cn.json")
PAGE_SIZE    = 30
DELAY        = 1.0       # seconds between pages

CN_SESSION   = os.getenv("LEETCODE_CN_SESSION", "")
CN_CSRF      = os.getenv("CSRF_TOKEN_CN", "")

_IMG_RE = re.compile(
    r'!\[[^\]]*\]\(https?://[^\)]+\)|<img[^>]+src=["\']https?://[^"\']+["\']',
    re.IGNORECASE,
)
_SLIDE_RE = re.compile(
    r'<x-turnstile|slideshow|幻灯片|slide|!\[.*?\]\(.*?gif',
    re.IGNORECASE,
)
_VIDEO_RE = re.compile(
    r'bilibili\.com|b23\.tv|youtu|vimeo|<iframe|\.mp4|\.webm|loom\.com',
    re.IGNORECASE,
)


def _has_image(content: str) -> bool:
    return bool(_IMG_RE.search(content or ""))

def _has_video(content: str) -> bool:
    return bool(_VIDEO_RE.search(content or ""))

def _has_slide(content: str) -> bool:
    return bool(_SLIDE_RE.search(content or ""))

def _unescape(raw: str) -> str:
    return (
        raw.replace("\\n", "\n")
           .replace("\\t", "\t")
           .replace("\\'", "'")
           .replace('\\"', '"')
    )


async def make_gql(page, query: str, variables: dict = None) -> dict:
    result = await page.evaluate("""async ({query, variables, csrf}) => {
        const r = await fetch('/graphql/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-csrftoken': csrf,
                'authorization': '',
            },
            credentials: 'include',
            body: JSON.stringify({ query, variables }),
        });
        return { status: r.status, data: await r.json() };
    }""", {"query": query, "variables": variables or {}, "csrf": CN_CSRF})
    return result


async def fetch_problem_list(page) -> list:
    """Fetch all recursion problems from CN."""
    logger.info("Fetching CN recursion problem list...")
    query = """
    {
      problemsetQuestionList(categorySlug: "" limit: 500 skip: 0 filters: {tags: ["recursion"]}) {
        total
        questions {
          frontendQuestionId
          title
          titleCn
          titleSlug
          difficulty
          topicTags { name nameTranslated slug }
        }
      }
    }
    """
    r = await make_gql(page, query)
    if r["status"] != 200 or "errors" in r["data"]:
        logger.error(f"Problem list error: {r}")
        return []
    d = r["data"]["data"]["problemsetQuestionList"]
    logger.info(f"Found {d['total']} CN recursion problems")
    return d["questions"]


async def fetch_solutions(page, title_slug: str) -> list:
    """
    Fetch solution articles for a problem.
    Keeps:
    - byLeetcode=True (official)
    - OR (contains 递归 AND has image/video/slide)
    """
    query = """
    query sol($slug: String!, $first: Int!, $skip: Int!) {
      questionSolutionArticles(
        questionSlug: $slug
        orderBy: HOT
        tagSlugs: ["recursion"]
        first: $first
        skip: $skip
      ) {
        totalNum
        edges {
          node {
            uuid
            title
            slug
            upvoteCount
            hitCount
            createdAt
            content
            thumbnail
            hasVideo
            byLeetcode
            author { username }
          }
        }
      }
    }
    """

    all_nodes = []
    skip = 0
    total = None

    while True:
        r = await make_gql(page, query, {"slug": title_slug, "first": PAGE_SIZE, "skip": skip})
        if r["status"] != 200 or "errors" in r["data"]:
            logger.warning(f"Solutions error for {title_slug}: {r['data']}")
            break

        conn = r["data"]["data"]["questionSolutionArticles"]
        if total is None:
            total = conn["totalNum"]
            logger.info(f"  {title_slug}: {total} tagged solutions")

        edges = conn.get("edges") or []
        all_nodes.extend(e["node"] for e in edges)

        skip += PAGE_SIZE
        if skip >= total or not edges:
            break
        await asyncio.sleep(DELAY)

    # Deduplicate by uuid (skip-pagination can return overlapping pages)
    seen_uuids = set()
    deduped = []
    for node in all_nodes:
        uid = node.get("uuid")
        if uid and uid not in seen_uuids:
            seen_uuids.add(uid)
            deduped.append(node)
    all_nodes = deduped

    kept = []
    for node in all_nodes:
        content = _unescape(node.get("content") or "")
        is_official = node.get("byLeetcode", False)
        has_recursion = "递归" in (node.get("title") or "") or "递归" in content
        has_img = _has_image(content)
        has_vid = node.get("hasVideo", False) or _has_video(content)
        has_sld = _has_slide(content)
        has_media = has_img or has_vid or has_sld

        if is_official or (has_recursion and has_media):
            kept.append({
                "id": node["uuid"],
                "title": node.get("title", ""),
                "slug": node.get("slug", ""),
                "content": content,
                "has_video": has_vid,
                "has_image": has_img,
                "has_slide": has_sld,
                "is_official": is_official,
                "author": (node.get("author") or {}).get("username", "Unknown"),
                "votes": node.get("upvoteCount", 0),
                "hits": node.get("hitCount", 0),
                "created_at": node.get("createdAt", ""),
                "thumbnail": node.get("thumbnail", ""),
                "url": f"{BASE_URL}/problems/{title_slug}/solution/{node.get('slug', node['uuid'])}/",
            })

    logger.info(f"  → kept {len(kept)} solutions")
    return kept


async def scrape_all():
    async with async_playwright() as p:
        stealth = Stealth()
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            extra_http_headers={
                "sec-ch-ua": '"Google Chrome";v="122", "Chromium";v="122", "Not:A-Brand";v="8"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
            },
        )
        await ctx.add_cookies([
            {"name": "LEETCODE_SESSION", "value": CN_SESSION, "domain": ".leetcode.cn", "path": "/"},
            {"name": "csrftoken",         "value": CN_CSRF,    "domain": ".leetcode.cn", "path": "/"},
        ])
        page = await ctx.new_page()
        await stealth.apply_stealth_async(page)

        logger.info("Loading leetcode.cn to establish session...")
        await page.goto("https://leetcode.cn/problemset/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)

        problems_raw = await fetch_problem_list(page)
        if not problems_raw:
            logger.error("No problems fetched, aborting.")
            await browser.close()
            return

        problems = []
        for prob in tqdm(problems_raw, desc="Scraping CN problems"):
            slug = prob["titleSlug"]
            solutions = await fetch_solutions(page, slug)
            await asyncio.sleep(DELAY)

            problems.append({
                "question_id": prob["frontendQuestionId"],
                "title": prob["title"],
                "title_cn": prob.get("titleCn", ""),
                "title_slug": slug,
                "difficulty": prob.get("difficulty", ""),
                "topic_tags": [t.get("nameTranslated") or t.get("name") for t in (prob.get("topicTags") or [])],
                "url": f"{BASE_URL}/problems/{slug}/",
                "content": "",
                "tutorial": None,
                "solutions": solutions,
                "source": "cn",
            })

        await browser.close()

    Path("output").mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)

    total_sols = sum(len(p["solutions"]) for p in problems)
    official = sum(
        sum(1 for s in p["solutions"] if s.get("is_official")) for p in problems
    )
    logger.info(f"Done. {len(problems)} problems, {total_sols} solutions ({official} official).")
    logger.info(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(scrape_all())
