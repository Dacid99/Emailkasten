from rest_framework import viewsets
from AttachmentModel import AttachmentModel
from Serializers import AttachmentSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer