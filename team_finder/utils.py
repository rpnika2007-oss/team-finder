from django.core.paginator import Paginator

DEFAULT_PAGE_SIZE = 12


def get_page(queryset, page_number, per_page=DEFAULT_PAGE_SIZE):
    """Возвращает объект страницы с разбивкой на страницы для набора запросов."""
    return Paginator(queryset, per_page).get_page(page_number)
