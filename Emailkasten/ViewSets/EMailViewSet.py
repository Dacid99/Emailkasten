from rest_framework import viewsets
from EMailModel import EMailModel
from Serializers import EMailSerializer

class EMailViewSet(viewsets.ModelViewSet):
    queryset = EMailModel.objects.all()
    serializer_class = EMailSerializer