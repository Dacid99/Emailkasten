from rest_framework.permissions import IsAuthenticated

class IsAdminOrSelf(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff) or request.user == obj
