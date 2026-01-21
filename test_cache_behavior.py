#!/usr/bin/env python3
"""
Test caching implementation
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/users/"

def test_cache_performance():
    print("🚀 Testing Cache Performance")
    print("=" * 50)
    
    # Test 1: First call (should be cache MISS)
    print("📞 Making first API call (cache MISS expected)...")
    start = time.time()
    try:
        response1 = requests.get(BASE_URL)
        time1 = time.time() - start
        print(f"✅ First call: {time1:.4f}s - Status: {response1.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python manage.py runserver")
        return
    
    # Test 2: Second call (should be cache HIT)
    print("📞 Making second API call (cache HIT expected)...")
    start = time.time()
    response2 = requests.get(BASE_URL)
    time2 = time.time() - start
    print(f"✅ Second call: {time2:.4f}s - Status: {response2.status_code}")
    
    # Calculate speedup
    if time2 > 0:
        speedup = time1 / time2
        print(f"🚀 Speedup: {speedup:.2f}x faster!")
    
    print("\\n" + "=" * 50)

def test_cache_invalidation():
    print("🔄 Testing Cache Invalidation")
    print("=" * 50)
    
    # Get current user count
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        initial_count = len(response.json())
        print(f"📊 Initial user count: {initial_count}")
    
    # Create a new user
    new_user = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123",
        "user_type": "passenger",
        "first_name": "Test",
        "last_name": "User"
    }
    
    print("👤 Creating new user...")
    create_response = requests.post(BASE_URL, json=new_user)
    
    if create_response.status_code == 201:
        print("✅ User created successfully")
        
        # Check if cache was invalidated
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            new_count = len(response.json())
            print(f"📊 New user count: {new_count}")
            
            if new_count > initial_count:
                print("✅ Cache invalidation working - new user visible!")
            else:
                print("❌ Cache invalidation failed - new user not visible")
    else:
        print(f"❌ Failed to create user: {create_response.status_code}")
    
    print("\\n" + "=" * 50)

if __name__ == "__main__":
    print("🧪 Cache Testing Suite")
    print("Make sure your Django server is running: python manage.py runserver")
    print()
    
    test_cache_performance()
    test_cache_invalidation()