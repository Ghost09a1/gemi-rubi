from django.http import JsonResponse
from django.core.cache import cache


def test_cache(request):
    """Test view to verify cache connection."""
    try:
        # Try to set a value in the cache
        cache.set("test_key", "Cache is working!", 30)

        # Try to get the value back
        cached_value = cache.get("test_key")

        return JsonResponse(
            {
                "status": "success",
                "message": "Cache connection successful",
                "cached_value": cached_value,
            }
        )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "message": f"Cache error: {str(e)}"}, status=500
        )
