from django.apps import AppConfig
from django.db.models.signals import post_save


class MainsiteConfig(AppConfig):
    name = "aether.main_site"

    def ready(self):
        from .models import NewsItem
        from .signals import postprocess_newsitem

        post_save.connect(postprocess_newsitem, sender=NewsItem)
