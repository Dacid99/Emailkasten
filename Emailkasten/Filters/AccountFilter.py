import django_filters
from ..Models.AccountModel import AccountModel

class AccountFilter(django_filters.FilterSet):

    class Meta:
        model = AccountModel
        fields = {
            'mail_address': ['icontains', 'contains', 'exact'],
            'mail_host': ['icontains', 'contains', 'exact'],
            'mail_host_port': ['exact', 'lte', 'gte'],
            'protocol': ['icontains', 'contains', 'exact'],
            'is_healthy': ['exact'],
            'created': ['lte', 'gte'],
            'updated': ['lte', 'gte']
        }