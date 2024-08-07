from rest_framework.pagination import PageNumberPagination, \
    LimitOffsetPagination, CursorPagination


class LargeResultPagination(PageNumberPagination):
    page_size = 200
    page_size_query_param = 'page_size'
    max_page_size = 300


class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100


class MyCursorPagination(CursorPagination):
    page_size = 10
    cursor_query_param = 'cursor'
    ordering = '-created'  # Adjust based on your model's fields
    page_size_query_param = 'page_size'
    max_page_size = 100

