from rest_framework import viewsets
from CorrespondentModel import CorrespondentModel
from Serializers import CorrespondentSerializer

class CorrespondentViewSet(viewsets.ModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer