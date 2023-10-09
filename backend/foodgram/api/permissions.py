from rest_framework import permissions


class IsAuthorOrSU(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff
