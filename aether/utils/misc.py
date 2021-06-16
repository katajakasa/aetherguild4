from datetime import datetime, timezone
from django.db.models import Subquery, IntegerField


def get_page(request):
    try:
        return max(int(request.GET.get('page', 1)), 1)
    except ValueError:
        return 1


class SQCount(Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = IntegerField()


def utc_now():
    return datetime.now(timezone.utc)
