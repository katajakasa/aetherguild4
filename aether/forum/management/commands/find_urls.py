import re

from django.core.management.base import BaseCommand
from aether.forum.models import ForumPost, ForumUser
from aether.main_site.models import NewsItem

match_url = re.compile(r'\[img\](\s*)(.+?)(\s*)\[\/img\]')


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-u',
            '--url',
            dest='url',
            type=str,
            help='Address fragment to look for')

    def handle(self, *args, **options):
        for item in NewsItem.objects.all():
            entries = match_url.findall(item.message.raw)
            for entry in entries:
                if options['url'] in entry[1]:
                    print(f"News {item.id}: {entry[1]}")

        for item in ForumUser.objects.all():
            entries = match_url.findall(item.signature.raw)
            for entry in entries:
                if options['url'] in entry[1]:
                    print(f"User {item.user.username}: {entry[1]}")

        for item in ForumPost.objects.iterator():
            entries = match_url.findall(item.message.raw)
            for entry in entries:
                if options['url'] in entry[1]:
                    print(f"Thread {item.thread_id} post {item.id}: {entry[1]}")
