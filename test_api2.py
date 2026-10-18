"""
Test script to find the correct way to get community solutions
"""
import requests
import json

test_slug = "add-two-numbers"

print("=" * 60)
print("Finding correct API for community solutions...")
print("=" * 60)

# Method 1: Try topicDiscuss
print("\n[Method 1] Testing topicDiscuss...")
query1 = """
query questionTopicsList($questionSlug: String!, $skip: Int, $first: Int, $orderBy: TopicSortingOption) {
  questionTopicsList(questionSlug: $questionSlug, skip: $skip, first: $first, orderBy: $orderBy) {
    totalNum
    edges {
      node {
        id
        title
        post {
          id
          voteCount
          content
          creationDate
          author {
            username
          }
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
            "questionSlug": test_slug,
            "first": 10,
            "skip": 0,
            "orderBy": "hot"
        }
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

print(f"Status: {response1.status_code}")
if response1.status_code == 200:
    data = response1.json()
    if 'errors' in data:
        print(f"Errors: {data['errors'][0]['message']}")
    else:
        topics = data.get('data', {}).get('questionTopicsList', {})
        print(f"✓ Success! Total: {topics.get('totalNum', 0)}")
        edges = topics.get('edges', [])
        if edges:
            print(f"  Retrieved {len(edges)} posts")
            print(f"  First: {edges[0]['node']['title'][:50]}")
else:
    print(f"✗ Failed: {response1.text[:200]}")

# Method 2: Try without questionSolutions wrapper
print("\n[Method 2] Testing direct solutions query...")
query2 = """
query solutions($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    topicTags {
      name
    }
  }
}
"""

response2 = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query2,
        "variables": {"titleSlug": test_slug}
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

print(f"Status: {response2.status_code}")
if response2.status_code == 200:
    data = response2.json()
    if 'errors' in data:
        print(f"Errors: {data['errors'][0]['message']}")
    else:
        print(f"✓ Question data accessible")

# Method 3: Try the discuss/solutions endpoint structure
print("\n[Method 3] Testing discuss query structure...")
query3 = """
query DiscussSolutionTopics($orderBy: TopicSortingOption, $query: String, $skip: Int, $first: Int, $tags: [String!]) {
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
          content
        }
      }
    }
  }
}
"""

response3 = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query3,
        "variables": {
            "orderBy": "hot",
            "query": test_slug,
            "first": 5,
            "skip": 0,
            "tags": ["solution"]
        },
        "operationName": "DiscussSolutionTopics"
    },
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
)

print(f"Status: {response3.status_code}")
if response3.status_code == 200:
    data = response3.json()
    if 'errors' in data:
        print(f"Errors: {data['errors'][0]['message']}")
    else:
        print(f"✓ Success!")
        
print("\n" + "=" * 60)
print("Recommendation:")
print("=" * 60)
print("Use questionTopicsList with questionSlug parameter")
print("This retrieves discuss posts which include solutions")
