from rest_framework import permissions

from users.models import User


# class IsAuthorOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return (request.method in permissions.SAFE_METHODS
#                 or request.user.is_authenticated)
#
#     def has_object_permission(self, request, view, obj):
#         if self.action == 'retrieve' and isinstance(obj, User):
#             return True
#         return (
#             request.method in permissions.SAFE_METHODS
#             or obj.author == request.user
#         )





# class UserPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if view.action == 'create':
#             return True
#         elif view.action == 'list':
#             # Логика для разрешения действия "list"
#             return True
#         elif view.action == 'retrieve':
#             # Логика для разрешения действия "retrieve"
#             return True
#         elif view.action == 'update':
#             # Логика для разрешения действия "update"
#             return True
#         elif view.action == 'partial_update':
#             # Логика для разрешения действия "partial_update"
#             return True
#         elif view.action == 'destroy':
#
#             return True
#
#     def has_object_permission(self, request, view, obj):
#         if view.action == 'retrieve':
#             # Логика для разрешения действия "retrieve"
#             return True
#         elif view.action == 'update':
#             # Логика для разрешения действия "update"
#             return True
#         elif view.action == 'partial_update':
#             # Логика для разрешения действия "partial_update"
#             return True
#         elif view.action == 'destroy':
#             # Логика для разрешения действия "destroy"
#             return True
#
#
# class IsAuthorOrSU(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return (request.user.is_authenticated or request.user.is_staff)
#
#     def has_object_permission(self, request, view, obj):
#         return obj.author == request.user or request.user.is_staff