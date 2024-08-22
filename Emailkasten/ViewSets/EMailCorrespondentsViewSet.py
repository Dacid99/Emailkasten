from rest_framework import viewsets
from ..Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ..Serializers import EMailCorrespondentsSerializer

class EMailCorrespondentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EMailCorrespondentsModel.objects.all()
    serializer_class = EMailCorrespondentsSerializer