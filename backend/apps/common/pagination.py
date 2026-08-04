"""Project-wide pagination policy."""

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Page-number pagination; client may tune size up to a hard cap.

    Example: GET /api/v1/tasks/?page=2&page_size=50
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
