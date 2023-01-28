import re

from django.core.management.base import BaseCommand

from aether.forum.models import ForumPost, ForumUser
from aether.main_site.models import NewsItem

re_urlimg = re.compile(r"\[url=(.+?)\]\[img\](\s*)(.+?)(\s*)\[\/img\]\[\/url\]")


def rfn(m):
    return "[img]{}[/img]".format(m.group(1))


class Command(BaseCommand):
    def handle(self, *args, **options):
        for item in NewsItem.objects.all():
            if re_urlimg.match(item.message.raw):
                item.message = re_urlimg.sub(rfn, item.message.raw)
                item.save(update_fields=["_message_rendered", "message"])

        for item in ForumUser.objects.all():
            if re_urlimg.match(item.signature.raw):
                item.signature = re_urlimg.sub(rfn, item.signature.raw)
                item.save(update_fields=["_signature_rendered", "signature"])

        for item in ForumPost.objects.all():
            if re_urlimg.match(item.message.raw):
                item.message = re_urlimg.sub(rfn, item.message.raw)
                item.save(update_fields=["_message_rendered", "message"])
