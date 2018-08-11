from django.apps import AppConfig
from django.db.models.signals import post_save


class ForumConfig(AppConfig):
    name = 'aether.forum'

    def ready(self):
        from .signals import postprocess_forumuser, postprocess_forumpost
        from .models import ForumUser, ForumPost
        post_save.connect(postprocess_forumuser, sender=ForumUser)
        post_save.connect(postprocess_forumpost, sender=ForumPost)
