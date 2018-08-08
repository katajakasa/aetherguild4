import math
import typing

from django.db.models import (Model, ForeignKey, DateTimeField, CharField, TextField, IntegerField, BooleanField,
                              Index, OneToOneField, PositiveIntegerField, ImageField, PROTECT, CASCADE, Subquery,
                              OuterRef, QuerySet, URLField, Exists)
from django.contrib.auth.models import Permission, User
from django.utils.functional import cached_property
from django.conf import settings
from django.db import IntegrityError


from precise_bbcode.fields import BBCodeTextField
from timezone_field import TimeZoneField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Thumbnail

from aether.utils.permissions import has_perm_obj
from aether.utils.misc import utc_now, SQCount


class ForumUser(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name='profile')
    last_all_read = DateTimeField(default=utc_now, null=False)
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

    def mark_all_read(self, user: User) -> None:
        self.last_all_read = utc_now()
        self.save(update_fields=['last_all_read'])
        ForumLastRead.objects.filter(user=user).delete()

    def __str__(self) -> str:
        return self.user.username


class ForumSection(Model):
    title = CharField(max_length=128, null=False, blank=False)
    sort_index = IntegerField(default=0, null=False)
    deleted = BooleanField(default=False, null=False)

    def __str__(self) -> str:
        return self.title

    def visible_boards(self, user: User = None) -> QuerySet:
        qs = self.boards.filter(deleted=False)\
            .select_related('read_perm', 'read_perm__content_type', 'write_perm', 'write_perm__content_type')\
            .order_by('sort_index')

        # Post count for all posts on the board
        post_count_sq = ForumPost.objects.filter(
            thread__board=OuterRef('pk'), thread__deleted=False, deleted=False).values('pk')
        qs = qs.annotate(total_posts=SQCount(post_count_sq))

        # Thread count for the board
        post_count_sq = ForumThread.objects.filter(
            board=OuterRef('pk'), deleted=False).values('pk')
        qs = qs.annotate(total_threads=SQCount(post_count_sq))

        # Latest post ID for the threads
        latest_post_sq = ForumPost.objects.filter(
            thread__board=OuterRef('pk'), thread__deleted=False, deleted=False).order_by('-id').values('pk')[:1]
        qs = qs.annotate(latest_post_id=Subquery(latest_post_sq))

        # Find out if threads have new content since last visit
        if user and user.is_authenticated:
            limit_ts = user.profile.last_all_read
            reads_sq = ForumLastRead.objects\
                .filter(user=user, thread=OuterRef('pk'), created_at__gt=OuterRef('modified_at'))\
                .values('thread')
            threads_sq = ForumThread.objects\
                .filter(board_id=OuterRef('pk'), deleted=False, modified_at__gt=limit_ts)\
                .exclude(pk__in=Subquery(reads_sq))\
                .values('pk')
            qs = qs.annotate(new_posts_count=SQCount(threads_sq))

        return qs

    def get_latest_posts(self, ids: typing.List[int]) -> dict:
        sq = ForumPost.objects.filter(thread__board=OuterRef('thread__board'), deleted=False).values('pk')
        qs = ForumPost.objects.filter(pk__in=ids)\
            .select_related('user', 'user__profile', 'thread')\
            .annotate(post_count=SQCount(sq))
        return {x.id: x for x in qs.all()}

    def can_read(self, user: User) -> bool:
        for board in self.boards.filter(deleted=False):
            if board.read_perm is None:
                return True
            if has_perm_obj(user, board.read_perm):
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

    def __str__(self) -> str:
        return self.title

    def can_read(self, user: User) -> bool:
        if self.read_perm is None:
            return True
        return has_perm_obj(user, self.read_perm)

    def can_write(self, user: User) -> bool:
        if not user.is_authenticated:
            return False
        if self.write_perm is None:
            return True
        return has_perm_obj(user, self.write_perm)

    def visible_threads(self, user: User = None) -> QuerySet:
        qs = self.threads.filter(deleted=False)\
            .select_related('user', 'user__profile')\
            .order_by('-sticky', '-modified_at')

        # Post count for the threads
        post_count_sq = ForumPost.objects\
            .filter(thread=OuterRef('pk'), deleted=False).values('pk')
        qs = qs.annotate(total_posts=SQCount(post_count_sq))

        # Latest post ID for the threads
        latest_post_sq = ForumPost.objects.filter(thread=OuterRef('pk'), deleted=False).order_by('-id').values('pk')[:1]
        qs = qs.annotate(latest_post_id=Subquery(latest_post_sq))

        # Find out if threads have new content since last visit
        if user and user.is_authenticated:
            limit_ts = user.profile.last_all_read
            reads_sq = ForumLastRead.objects\
                .filter(user=user, thread=OuterRef('pk'), created_at__gt=OuterRef('modified_at'))\
                .values('thread')
            threads_sq = ForumThread.objects\
                .filter(pk=OuterRef('pk'), deleted=False, modified_at__gt=limit_ts)\
                .exclude(pk__in=Subquery(reads_sq))\
                .values('pk')
            qs = qs.annotate(new_posts_count=SQCount(threads_sq))

        return qs

    def get_latest_posts(self, ids: typing.List[int]) -> dict:
        sq = ForumPost.objects.filter(thread__board=self.pk, deleted=False).values('pk')
        qs = ForumPost.objects.filter(pk__in=ids)\
            .select_related('user', 'user__profile', 'thread')\
            .annotate(post_count=SQCount(sq))
        return {x.id: x for x in qs.all()}

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

    def __str__(self) -> str:
        return self.title

    @property
    def visible_posts(self) -> QuerySet:
        qs = self.posts.filter(deleted=False).select_related('user', 'user__profile').order_by('id')

        # Find out if post has edits
        post_edit_sq = ForumPostEdit.objects.filter(post=OuterRef('pk')).values('pk')
        qs = qs.annotate(has_edits=Exists(post_edit_sq))

        return qs

    @cached_property
    def last_post(self) -> QuerySet:
        sq = self.posts.filter(deleted=False).values('pk')
        return self.posts.filter(deleted=False)\
            .select_related('user', 'user__profile') \
            .annotate(post_count=SQCount(sq)) \
            .order_by('-id').first()

    def has_new_content(self, user: User) -> bool:
        try:
            last_read = ForumLastRead.objects.get(user=user, thread=self)
        except ForumLastRead.DoesNotExist:
            return False
        return self.modified_at > last_read.created_at

    def set_modified(self) -> None:
        self.modified_at = utc_now()
        self.save(update_fields=['modified_at'])

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

    def __str__(self) -> str:
        return str(self.id)

    @property
    def visible_edits(self) -> QuerySet:
        return self.edits.exclude(message='').order_by('id')

    @property
    def is_first(self) -> bool:
        return self.thread.visible_posts.first().id == self.id

    def page_for(self, user: User, count: int = None) -> int:
        show_count = user.profile.message_limit if user.is_authenticated else settings.FORUM_MESSAGE_LIMIT
        if not count:
            count = self.thread.posts.filter(deleted=False).count()
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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return "{} by {}".format(self.thread.id, self.user.username)

    @staticmethod
    def refresh_last_read(user, thread) -> None:
        try:
            ForumLastRead.objects.create(user=user, thread=thread, created_at=utc_now())
        except IntegrityError:
            ForumLastRead.objects.filter(user=user, thread=thread).update(created_at=utc_now())

    class Meta:
        app_label = 'forum'
        unique_together = (('thread', 'user'),)


class BBCodeImage(Model):
    source_url = URLField(db_index=True, unique=True)
    created_at = DateTimeField(default=utc_now, null=False)
    original = ImageField(upload_to='bbcode', blank=True)
    medium = ImageSpecField(source='original',
                            processors=[Thumbnail(800, 800)],
                            format='JPEG',
                            options={'quality': 80})
    small = ImageSpecField(source='original',
                           processors=[Thumbnail(120, 120)],
                           format='PNG',
                           options={'quality': 80})

    def __str__(self) -> str:
        return str(self.source_url)

    class Meta:
        app_label = 'forum'
        verbose_name = 'BBCode Image'
        verbose_name_plural = 'BBCode Images'
