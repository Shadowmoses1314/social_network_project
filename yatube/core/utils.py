from django.core.paginator import Paginator

TEN_RECORDS = 10


def paginate_page(request, posts, post_per_page=TEN_RECORDS):
    paginator = Paginator(posts, post_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
