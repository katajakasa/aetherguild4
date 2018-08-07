import binascii
import arrow

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import transaction

from aether.forum import models as forum_models
from aether.olddata import models as old_models
from aether.main_site import models as site_models


def make_utc(dt):
    return arrow.get(dt, 'Europe/Amsterdam').to('UTC').datetime


class Command(BaseCommand):
    @staticmethod
    def log(name, text):
        print("[{0: <10}] {1}".format(name, text))

    @staticmethod
    def clear_target_db():
        site_models.NewsItem.objects.all().delete()

    def migrate_news(self):
        for old_item in old_models.News.objects.using('old').all():
            item = site_models.NewsItem(
                nickname='Rinnagaros',
                header=old_item.header,
                message=self.replace_bbcode(old_item.message),
                created_at=make_utc(old_item.time),
                modified_at=make_utc(old_item.time)
            )
            item.save()
            self.log("newsitem", "{} migrated".format(old_item.header))

    @staticmethod
    def replace_bbcode(value):
        return value\
            .replace('[list=disc]', '[ul]') \
            .replace('[list=1]', '[ul]') \
            .replace('[list]', '[ul]') \
            .replace('[/list]', '[/ul]')\
            .replace('[*]', '[li]')\
            .replace('[/*]', '[/li]')

    @transaction.atomic
    def handle(self, *args, **options):
        self.clear_target_db()
        self.migrate_news()
