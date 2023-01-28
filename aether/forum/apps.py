from django.apps import AppConfig
from django.db.models.signals import post_save


class ForumConfig(AppConfig):
    name = "aether.forum"

    def ready(self):
        from .models import ForumPost, ForumUser
        from .signals import postprocess_forumpost, postprocess_forumuser

        post_save.connect(postprocess_forumuser, sender=ForumUser)
        post_save.connect(postprocess_forumpost, sender=ForumPost)
