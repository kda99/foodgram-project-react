from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6
PAGE_SIZE_QUERY_PARAM = 'limit'

class CustomPagination(PageNumberPagination):
    django_paginator_class = Paginator
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    page_size = PAGE_SIZE