from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from aether.utils.misc import get_page

from .models import GalleryGroup


@never_cache
def gallery_index(request):
    paginator = Paginator(GalleryGroup.objects.order_by("-created_at").all(), 5)
    page = get_page(request)
    return render(
        request,
        "gallery/galleries.html",
        {
            "galleries": paginator.get_page(page),
        },
    )
