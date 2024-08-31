from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers import AttachmentSerializer
from ..Filters.AttachmentsFilter import AttachmentFilter
import os

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AttachmentFilter

    ALLOWED_SORT_FIELDS = ['file_name', 'datasize']

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort', None)
        if sort_by:
            sort_fields = sort_by.split(',')
            for field in sort_fields:
                    if field.startswith('-'):
                        field_name = field[1:]  # Remove the leading '-'
                        if field_name in self.ALLOWED_SORT_FIELDS:
                            queryset = queryset.order_by(field)  # Descending order
                        else:
                            raise ValidationError(f"Invalid sort field: {field_name}")
                    else:
                        if field in self.ALLOWED_SORT_FIELDS:
                            queryset = queryset.order_by(field)  # Ascending order
                        else:
                            raise ValidationError(f"Invalid sort field: {field}")

        return queryset

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        attachment = self.get_object()
        fileName = attachment.file_name
        filePath = attachment.file_path

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response