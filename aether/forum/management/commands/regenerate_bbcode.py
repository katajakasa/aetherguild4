from django.core.management.base import BaseCommand
from django.db import transaction
from precise_bbcode.bbcode import get_parser

from aether.forum.models import ForumPost, ForumUser
from aether.main_site.models import NewsItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        parser = get_parser()

        with transaction.atomic():
            count = 0
            for item in NewsItem.objects.select_for_update():
                item.message.rendered = parser.render(item.message.raw)
                item.save(update_fields=["_message_rendered"])
                count += 1
                if count % 10 == 0:
                    print("NewsItem:  {}".format(count))

        with transaction.atomic():
            count = 0
            for item in ForumUser.objects.select_for_update():
                item.signature.rendered = parser.render(item.signature.raw)
                item.save(update_fields=["_signature_rendered"])
                count += 1
                if count % 100 == 0:
                    print("ForumUser: {}".format(count))

        with transaction.atomic():
            count = 0
            for item in ForumPost.objects.select_for_update():
                item.message.rendered = parser.render(item.message.raw)
                item.save(update_fields=["_message_rendered"])
                count += 1
                if count % 1000 == 0:
                    print("ForumPost: {}".format(count))
