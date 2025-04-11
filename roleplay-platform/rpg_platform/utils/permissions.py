from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners or admins to access an object.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if user is admin
        if request.user.is_staff:
            return True

        # Allow access if user is the owner
        return obj.user == request.user


class IsPublicOrOwner(permissions.BasePermission):
    """
    Custom permission to allow access to public objects or to owners.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if object is public
        if hasattr(obj, "public") and obj.public:
            return True

        # Allow access if user is the owner
        return obj.user == request.user


class IsFriendsOrOwner(permissions.BasePermission):
    """
    Custom permission to allow access to friends or owners.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if user is the owner
        if obj.user == request.user:
            return True

        # Allow access if users are friends
        if hasattr(obj.user, "is_friend_with"):
            return obj.user.is_friend_with(request.user)

        return False
