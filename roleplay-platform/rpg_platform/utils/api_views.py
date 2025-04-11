from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from functools import wraps


class BaseAPIView(APIView):
    """
    Base API view with common functionality
    """

    def get_cache_key(self, request, *args, **kwargs):
        """
        Generate a cache key based on the request and view parameters
        """
        return f"{request.path}:{request.user.id if request.user.is_authenticated else 'anon'}"

    def get_cached_response(self, request, *args, **kwargs):
        """
        Get cached response if available
        """
        cache_key = self.get_cache_key(request, *args, **kwargs)
        return cache.get(cache_key)

    def set_cached_response(self, request, response, *args, **kwargs):
        """
        Cache the response
        """
        cache_key = self.get_cache_key(request, *args, **kwargs)
        cache.set(cache_key, response, timeout=300)  # 5 minutes cache

    def success_response(self, data, status=status.HTTP_200_OK):
        """
        Return a standardized success response
        """
        return Response({"success": True, "data": data}, status=status)

    def error_response(self, message, status=status.HTTP_400_BAD_REQUEST, details=None):
        """
        Return a standardized error response
        """
        return Response(
            {"success": False, "error": {"message": message, "details": details}},
            status=status,
        )

    def paginate_response(self, queryset, serializer_class, request):
        """
        Helper method for paginated responses
        """
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = serializer_class(queryset, many=True)
        return self.success_response(serializer.data)
