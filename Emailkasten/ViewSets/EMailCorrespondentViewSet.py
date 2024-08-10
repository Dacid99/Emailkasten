from rest_framework import viewsets
from EMailCorrespondentsModel import EMailCorrespondentsModel
from Serializers import EMailCorrespondentsSerializer

class EMailCorrespondentsViewSet(viewsets.ModelViewSet):
    queryset = EMailCorrespondentsModel.objects.all()
    serializer_class = EMailCorrespondentsSerializer