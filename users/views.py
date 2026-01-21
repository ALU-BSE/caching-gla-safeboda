from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view

from users.models import User
from users.serializers import UserSerializer


# Create your views here.

def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


@api_view(['GET'])
def cache_stats(request):
    """Get cache statistics"""
    try:
        # Get Redis client
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Get all keys
        all_keys = redis_conn.keys('*')
        
        # Filter our app's keys
        user_keys = [key.decode('utf-8') for key in all_keys if b'user' in key]
        
        stats = {
            'total_keys': len(all_keys),
            'user_cache_keys': user_keys,
            'user_cache_count': len(user_keys),
            'cache_backend': settings.CACHES['default']['BACKEND'],
            'cache_location': settings.CACHES['default']['LOCATION'],
            'default_timeout': settings.CACHE_TTL,
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Could not retrieve cache stats'
        }, status=500)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def list(self, request, *args, **kwargs):
        # Step 1: Create cache key
        cache_key = get_cache_key('user_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            print(f"✅ Cache HIT for {cache_key}")
            return Response(cached_data)
        
        print(f"❌ Cache MISS for {cache_key}")
        
        # Step 3: Get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        print(f"💾 Cached data for {cache_key}")
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        # Get user ID from URL
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user', user_id)
        
        # Try cache first
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            print(f"✅ Cache HIT for {cache_key}")
            return Response(cached_data)
        
        print(f"❌ Cache MISS for {cache_key}")
        
        # Get from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the result
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        print(f"💾 Cached data for {cache_key}")
        
        return response
    
    def perform_create(self, serializer):
        # Clear user list cache when new user is created
        cache.delete('user_list')
        print("🗑️ Cleared user_list cache after create")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        # Clear both list and individual user cache
        user_id = serializer.instance.id
        cache.delete('user_list')
        cache.delete(f'user_{user_id}')
        print(f"🗑️ Cleared caches after update for user {user_id}")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        # Clear caches when user is deleted
        user_id = instance.id
        cache.delete('user_list')
        cache.delete(f'user_{user_id}')
        print(f"🗑️ Cleared caches after delete for user {user_id}")
        super().perform_destroy(instance)