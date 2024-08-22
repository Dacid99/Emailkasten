from ..Serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import generics

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer