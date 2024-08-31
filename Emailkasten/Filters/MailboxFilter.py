import django_filters
from ..Models.MailboxModel import MailboxModel

class MailboxFilter(django_filters.FilterSet):

    mail_address__icontains = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='icontains')
    mail_address__contains = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='contains')
    mail_address__exact = django_filters.CharFilter(field_name='account__mail_address', lookup_expr='exact')
    mail_host__icontains = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='icontains')
    mail_host__contains = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='contains')
    mail_host__exact = django_filters.CharFilter(field_name='account__mail_host', lookup_expr='exact')
    protocol__exact = django_filters.CharFilter(field_name='account__protocol', lookup_expr='exact')
    is_healthy__exact = django_filters.BooleanFilter(field_name='account__is_healthy', lookup_expr='exact')
    
    class Meta:
        model = MailboxModel
        fields = {
            'name': ['icontains', 'contains', 'exact'],
            'cycle_interval': ['exact', 'lte', 'gte'],
            'fetching_criterion': ['exact'],
            'save_toEML': ['exact'],
            'save_attachments': ['exact'],
            'is_fetched': ['exact'],
            'created': ['lte', 'gte'],
            'updated': ['lte', 'gte']
        }