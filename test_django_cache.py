#!/usr/bin/env python3
"""
Test Django cache configuration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('c:\\Users\\Pc\\caching-gla-safeboda')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeboda.settings')
django.setup()

from django.core.cache import cache

def test_cache():
    print("Testing Django cache configuration...")
    
    try:
        # Test basic cache operations
        cache.set('test_key', 'Hello Cache!', 30)
        value = cache.get('test_key')
        
        if value == 'Hello Cache!':
            print("✅ Cache is working correctly!")
            print(f"✅ Retrieved value: {value}")
            
            # Clean up
            cache.delete('test_key')
            print("✅ Cache test completed successfully!")
            return True
        else:
            print("❌ Cache test failed - value mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False

if __name__ == "__main__":
    test_cache()