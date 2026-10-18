"""
Debug script to see what the GraphQL API is actually returning
"""
import requests
from config import LEETCODE_SESSION, CSRF_TOKEN, HEADERS

print("Testing GraphQL API response...")
print("=" * 60)

session = requests.Session()

# Set up headers for GraphQL
graphql_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://leetcode.com",
    "Referer": "https://leetcode.com/problemset/all/",
}

# Add cookies
if LEETCODE_SESSION:
    session.cookies.set('LEETCODE_SESSION', LEETCODE_SESSION, domain='.leetcode.com')
    print(f"✓ Using LEETCODE_SESSION (length: {len(LEETCODE_SESSION)})")
if CSRF_TOKEN:
    session.cookies.set('csrftoken', CSRF_TOKEN, domain='.leetcode.com')
    graphql_headers['x-csrftoken'] = CSRF_TOKEN
    print(f"✓ Using CSRF_TOKEN (length: {len(CSRF_TOKEN)})")

session.headers.update(graphql_headers)

# Test query
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
    }
  }
}
"""

variables = {
    "categorySlug": "",
    "skip": 0,
    "limit": 5,
    "filters": {
        "tags": ["recursion"]
    }
}

payload = {
    "query": query,
    "variables": variables
}

print("\nSending request to https://leetcode.com/graphql")
print("-" * 60)

try:
    response = session.post(
        "https://leetcode.com/graphql",
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
    print(f"Response Length: {len(response.text)} bytes")
    print("\nFirst 500 characters of response:")
    print("-" * 60)
    print(response.text[:500])
    print("-" * 60)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("\n✓ Valid JSON response!")
            if 'errors' in data:
                print(f"❌ GraphQL Errors: {data['errors']}")
            elif 'data' in data:
                questions = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
                print(f"✓ Success! Found {len(questions)} problems")
                if questions:
                    print(f"First problem: {questions[0]}")
        except ValueError as e:
            print(f"\n❌ Cannot parse as JSON: {e}")
            print("\nThis means the API returned HTML or other non-JSON content")
            print("Likely causes:")
            print("  - Session cookie is invalid or expired")
            print("  - Being redirected to login page")
            print("  - CSRF token issues")
    else:
        print(f"\n❌ HTTP Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")

print("\n" + "=" * 60)
