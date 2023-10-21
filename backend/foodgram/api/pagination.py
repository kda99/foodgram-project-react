from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 6

    def paginate_queryset(self, queryset, request, view=None):
        if ('limit' in request.query_params and 'is_in_shopping_cart'
                in request.query_params):
            limit = request.query_params.get('limit')
            is_in_shopping_cart = request.query_params.get(
                'is_in_shopping_cart')
            if limit in ('999', '6') and is_in_shopping_cart == '1':
                self.page_size = '999'
        return super().paginate_queryset(queryset, request, view)
