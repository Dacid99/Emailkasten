from rest_framework import viewsets
from ..Models.EMailModel import EMailModel
from ..Serializers import EMailSerializer

class EMailViewSet(viewsets.ModelViewSet):
    queryset = EMailModel.objects.all()
    serializer_class = EMailSerializer