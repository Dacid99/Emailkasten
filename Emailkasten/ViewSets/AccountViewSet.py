from rest_framework import viewsets
from AccountModel import AccountModel
from Serializers import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer