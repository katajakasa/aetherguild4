from django.db import models


class ForumBoards(models.Model):
    sid = models.ForeignKey('ForumSections', models.DO_NOTHING, db_column='sid')
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    min_read_level = models.PositiveSmallIntegerField()
    min_write_level = models.PositiveSmallIntegerField()
    sort_index = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'forum_boards'


class ForumLastReads(models.Model):
    tid = models.ForeignKey('ForumThreads', models.DO_NOTHING, db_column='tid', primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'forum_last_reads'
        unique_together = (('tid', 'uid'),)


class ForumPostEdits(models.Model):
    pid = models.ForeignKey('ForumPosts', models.DO_NOTHING, db_column='pid')
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    edit_time = models.DateTimeField()
    description = models.CharField(max_length=256)

    class Meta:
        managed = False
        db_table = 'forum_post_edits'


class ForumPosts(models.Model):
    tid = models.ForeignKey('ForumThreads', models.DO_NOTHING, db_column='tid')
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    message = models.TextField()
    post_time = models.DateTimeField()
    ip = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'forum_posts'


class ForumSections(models.Model):
    title = models.CharField(max_length=64)
    sort_index = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'forum_sections'


class ForumThreads(models.Model):
    bid = models.ForeignKey(ForumBoards, models.DO_NOTHING, db_column='bid')
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    title = models.CharField(max_length=64)
    post_time = models.DateTimeField()
    views = models.PositiveIntegerField()
    sticky = models.IntegerField()
    closed = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'forum_threads'


class News(models.Model):
    header = models.CharField(max_length=64)
    message = models.TextField()
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'news'


class OldUsers(models.Model):
    uid = models.AutoField(primary_key=True)
    password = models.CharField(max_length=40)
    salt = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'old_users'


class Images(models.Model):
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    filename = models.CharField(max_length=256, blank=True, null=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    filesize = models.PositiveIntegerField()
    upload_time = models.DateTimeField()
    title = models.CharField(max_length=128)
    type = models.PositiveIntegerField()
    rights = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'images'


class Profiles(models.Model):
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid')
    email = models.CharField(max_length=128)
    email_public = models.IntegerField()
    website = models.CharField(max_length=128)
    signature = models.TextField()
    timezone = models.CharField(max_length=64)
    timeformat = models.CharField(max_length=32)
    staylogged = models.IntegerField()
    location = models.CharField(max_length=128)
    forumlimit_msg = models.PositiveIntegerField()
    forumlimit_thr = models.PositiveIntegerField()
    avatar = models.ForeignKey(Images, models.DO_NOTHING, blank=True, null=True)
    chat_color = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'profiles'


class Users(models.Model):
    username = models.CharField(unique=True, max_length=32)
    password = models.CharField(max_length=32)
    alias = models.CharField(max_length=32)
    level = models.PositiveIntegerField()
    active = models.PositiveSmallIntegerField()
    registered = models.DateTimeField()
    lastcontact = models.DateTimeField()
    lastlogoffpoint = models.DateTimeField()
    spambot = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'users'
