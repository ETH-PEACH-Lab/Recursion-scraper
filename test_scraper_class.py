"""
Test the actual scraper class to see what's failing
"""
from scraper import LeetCodeScraper

print("Testing LeetCodeScraper class...")
print("=" * 60)

scraper = LeetCodeScraper()

print("\nSession headers:")
for key, value in scraper.session.headers.items():
    print(f"  {key}: {value}")

print("\nSession cookies:")
for cookie in scraper.session.cookies:
    print(f"  {cookie.name}: {cookie.value[:20]}...")

print("\n" + "=" * 60)
print("Attempting to fetch recursion problems...")
print("=" * 60)

problems = scraper.get_recursion_problems()

if problems:
    print(f"\n✓ Success! Found {len(problems)} problems")
    print(f"First problem: {problems[0]['title']}")
else:
    print("\n❌ Failed to fetch problems")

print("\n" + "=" * 60)
