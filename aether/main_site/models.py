from django.db.models import Model, CharField, DateTimeField, BooleanField, Index
from precise_bbcode.fields import BBCodeTextField


class NewsItem(Model):
    nickname = CharField(max_length=128, null=False, blank=False)
    header = CharField(max_length=128, null=False, blank=False)
    message = BBCodeTextField(null=False, blank=False)
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return self.header

    class Meta:
        app_label = 'main_site'
        indexes = [
            Index(fields=['created_at', 'deleted']),
        ]
