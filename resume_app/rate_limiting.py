from django.core.cache import cache
from django.http import HttpResponse
from functools import wraps
import time

def rate_limit(key_prefix, limit=5, period=3600):
    """
    Rate limiting decorator that limits requests by IP
    key_prefix: prefix for the cache key
    limit: maximum number of requests allowed in the period
    period: time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Get client IP - consider using a middleware for more reliable IP detection
            ip = request.META.get('REMOTE_ADDR', '')
            
            # Create a unique key for this IP and endpoint
            cache_key = f"{key_prefix}_{ip}"
            
            # Get current count and timestamp
            cache_data = cache.get(cache_key) or {'count': 0, 'timestamp': time.time()}
            
            # Reset counter if period has passed
            if time.time() - cache_data['timestamp'] > period:
                cache_data = {'count': 0, 'timestamp': time.time()}
                
            # Increment counter
            cache_data['count'] += 1
            
            # Update cache
            cache.set(cache_key, cache_data, period)
            
            # Check if limit exceeded
            if cache_data['count'] > limit:
                return HttpResponse(
                    "Too many requests. Please try again later.", 
                    status=429
                )
                
            # If not exceeded, proceed with the view
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator