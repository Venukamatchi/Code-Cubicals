# api_debug.py - Script to explore the Omnidimension API structure
import json
import requests

OMNI_API_KEY = "JZPaq_oYAu30ggdL7dL1ApxaxtvzukFYrVY8xoyl9cg"
OMNI_AGENT_ID = 2342

def explore_api():
    """Explore the API to understand its structure"""
    
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Base endpoints to explore
    base_endpoints = [
        "https://backend.omnidim.io/api/v1/",
        "https://backend.omnidim.io/api/v1/agents",
        "https://backend.omnidim.io/api/v1/agents/2342",
        "https://backend.omnidim.io/api/v1/call",
        "https://backend.omnidim.io/api/v1/calls",
        "https://backend.omnidim.io/api/v1/voice",
        "https://backend.omnidim.io/api/",
    ]
    
    print("🔍 Exploring API structure...\n")
    
    for endpoint in base_endpoints:
        print(f"📡 Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS (200)")
                try:
                    data = response.json()
                    print(f"📊 Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"📋 Keys: {list(data.keys())}")
                        for key, value in data.items():
                            if isinstance(value, list) and value:
                                print(f"   {key}: list with {len(value)} items")
                                if value:
                                    print(f"      First item type: {type(value[0])}")
                                    if isinstance(value[0], dict):
                                        print(f"      First item keys: {list(value[0].keys())}")
                            else:
                                print(f"   {key}: {type(value)} = {str(value)[:100]}")
                    elif isinstance(data, list):
                        print(f"📋 List with {len(data)} items")
                        if data and isinstance(data[0], dict):
                            print(f"   First item keys: {list(data[0].keys())}")
                    
                    print(f"📄 Raw response: {json.dumps(data, indent=2)[:500]}...")
                except:
                    print(f"📄 Text response: {response.text[:200]}...")
                    
            elif response.status_code == 404:
                print(f"❌ NOT FOUND (404)")
            elif response.status_code == 401:
                print(f"🔐 UNAUTHORIZED (401)")
            elif response.status_code == 405:
                print(f"🔄 METHOD NOT ALLOWED (405)")
            else:
                print(f"⚠️  HTTP {response.status_code}")
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 60)

def test_agent_details():
    """Get detailed information about the specific agent"""
    
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🤖 Getting details for agent {OMNI_AGENT_ID}...\n")
    
    # Try different ways to get agent details
    agent_endpoints = [
        f"https://backend.omnidim.io/api/v1/agents/{OMNI_AGENT_ID}",
        f"https://backend.omnidim.io/api/v1/agent/{OMNI_AGENT_ID}",
        f"https://backend.omnidim.io/api/v1/bots/{OMNI_AGENT_ID}",
        f"https://backend.omnidim.io/api/v1/agents/{OMNI_AGENT_ID}/details",
        f"https://backend.omnidim.io/api/v1/agents/{OMNI_AGENT_ID}/capabilities",
    ]
    
    for endpoint in agent_endpoints:
        print(f"📡 Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS")
                try:
                    data = response.json()
                    print(f"📄 Agent details: {json.dumps(data, indent=2)}")
                except:
                    print(f"📄 Response: {response.text}")
            else:
                print(f"❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 40)

def test_call_endpoints():
    """Test potential call endpoints without actually making a call"""
    
    headers = {
        "Authorization": f"Bearer {OMNI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📞 Testing call-related endpoints...\n")
    
    # Test with OPTIONS method to see what's allowed
    call_endpoints = [
        "https://backend.omnidim.io/api/v1/call",
        "https://backend.omnidim.io/api/v1/calls", 
        "https://backend.omnidim.io/api/v1/voice",
        "https://backend.omnidim.io/api/v1/call/dispatch_call",
        "https://backend.omnidim.io/api/v1/agent/dispatch_voice",
    ]
    
    for endpoint in call_endpoints:
        print(f"📡 Testing: {endpoint}")
        
        # Try OPTIONS first
        try:
            response = requests.options(endpoint, headers=headers, timeout=10)
            if response.status_code in [200, 204]:
                allowed_methods = response.headers.get('Allow', 'Not specified')
                print(f"✅ OPTIONS: Allowed methods: {allowed_methods}")
        except:
            pass
        
        # Try GET
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ GET: Success")
                try:
                    data = response.json()
                    print(f"📄 Response: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"📄 Response: {response.text[:200]}...")
            elif response.status_code == 405:
                print(f"🔄 GET: Method not allowed (might accept POST)")
            else:
                print(f"❌ GET: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ GET ERROR: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    print("🔍 Omnidimension API Debug Tool")
    print("=" * 60)
    
    explore_api()
    test_agent_details()
    test_call_endpoints()
    
    print("\n✅ API exploration complete!")
    print("Check the output above to understand the correct API structure.")
