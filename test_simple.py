import requests

# Try without tags parameter
query1 = """
query questionTopicsList($questionSlug: String!) {
  questionTopicsList(questionSlug: $questionSlug) {
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

print("Test 1: Basic query without optional params")
response1 = requests.post(
    'https://leetcode.com/graphql',
    json={
        'query': query1,
        'variables': {
            'questionSlug': 'two-sum'
        }
    },
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)

print('Status:', response1.status_code)
data1 = response1.json()
if 'errors' in data1:
    print('Error:', data1['errors'][0]['message'])
else:
    total = data1.get('data', {}).get('questionTopicsList', {}).get('totalNum', 0)
    print(f'✓ Success! Total discussions: {total}')

print("\n" + "="*60 + "\n")

# Try getting all discuss posts (not filtered by question)
query2 = """
query allTopics($skip: Int, $first: Int) {
  allTopics: topicTag(slug: "recursion") {
    name
    slug
  }
}
"""

print("Test 2: Try topicTag query")
response2 = requests.post(
    'https://leetcode.com/graphql',
    json={
        'query': query2,
        'variables': {}
    },
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)

print('Status:', response2.status_code)
data2 = response2.json()
if 'errors' in data2:
    print('Error:', data2['errors'][0]['message'])
else:
    print('✓ Success!')
    print(data2)
