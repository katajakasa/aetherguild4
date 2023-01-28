from django.urls import reverse

from aether.utils.cache import expire_page


def invalidate_cache(sender, instance, created, **kwargs):
    expire_page(reverse("gallery:index"))
