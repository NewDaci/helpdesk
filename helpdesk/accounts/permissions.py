from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role == 'ADMIN'


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role == 'AGENT'


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.role == 'USER'
