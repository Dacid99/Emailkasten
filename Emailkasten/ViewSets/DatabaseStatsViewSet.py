from rest_framework import viewsets
from rest_framework.response import Response
from ..Models.EMailModel import EMailModel
from ..Models.CorrespondentModel import CorrespondentModel
from ..Models.AttachmentModel import AttachmentModel
from ..Models.AccountModel import AccountModel

class DatabaseStatsViewSet(viewsets.ViewSet):
    def list(self, request):
        email_count = EMailModel.objects.count()
        correspondent_count = CorrespondentModel.objects.count()
        attachment_count = AttachmentModel.objects.count()
        account_count = AccountModel.objects.count()

        data = {
            'email_count': email_count,
            'correspondent_count': correspondent_count,
            'attachment_count': attachment_count,
            'account_count': account_count,
        }
        return Response(data)