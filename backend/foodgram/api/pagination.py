from django.core import paginator
from rest_framework.pagination import PageNumberPagination

PAGE_SIZE = 6


class CustomPagination(PageNumberPagination):
    django_paginator_class = paginator.Paginator
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE