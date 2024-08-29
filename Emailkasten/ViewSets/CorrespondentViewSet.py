from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers import CorrespondentSerializer
from ..Filters.CorrespondentFilter import CorrespondentFilter

class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CorrespondentFilter