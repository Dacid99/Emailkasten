from rest_framework import viewsets
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers import AttachmentSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer