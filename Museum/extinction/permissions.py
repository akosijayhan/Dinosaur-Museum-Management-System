# accounts/permissions.py
from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
  """Custom permission:

  - Safe methods (GET, HEAD, OPTIONS) are allowed for anyone.
  - Write methods (PUT, PATCH, DELETE) are allowed ONLY for admins or the
  object creator (created_by).
  """

  def has_permission(self, request, view):
    if request.method in permissions.SAFE_METHODS:
      return True
    return bool(request.user and request.user.is_authenticated)

  def has_object_permission(self, request, view, obj):
    if request.method in permissions.SAFE_METHODS:
      return True

    # Staff/Admins have full write permissions
    if request.user.is_staff or request.user.is_superuser:
      return True

    # Creator/Owner has full write permissions
    if hasattr(obj, 'created_by') and obj.created_by == request.user:
      return True

    return False