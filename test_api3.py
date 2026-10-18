"""
Test to understand the questionTopicsList query structure
"""
import requests
import json

test_slug = "two-sum"  # A very popular problem

print("Testing different query approaches...\n")

# Test 1: With question slug in query
print("=" * 60)
print("[Test 1] Using question slug in query parameter")
print("=" * 60)
query1 = """
query questionTopicsList($orderBy: TopicSortingOption, $query: String, $skip: Int, $first: Int, $tags: [String!]) {
  questionTopicsList(
    orderBy: $orderBy
    query: $query
    skip: $skip
    first: $first
    tags: $tags
  ) {
    totalNum
    edges {
      node {
        id
        title
        post {
          id
          voteCount
        }
      }
    }
  }
}
"""

response1 = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query1,
        "variables": {
            "orderBy": "hot",
            "query": test_slug,
            "skip": 0,
            "first": 10,
            "tags": ["solution"]
        }
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

if response1.status_code == 200:
    data = response1.json()
    if 'errors' not in data:
        total = data.get('data', {}).get('questionTopicsList', {}).get('totalNum', 0)
        edges = data.get('data', {}).get('questionTopicsList', {}).get('edges', [])
        print(f"Total: {total}, Retrieved: {len(edges)}")
        if edges:
            for i, edge in enumerate(edges[:3]):
                print(f"  {i+1}. {edge['node']['title'][:60]}")
    else:
        print(f"Error: {data['errors']}")

# Test 2: Using questionSlug parameter (if it exists)
print("\n" + "=" * 60)
print("[Test 2] Using questionSlug parameter")
print("=" * 60)
query2 = """
query questionTopicsList($questionSlug: String!, $orderBy: TopicSortingOption, $skip: Int, $first: Int) {
  questionTopicsList(
    questionSlug: $questionSlug
    orderBy: $orderBy
    skip: $skip
    first: $first
  ) {
    totalNum
    edges {
      node {
        id
        title
      }
    }
  }
}
"""

response2 = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query2,
        "variables": {
            "questionSlug": test_slug,
            "orderBy": "hot",
            "skip": 0,
            "first": 10
        }
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

if response2.status_code == 200:
    data = response2.json()
    if 'errors' not in data:
        total = data.get('data', {}).get('questionTopicsList', {}).get('totalNum', 0)
        edges = data.get('data', {}).get('questionTopicsList', {}).get('edges', [])
        print(f"✓ Total: {total}, Retrieved: {len(edges)}")
        if edges:
            for i, edge in enumerate(edges[:3]):
                print(f"  {i+1}. {edge['node']['title'][:60]}")
    else:
        print(f"✗ Error: {data['errors'][0]['message']}")
else:
    print(f"✗ HTTP Error: {response2.status_code}")

# Test 3: Get question ID first, then use it
print("\n" + "=" * 60)
print("[Test 3] Get question details first")
print("=" * 60)
query3 = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    questionFrontendId
    title
  }
}
"""

response3 = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query3,
        "variables": {"titleSlug": test_slug}
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

if response3.status_code == 200:
    data = response3.json()
    if 'errors' not in data:
        question = data.get('data', {}).get('question', {})
        print(f"Question ID: {question.get('questionFrontendId')}")
        print(f"Title: {question.get('title')}")
        print(f"Backend ID: {question.get('questionId')}")

print("\n" + "=" * 60)
print("Recommendation: Use questionSlug parameter")
print("=" * 60)
