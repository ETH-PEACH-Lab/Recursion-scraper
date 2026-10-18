"""
LeetCode Recursion Problems Scraper

This module scrapes LeetCode problems tagged with 'recursion',
including their tutorials and solutions.
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import json
from tqdm import tqdm

import config
from models import Problem, Solution
from utils import logger, rate_limit, save_to_json, save_to_csv, setup_output_dir


def _title_to_slug(title: str) -> str:
    """Convert a solution title to a URL slug matching LeetCode's format."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


class LeetCodeScraper:
    """Scraper for LeetCode recursion problems."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        
        # Add cookies if available
        if config.LEETCODE_SESSION:
            self.session.cookies.set('LEETCODE_SESSION', config.LEETCODE_SESSION, domain='.leetcode.com')
            logger.info("Using authenticated session (LEETCODE_SESSION cookie set)")
        else:
            logger.warning("No LEETCODE_SESSION found - some content may be inaccessible")
        
        if config.CSRF_TOKEN:
            self.session.cookies.set('csrftoken', config.CSRF_TOKEN, domain='.leetcode.com')
        
        logger.info("LeetCode scraper initialized")
    
    def get_recursion_problems(self) -> List[dict]:
        """
        Fetch list of problems tagged with 'recursion' using LeetCode's GraphQL API.
        """
        logger.info("Fetching recursion problems list...")
        
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
          problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
          ) {
            total: totalNum
            questions: data {
              questionId
              title
              titleSlug
              difficulty
              topicTags {
                name
                slug
              }
            }
          }
        }
        """
        
        variables = {
            "categorySlug": "",
            "skip": 0,
            "limit": 500,
            "filters": {
                "tags": ["recursion"]
            }
        }
        
        payload = {
            "query": query,
            "variables": variables
        }
        
        # Temporarily update session headers for GraphQL
        original_accept = self.session.headers.get('Accept')
        original_content_type = self.session.headers.get('Content-Type')
        
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://leetcode.com",
            "Referer": "https://leetcode.com/problemset/all/",
        })
        
        try:
            response = self.session.post(
                config.LEETCODE_API_URL,
                json=payload,
                timeout=config.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            questions = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
            
            logger.info(f"Found {len(questions)} recursion problems")
            return questions
            
        except Exception as e:
            logger.error(f"Error fetching problems list: {e}")
            return []
        finally:
            # Restore original headers
            if original_accept:
                self.session.headers['Accept'] = original_accept
            if original_content_type:
                self.session.headers['Content-Type'] = original_content_type
            else:
                self.session.headers.pop('Content-Type', None)
    
    def get_problem_details(self, title_slug: str) -> Optional[dict]:
        """
        Fetch detailed information for a specific problem.
        """
        query = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            title
            titleSlug
            content
            difficulty
            topicTags {
              name
              slug
            }
            hints
            solution {
              id
              content
            }
          }
        }
        """
        
        variables = {"titleSlug": title_slug}
        payload = {
            "query": query,
            "variables": variables
        }
        
        # Temporarily update headers for GraphQL
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
        try:
            response = self.session.post(
                config.LEETCODE_API_URL,
                json=payload,
                timeout=config.TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            question_data = data.get('data', {}).get('question', {})
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error fetching details for {title_slug}: {e}")
            return None
    
    def get_problem_solutions(self, title_slug: str) -> List[dict]:
        """
        Fetch community solutions via GraphQL API.
        Filter for solutions containing 'recursion' keyword and media (video/images).
        """
        logger.info(f"Fetching solutions for {title_slug}...")

        query = """
        query communitySolutions($filters: QuestionSolutionsFilterInput!) {
          questionSolutions(filters: $filters) {
            totalNum
            solutions {
              id
              title
              post {
                id
                voteCount
                creationDate
                author {
                  username
                }
                content
              }
            }
          }
        }
        """

        PAGE_SIZE = 50

        headers_patch = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": f"{config.LEETCODE_BASE_URL}/problems/{title_slug}/solutions/",
        }
        if config.CSRF_TOKEN:
            headers_patch["x-csrftoken"] = config.CSRF_TOKEN
        self.session.headers.update(headers_patch)

        def _fetch_page(skip: int) -> dict:
            payload = {
                "query": query,
                "variables": {
                    "filters": {
                        "questionSlug": title_slug,
                        "skip": skip,
                        "first": PAGE_SIZE,
                        "orderBy": "hot",
                        "topicTags": [config.TOPIC_TAG],
                    }
                },
                "operationName": "communitySolutions",
            }
            resp = self.session.post(config.LEETCODE_API_URL, json=payload, timeout=config.TIMEOUT)
            if resp.status_code == 403:
                raise PermissionError("403")
            resp.raise_for_status()
            return resp.json()

        def _parse(sol: dict) -> Optional[dict]:
            post = sol.get("post") or {}
            raw_content = post.get("content") or ""
            content = (
                raw_content
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace("\\'", "'")
                .replace('\\"', '"')
            )
            content = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), content)
            content = re.sub(r'\$\$([^$]*)\$\$', r'\1', content)
            has_video = self._contains_video(content)
            has_image = self._contains_image(content)
            if config.REQUIRE_MEDIA and not (has_video or has_image):
                return None
            return {
                "id": str(sol.get("id", "")),
                "title": sol.get("title", ""),
                "content": content,
                "has_video": has_video,
                "has_image": has_image,
                "author": post.get("author", {}).get("username", "Unknown"),
                "votes": post.get("voteCount", 0),
                "created_at": str(post.get("creationDate", "")),
                "is_paid": False,
                "url": f"{config.LEETCODE_BASE_URL}/problems/{title_slug}/solutions/{sol.get('id')}/{_title_to_slug(sol.get('title',''))}/",
            }

        try:
            # First page — tells us totalNum
            data = _fetch_page(0)
            if "errors" in data:
                logger.warning(f"GraphQL errors for {title_slug}: {data['errors']}")
                return []

            qs = data.get("data", {}).get("questionSolutions", {})
            total = qs.get("totalNum", 0)
            all_raw = list(qs.get("solutions", []))

            logger.info(f"{title_slug}: {total} tagged solutions, fetching all pages...")

            skip = PAGE_SIZE
            while skip < total:
                rate_limit(0.5)
                page_data = _fetch_page(skip)
                page_sols = (
                    page_data.get("data", {})
                    .get("questionSolutions", {})
                    .get("solutions", [])
                )
                if not page_sols:
                    break
                all_raw.extend(page_sols)
                skip += PAGE_SIZE

            filtered = [r for sol in all_raw if (r := _parse(sol)) is not None]
            logger.info(f"Found {len(filtered)} filtered solutions for {title_slug} (from {len(all_raw)} tagged)")
            return filtered

        except PermissionError:
            logger.warning(f"403 for {title_slug} - add LEETCODE_SESSION to .env")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {title_slug}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching solutions for {title_slug}: {e}")
            return []
    
    def _contains_video(self, content: str) -> bool:
        if not content:
            return False
        content_lower = content.lower()
        return any(x in content_lower for x in [
            'youtube.com', 'youtu.be', 'vimeo.com', 'loom.com',
            '<iframe', '.mp4', '.webm',
        ])

    _IMG_RE = re.compile(
        r'!\[[^\]]*\]\(https?://[^\)]+\)|<img[^>]+src=["\']https?://[^"\']+["\']',
        re.IGNORECASE,
    )

    def _contains_image(self, content: str) -> bool:
        if not content:
            return False
        return bool(self._IMG_RE.search(content))
    
    def scrape_all(self) -> List[Problem]:
        """
        Main method to scrape all recursion problems with their details.
        """
        logger.info("Starting scraping process...")
        setup_output_dir()
        
        # Get list of recursion problems
        problems_list = self.get_recursion_problems()
        
        if not problems_list:
            logger.warning("No problems found!")
            return []
        
        problems = []
        
        # Fetch details for each problem with progress bar
        for problem_data in tqdm(problems_list, desc="Scraping problems"):
            title_slug = problem_data['titleSlug']
            
            # Get detailed information
            details = self.get_problem_details(title_slug)
            rate_limit()
            
            if not details:
                continue
            
            # Create Problem object
            problem = Problem(
                title=details.get('title', ''),
                title_slug=details.get('titleSlug', ''),
                question_id=details.get('questionId', ''),
                difficulty=details.get('difficulty', ''),
                topic_tags=[tag['name'] for tag in details.get('topicTags', [])],
                url=f"{config.LEETCODE_BASE_URL}/problems/{title_slug}/",
                content=details.get('content', ''),
                tutorial=details.get('solution', {}).get('content') if details.get('solution') else None,
                solutions=[]
            )
            
            problems.append(problem)
            
            # Fetch community solutions with filters
            logger.info(f"Fetching filtered solutions for {title_slug}...")
            solutions = self.get_problem_solutions(title_slug)
            problem.solutions = solutions
            rate_limit()
        
        logger.info(f"Successfully scraped {len(problems)} problems")
        return problems
    
    def save_results(self, problems: List[Problem]):
        """Save scraped problems to file."""
        problems_dict = [p.to_dict() for p in problems]
        
        # Save as JSON
        save_to_json(problems_dict, 'recursion_problems.json')
        
        # Save simplified version as CSV
        simplified = [
            {
                'question_id': p.question_id,
                'title': p.title,
                'difficulty': p.difficulty,
                'url': p.url,
                'has_tutorial': p.tutorial is not None,
                'solutions_count': len(p.solutions) if p.solutions else 0,
                'solutions_with_media': sum(1 for s in (p.solutions or []) if s.get('has_video') or s.get('has_image'))
            }
            for p in problems
        ]
        save_to_csv(simplified, 'recursion_problems.csv')
        
        # Save all filtered solutions separately
        all_solutions = []
        for p in problems:
            if p.solutions:
                for sol in p.solutions:
                    solution_entry = {
                        'problem_id': p.question_id,
                        'problem_title': p.title,
                        'problem_url': p.url,
                        'solution_id': sol.get('id'),
                        'solution_title': sol.get('title'),
                        'author': sol.get('author'),
                        'votes': sol.get('votes'),
                        'has_video': sol.get('has_video'),
                        'has_image': sol.get('has_image'),
                        'is_paid': sol.get('is_paid'),
                        'created_at': sol.get('created_at'),
                        'content_preview': sol.get('content', '')[:200] + '...' if sol.get('content') else ''
                    }
                    all_solutions.append(solution_entry)
        
        if all_solutions:
            save_to_json(all_solutions, 'filtered_solutions.json')
            save_to_csv(all_solutions, 'filtered_solutions.csv')
            logger.info(f"Saved {len(all_solutions)} filtered solutions")


def main():
    """Main execution function."""
    scraper = LeetCodeScraper()
    
    # Scrape all recursion problems
    problems = scraper.scrape_all()
    
    # Save results
    if problems:
        scraper.save_results(problems)
        logger.info("✓ Scraping completed successfully!")
    else:
        logger.warning("No problems were scraped")


if __name__ == "__main__":
    main()
