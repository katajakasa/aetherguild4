from django.db.models import BooleanField, CharField, DateTimeField, Index, Model
from precise_bbcode.fields import BBCodeTextField

from aether.utils.misc import utc_now


class NewsItem(Model):
    nickname = CharField(max_length=128, null=False, blank=False)
    header = CharField(max_length=128, null=False, blank=False)
    message = BBCodeTextField(null=False, blank=False)
    created_at = DateTimeField(null=False, default=utc_now)
    modified_at = DateTimeField(null=False, default=utc_now)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return self.header

    class Meta:
        app_label = "main_site"
        indexes = [
            Index(fields=["created_at", "deleted"]),
        ]
