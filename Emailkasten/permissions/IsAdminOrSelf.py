from rest_framework.permissions import IsAdminUser

class IsAdminOrSelf(IsAdminUser):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view, obj) or request.user == obj