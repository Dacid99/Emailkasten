from rest_framework import viewsets
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers import CorrespondentSerializer

class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer