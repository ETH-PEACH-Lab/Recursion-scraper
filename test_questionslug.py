import requests

query = """
query questionTopicsList($questionSlug: String!, $orderBy: TopicSortingOption, $skip: Int, $first: Int, $tags: [String!]) {
  questionTopicsList(
    questionSlug: $questionSlug
    orderBy: $orderBy
    skip: $skip
    first: $first
    tags: $tags
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

response = requests.post(
    'https://leetcode.com/graphql',
    json={
        'query': query,
        'variables': {
            'questionSlug': 'two-sum',
            'orderBy': 'hot',
            'skip': 0,
            'first': 5,
            'tags': []
        }
    },
    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
)

print('Status:', response.status_code)
data = response.json()
if 'errors' in data:
    print('Error:', data['errors'][0]['message'])
else:
    total = data.get('data', {}).get('questionTopicsList', {}).get('totalNum', 0)
    edges = data.get('data', {}).get('questionTopicsList', {}).get('edges', [])
    print(f'Success! Total: {total}, Retrieved: {len(edges)}')
    if edges:
        for e in edges[:3]:
            print(f'  - {e["node"]["title"][:60]}')
