import arrow
import math

from django.db.models import (Model, ForeignKey, DateTimeField, CharField, TextField, IntegerField, BooleanField,
                              Index, OneToOneField, PositiveIntegerField, ImageField, PROTECT, CASCADE)
from django.contrib.auth.models import Permission, User
from django.conf import settings
from django.db import IntegrityError

from precise_bbcode.fields import BBCodeTextField
from timezone_field import TimeZoneField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


def utc_now():
    return arrow.utcnow().datetime


class ForumUser(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    alias = CharField(max_length=32)
    signature = BBCodeTextField(null=False, blank=True, default='')
    timezone = TimeZoneField(default='Europe/Amsterdam', null=False)
    message_limit = PositiveIntegerField(default=25)
    thread_limit = PositiveIntegerField(default=25)
    avatar = ImageField(upload_to='avatars', blank=True)
    avatar_thumbnail = ImageSpecField(source='avatar',
                                      processors=[ResizeToFill(150, 150)],
                                      format='PNG',
                                      options={'quality': 75})

    def __str__(self):
        return self.user.username


class ForumSection(Model):
    title = CharField(max_length=128, null=False, blank=False)
    sort_index = IntegerField(default=0, null=False)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return self.title

    @property
    def visible_boards(self):
        return self.boards.filter(deleted=False).order_by('sort_index')

    def can_read(self, user: User):
        for board in self.boards.filter(deleted=False):
            if board.read_perm is None or user.has_perm(board.read_perm):
                return True
        return False

    class Meta:
        app_label = 'forum'
        indexes = [
            Index(fields=['sort_index', 'deleted']),
            Index(fields=['deleted']),
        ]


class ForumBoard(Model):
    section = ForeignKey(ForumSection, on_delete=PROTECT, null=False, related_name='boards')
    title = CharField(max_length=128, null=False, blank=False)
    description = TextField(null=False)
    read_perm = ForeignKey(Permission, on_delete=PROTECT, null=True, related_name='readable_boards')
    write_perm = ForeignKey(Permission, on_delete=PROTECT, null=True, related_name='writable_boards')
    sort_index = IntegerField(default=0, null=False)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return self.title

    def can_read(self, user: User):
        if self.read_perm is None:
            return True
        return user.has_perm(self.read_perm.codename)

    def can_write(self, user: User):
        if not user.is_authenticated:
            return False
        if self.write_perm is None:
            return True
        return user.has_perm(self.write_perm.codename)

    @property
    def visible_threads(self):
        return self.threads.filter(deleted=False).order_by('-sticky', '-modified_at')

    @property
    def total_posts(self):
        return ForumPost.objects.filter(thread__board=self.pk, thread__deleted=False, deleted=False).count()

    @property
    def total_threads(self):
        return self.threads.filter(deleted=False).count()

    @property
    def last_post(self):
        return ForumPost.objects.filter(thread__board=self.pk, deleted=False).order_by('-id').first()

    class Meta:
        app_label = 'forum'
        indexes = [
            Index(fields=['section', 'sort_index', 'deleted']),
            Index(fields=['deleted']),
        ]


class ForumThread(Model):
    board = ForeignKey(ForumBoard, on_delete=PROTECT, null=False, related_name='threads')
    user = ForeignKey(User, on_delete=PROTECT, null=False)
    title = CharField(max_length=128, null=False, blank=False)
    created_at = DateTimeField(default=utc_now, null=False)
    modified_at = DateTimeField(default=utc_now, null=False)  # Can be edited manually
    views = IntegerField(default=0, null=False)
    sticky = BooleanField(default=False, null=False)
    closed = BooleanField(default=False, null=False)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return self.title

    @property
    def visible_posts(self):
        return self.posts.filter(deleted=False).order_by('id')

    @property
    def total_posts(self):
        return self.posts.filter(deleted=False).count()

    @property
    def last_post(self):
        return self.posts.filter(deleted=False).order_by('-id').first()

    def has_new_content(self, user: User):
        try:
            last_read = ForumLastRead.objects.get(user=user, thread=self)
        except ForumLastRead.DoesNotExist:
            return False
        return self.modified_at > last_read.created_at

    def set_modified(self):
        self.modified_at = utc_now()
        self.save()

    def get_last_read(self, user: User):
        try:
            return self.last_reads.get(user=user).created_at
        except ForumLastRead.DoesNotExist:
            return None

    class Meta:
        app_label = 'forum'
        indexes = [
            Index(fields=['board', 'sticky', 'modified_at', 'deleted']),
            Index(fields=['deleted']),
        ]


class ForumPost(Model):
    thread = ForeignKey(ForumThread, on_delete=PROTECT, null=False, related_name='posts')
    user = ForeignKey(User, on_delete=PROTECT, null=False)
    message = BBCodeTextField(null=False, blank=False)
    created_at = DateTimeField(default=utc_now, null=False)
    deleted = BooleanField(default=False, null=False)

    def __str__(self):
        return str(self.id)

    @property
    def visible_edits(self):
        return self.edits.exclude(message='').order_by('id')

    @property
    def is_first(self):
        return self.thread.visible_posts.first().id == self.id

    def page_for(self, user: User):
        show_count = user.profile.message_limit if user.is_authenticated else settings.FORUM_MESSAGE_LIMIT
        count = self.thread.total_posts
        return math.ceil(count / show_count)

    class Meta:
        app_label = 'forum'
        indexes = [
            Index(fields=['thread', 'created_at', 'deleted']),
            Index(fields=['deleted']),
        ]


class ForumPostEdit(Model):
    post = ForeignKey(ForumPost, on_delete=CASCADE, null=False, related_name='edits')
    editor = CharField(max_length=32, null=False, blank=False)
    message = CharField(max_length=255, null=False, blank=True)
    created_at = DateTimeField(default=utc_now, null=False)

    def __str__(self):
        return "{} by {}: {}".format(self.created_at, self.editor, self.message)

    class Meta:
        app_label = 'forum'
        indexes = [
            Index(fields=['post', 'created_at']),
        ]


class ForumLastRead(Model):
    thread = ForeignKey(ForumThread, on_delete=CASCADE, null=False, related_name='last_reads')
    user = ForeignKey(User, on_delete=CASCADE, null=False, related_name='last_reads')
    created_at = DateTimeField(default=utc_now, null=False)

    def __str__(self):
        return "{} by {}".format(self.thread.id, self.user.username)

    @staticmethod
    def refresh_last_read(user, thread):
        try:
            ForumLastRead.objects.create(user=user, thread=thread, created_at=utc_now())
        except IntegrityError:
            ForumLastRead.objects.filter(user=user, thread=thread).update(created_at=utc_now())

    class Meta:
        app_label = 'forum'
        unique_together = (('thread', 'user'),)

