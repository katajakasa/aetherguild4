from django.core.management.base import BaseCommand
from aether.forum.models import ForumPost, ForumUser
from aether.main_site.models import NewsItem
from aether.forum import tasks


class Command(BaseCommand):
    def handle(self, *args, **options):
        for instance in NewsItem.objects.all():
            tasks.postprocess.apply_async(('newsitem', instance.id), retry=False)

        for instance in ForumUser.objects.all():
            tasks.postprocess.apply_async(('forumuser', instance.id), retry=False)

        for instance in ForumPost.objects.all():
            tasks.postprocess.apply_async(('forumpost', instance.id), retry=False)
