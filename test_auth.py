"""
Test if your LeetCode session is valid
"""
import requests
from config import LEETCODE_SESSION, CSRF_TOKEN, HEADERS

print("Testing LeetCode Authentication...")
print("=" * 60)

if not LEETCODE_SESSION:
    print("❌ ERROR: LEETCODE_SESSION not found in .env file")
    print("\nPlease:")
    print("1. Copy .env.example to .env")
    print("2. Add your LEETCODE_SESSION cookie value")
    print("3. See 获取Cookie指南.md for detailed instructions")
    exit(1)

print(f"✓ LEETCODE_SESSION found (length: {len(LEETCODE_SESSION)})")
if CSRF_TOKEN:
    print(f"✓ CSRF_TOKEN found (length: {len(CSRF_TOKEN)})")
else:
    print("⚠ CSRF_TOKEN not found (may be optional)")

print("\nTesting access to LeetCode...")
print("-" * 60)

session = requests.Session()
session.headers.update(HEADERS)
session.cookies.set('LEETCODE_SESSION', LEETCODE_SESSION, domain='.leetcode.com')
if CSRF_TOKEN:
    session.cookies.set('csrftoken', CSRF_TOKEN, domain='.leetcode.com')

# Test 1: Access main page
print("\n[Test 1] Accessing LeetCode homepage...")
try:
    response = session.get('https://leetcode.com/', timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Can access LeetCode")
    else:
        print(f"⚠ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Access a problem page
print("\n[Test 2] Accessing a problem page...")
try:
    response = session.get('https://leetcode.com/problems/two-sum/', timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Can access problem pages")
        # Check if logged in
        if 'Sign in' not in response.text and 'premium' in response.text.lower():
            print("✓ Session appears to be valid (logged in)")
        else:
            print("⚠ May not be logged in properly")
    else:
        print(f"⚠ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Access solutions page
print("\n[Test 3] Accessing solutions page...")
try:
    # First visit the problem
    session.get('https://leetcode.com/problems/two-sum/', timeout=10)
    
    # Then visit solutions
    response = session.get('https://leetcode.com/problems/two-sum/solutions/', timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Can access solutions pages!")
        # Check for solution content
        if 'solution' in response.text.lower() or 'discuss' in response.text.lower():
            print("✓ Solutions content found")
        else:
            print("⚠ Page loaded but content structure may be different")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Session cookie may be invalid or expired")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged into LeetCode in your browser")
        print("2. Get a fresh LEETCODE_SESSION cookie")
        print("3. Copy the ENTIRE cookie value (it's very long)")
        print("4. Make sure there are no extra spaces in .env file")
    else:
        print(f"⚠ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Test GraphQL API
print("\n[Test 4] Testing GraphQL API...")
try:
    query = """
    query {
      user {
        username
        profile {
          realName
        }
      }
    }
    """
    
    response = session.post(
        'https://leetcode.com/graphql',
        json={'query': query},
        timeout=10
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'errors' not in data and data.get('data', {}).get('user'):
            user = data['data']['user']
            print(f"✓ Logged in as: {user.get('username', 'Unknown')}")
        else:
            print("⚠ API accessible but not authenticated")
    else:
        print(f"⚠ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing complete!")
print("\nIf you see 403 errors, please:")
print("1. Log into LeetCode in your browser")
print("2. Get a fresh LEETCODE_SESSION cookie (see 获取Cookie指南.md)")
print("3. Update your .env file")
print("=" * 60)
