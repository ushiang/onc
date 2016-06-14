from packages.bin.dictionary import Config
from packages.bin.lib import get_query_string

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate(page, obj_list, request, q):
    """
    Builds a Pagination object for tables
    :param page: page object
    :param obj_list: query_set object
    :param request: request object
    :param q: string > query string used to represent page index
    :return: returns a tuple of a pagination object and query_set object
    """
    page.paginator = Paginator(obj_list, Config.PAGE_LIMIT)
    index = request.GET.get('page')

    try:
        obj = page.paginator.page(index)

    except PageNotAnInteger:
        obj = page.paginator.page(1)

    except EmptyPage:
        obj = page.paginator.page(page.paginator.num_pages)

    page.paginator_str = "Showing records %d to %d of %d entries" % (obj.start_index(), obj.end_index(), len(obj_list))
    page.paginator_index = obj.number
    page.query_string = get_query_string(request)

    return page, obj