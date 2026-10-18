"""
Test script to verify LeetCode API queries
"""
import requests
import json

# Test 1: Get problem list
print("=" * 60)
print("Test 1: Fetching problem list...")
print("=" * 60)

query1 = """
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

variables1 = {
    "categorySlug": "",
    "skip": 0,
    "limit": 5,
    "filters": {
        "tags": ["recursion"]
    }
}

response1 = requests.post(
    "https://leetcode.com/graphql",
    json={"query": query1, "variables": variables1},
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)

print(f"Status: {response1.status_code}")
if response1.status_code == 200:
    data = response1.json()
    if 'errors' in data:
        print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
    else:
        problems = data.get('data', {}).get('problemsetQuestionList', {}).get('questions', [])
        print(f"Success! Found {len(problems)} problems")
        if problems:
            print(f"First problem: {problems[0]['title']} ({problems[0]['titleSlug']})")
            test_slug = problems[0]['titleSlug']
else:
    print(f"Error: {response1.text[:500]}")
    test_slug = "add-two-numbers"

print()

# Test 2: Get solutions for a problem
print("=" * 60)
print(f"Test 2: Fetching solutions for '{test_slug}'...")
print("=" * 60)

# Try simpler query first
query2_simple = """
query questionSolutions($questionSlug: String!) {
  question(titleSlug: $questionSlug) {
    solution {
      id
      content
    }
  }
}
"""

response2_simple = requests.post(
    "https://leetcode.com/graphql",
    json={
        "query": query2_simple,
        "variables": {"questionSlug": test_slug}
    },
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)

print(f"Status (official solution): {response2_simple.status_code}")
if response2_simple.status_code == 200:
    data = response2_simple.json()
    if 'errors' in data:
        print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
    else:
        solution = data.get('data', {}).get('question', {}).get('solution')
        if solution:
            print(f"Success! Found official solution (ID: {solution.get('id')})")
        else:
            print("No official solution available")
else:
    print(f"Error: {response2_simple.text[:500]}")

print()

# Test 3: Try to get community solutions (discuss posts)
print("=" * 60)
print(f"Test 3: Trying community solutions API...")
print("=" * 60)

query3 = """
query discussSolutionTopics($questionSlug: String!, $first: Int!, $skip: Int!, $orderBy: TopicSortingOption) {
  questionSolutions(
    questionSlug: $questionSlug
    first: $first
    skip: $skip
    orderBy: $orderBy
  ) {
    hasDirectResults
    totalNum
    solutions {
      id
      title
      post {
        id
        voteCount
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
            "questionSlug": test_slug,
            "first": 10,
            "skip": 0,
            "orderBy": "HOT"
        },
        "operationName": "discussSolutionTopics"
    },
    headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)

print(f"Status: {response3.status_code}")
if response3.status_code == 200:
    data = response3.json()
    if 'errors' in data:
        print(f"GraphQL Errors: {json.dumps(data['errors'], indent=2)}")
    else:
        solutions = data.get('data', {}).get('questionSolutions', {})
        print(f"Success! Total solutions: {solutions.get('totalNum', 0)}")
        sol_list = solutions.get('solutions', [])
        if sol_list:
            print(f"Retrieved {len(sol_list)} solutions")
            print(f"First solution: {sol_list[0].get('title', 'No title')}")
        else:
            print("No solutions in response")
else:
    print(f"Error: {response3.text[:500]}")

print()
print("=" * 60)
print("Testing complete!")
print("=" * 60)
