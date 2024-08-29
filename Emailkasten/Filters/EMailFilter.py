import django_filters
from ..Models.EMailModel import EMailModel

class EMailFilter(django_filters.FilterSet):
    class Meta:
        model = EMailModel
        fields = {
            'datetime': ['gte', 'lte'],
            'email_subject': ['icontains', 'exact'],
            'bodytext': ['icontains'],
            'datasize': ['gte', 'lte']
        }