from rest_framework.permissions import BasePermission

class TicketAccessPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        role = request.user.profile.role

        if role == 'ADMIN':
            return True

        if role == 'AGENT':
            return obj.assigned_to == request.user

        if role == 'USER':
            return obj.created_by == request.user

        return False
