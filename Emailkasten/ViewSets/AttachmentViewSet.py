from rest_framework import viewsets
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers import AttachmentSerializer
import os

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        attachment = self.get_object()
        fileName = attachment.file_name
        filePath = attachment.file_path

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response