from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'

    def get_page_size(self, request):
        if request.query_params.get('all') == 'true':
            return None
        return super().get_page_size(request)
    
    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('all') == 'true':
            return list(queryset)
        return super().paginate_queryset(queryset, request, view)