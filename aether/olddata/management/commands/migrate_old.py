import binascii
import arrow

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import transaction, IntegrityError

from aether.forum import models as forum_models
from aether.olddata import models as old_models
from aether.main_site import models as site_models

"""
Run this for source database first:
update users SET lastlogoffpoint = lastcontact WHERE lastlogoffpoint = '0000-00-00 00:00:00';
"""


def make_utc(dt):
    return arrow.get(dt, 'Europe/Amsterdam').to('UTC').datetime


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.level_to_group_map = {}
        self.user_mapping = {}
        self.forum_perm_mapping = {}
        self.section_mapping = {}
        self.board_mapping = {}
        self.thread_mapping = {}
        self.post_mapping = {}

    @staticmethod
    def log(name, text):
        print("[{0: <10}] {1}".format(name, text))

    def migrate_users(self):
        for old_user in old_models.Users.objects.using('old').all():
            user = User(
                is_active=False,
                is_staff=False,
                is_superuser=False,
                date_joined=make_utc(old_user.registered),
                last_login=make_utc(old_user.lastcontact),
                username=old_user.username
            )
            forum_user = forum_models.ForumUser(
                alias=old_user.alias,
                last_all_read=make_utc(old_user.lastcontact)
            )

            # If old profile exists, fill data
            try:
                old_profile = old_models.Profiles.objects.using("old").get(uid=old_user.id)
                forum_user.signature = self.replace_escapes(old_profile.signature)
                forum_user.timezone = old_profile.timezone
                forum_user.message_limit = old_profile.forumlimit_msg
                forum_user.thread_limit = old_profile.forumlimit_thr
                user.email = old_profile.email
            except old_models.Profiles.DoesNotExist:
                pass

            # Handle password conversion
            old_pw = binascii.hexlify(old_user.password)
            if old_pw == b'0000000000000000000000000000000000000000000000000000000000000000':
                old_pw = None

            # If user has no posts and is ancient, drop
            has_posts = old_models.ForumPosts.objects.using("old").filter(uid=old_user.id).exists()
            if not has_posts and not old_pw:
                self.log("user", "{} DROPPED".format(old_user.username))
                continue

            # Migrate password OR reset password if password is ancient
            if old_pw:
                user.password = 'sha256${}${}'.format(settings.OLD_PW_SALT, old_pw.decode())
            else:
                user.set_unusable_password()

            # Activate user only if it was originally active and not a spambot
            if bool(old_user.active) and not bool(old_user.spambot):
                user.is_active = True
            else:
                user.is_active = False

            # admin, root to staff
            if old_user.level in [3, 4]:
                user.is_staff = True

            # Root to superuser
            if old_user.level == 4:
                user.is_superuser = True

            # That's that, save user
            user.save()
            forum_user.user = user
            forum_user.save()

            # Save to mapping
            groups = set()
            for level, group in self.level_to_group_map.items():
                if level <= old_user.level:
                    groups.add(group)

            for group in groups:
                group.user_set.add(user)

            # Old to new user ID mapping
            self.user_mapping[old_user.id] = user.id

            # Log task
            self.log("user", "{} migrated".format(old_user.username))

    @staticmethod
    def clear_target_db():
        site_models.NewsItem.objects.all().delete()

        forum_models.ForumUser.objects.all().delete()
        forum_models.ForumLastRead.objects.all().delete()
        forum_models.ForumPostEdit.objects.all().delete()
        forum_models.ForumPost.objects.all().delete()
        forum_models.ForumThread.objects.all().delete()
        forum_models.ForumBoard.objects.all().delete()
        forum_models.ForumSection.objects.all().delete()

        User.objects.all().delete()
        Group.objects.all().delete()
        Permission.objects.all().delete()

    def migrate_news(self):
        for old_item in old_models.News.objects.using('old').all():
            item = site_models.NewsItem(
                nickname='Rinnagaros',
                header=old_item.header,
                message=self.replace_bbcode(old_item.message),
                created_at=make_utc(old_item.time)
            )
            item.save()
            self.log("newsitem", "{} migrated".format(old_item.header))

    def create_groups(self):
        basic = Group.objects.create(name='basic_users')
        advanced = Group.objects.create(name='advanced_users')
        admin = Group.objects.create(name='admin_users')
        self.level_to_group_map = {
            0: basic,  # guest to guest
            1: basic,  # newbie to guest
            2: advanced,  # user to user
            3: admin,  # admin to admin
            4: admin   # root to admin
        }

        # Add default permissions
        ct = ContentType.objects.get_for_model(forum_models.ForumBoard)
        basic.permissions.add(Permission.objects.create(codename='can_view_basic_boards',
                                                        name='Can view basic boards',
                                                        content_type=ct))
        basic.permissions.add(Permission.objects.create(codename='can_write_basic_boards',
                                                        name='Can post to basic boards',
                                                        content_type=ct))

        advanced.permissions.add(Permission.objects.create(codename='can_view_advanced_boards',
                                                           name='Can view advanced boards',
                                                           content_type=ct))
        advanced.permissions.add(Permission.objects.create(codename='can_write_advanced_boards',
                                                           name='Can post to advanced boards',
                                                           content_type=ct))

        admin.permissions.add(Permission.objects.create(codename='can_view_admin_boards',
                                                        name='Can view admin boards',
                                                        content_type=ct))
        admin.permissions.add(Permission.objects.create(codename='can_write_admin_boards',
                                                        name='Can post to admin boards',
                                                        content_type=ct))

        admin.permissions.add(Permission.objects.create(codename='can_manage_boards',
                                                        name='Can manage boards',
                                                        content_type=ct))
        admin.permissions.add(Permission.objects.create(codename='can_manage_news',
                                                        name='Can manage news items',
                                                        content_type=ct))

        self.forum_perm_mapping = {
            0: (None, None),  # guest to guest
            1: ('can_view_basic_boards', 'can_write_basic_boards'),  # newbie to basic
            2: ('can_view_advanced_boards', 'can_write_advanced_boards'),  # user to user
            3: ('can_view_admin_boards', 'can_write_admin_boards'),  # admin to admin
            4: ('can_view_admin_boards', 'can_write_admin_boards'),  # root to admin
        }

    @staticmethod
    def replace_escapes(value):
        return value.replace("\\'", "'").replace('\\"', '"')

    @staticmethod
    def replace_bbcode(value):
        return value\
            .replace('[list=disc]', '[ul]') \
            .replace('[list=1]', '[ul]') \
            .replace('[list]', '[ul]') \
            .replace('[/list]', '[/ul]')\
            .replace('[*]', '[li]')\
            .replace('[/*]', '[/li]')

    @staticmethod
    def replace_html(value):
        return value.replace('&amp;', '&')\
            .replace('&lt;', '<')\
            .replace('&gt;', '>')\
            .replace('&quot;', '"')

    def migrate_sections(self):
        for old_section in old_models.ForumSections.objects.using('old').all():
            section = forum_models.ForumSection(
                title=old_section.title,
                sort_index=old_section.sort_index
            )
            section.save()
            self.section_mapping[old_section.id] = section.id
            self.log("section", "{} migrated".format(old_section.title))

    def migrate_boards(self):
        for old_board in old_models.ForumBoards.objects.using('old').all():
            read_codename = self.forum_perm_mapping[old_board.min_read_level][0]
            write_codename = self.forum_perm_mapping[old_board.min_write_level][1]
            board = forum_models.ForumBoard(
                section_id=self.section_mapping[old_board.sid.id],
                title=old_board.title,
                description=old_board.description,
                sort_index=old_board.sort_index,
                read_perm=Permission.objects.get(codename=read_codename) if read_codename else None,
                write_perm=Permission.objects.get(codename=write_codename) if write_codename else None,
            )
            board.save()
            self.board_mapping[old_board.id] = board.id
            self.log("board", "{} migrated".format(old_board.title))

    def migrate_threads(self):
        for old_thread in old_models.ForumThreads.objects.using('old').iterator():
            latest_post = old_models.ForumPosts.objects.using('old').filter(tid=old_thread.id).order_by('-id').first()
            thread = forum_models.ForumThread(
                board_id=self.board_mapping[old_thread.bid.id],
                user_id=self.user_mapping[old_thread.uid.id],
                title=self.replace_html(old_thread.title),
                created_at=make_utc(old_thread.post_time),
                modified_at=make_utc(latest_post.post_time),
                views=old_thread.views,
                sticky=bool(old_thread.sticky),
                closed=bool(old_thread.closed)
            )
            thread.save()
            self.thread_mapping[old_thread.id] = thread.id
            self.log("thread", "{} migrated".format(old_thread.title))

    def migrate_posts(self):
        count = 0
        for old_post in old_models.ForumPosts.objects.using('old').iterator():
            post = forum_models.ForumPost(
                user_id=self.user_mapping[old_post.uid.id],
                thread_id=self.thread_mapping[old_post.tid.id],
                created_at=make_utc(old_post.post_time),
                message=self.replace_bbcode(old_post.message)
            )
            post.save()
            self.post_mapping[old_post.id] = post.id
            count += 1
            if count % 100 == 0:
                self.log("post", "{} migrated".format(count))

    def migrate_post_edits(self):
        count = 0
        for old_edit in old_models.ForumPostEdits.objects.using('old').iterator():
            profile = forum_models.ForumUser.objects.get(user_id=self.user_mapping[old_edit.uid.id])
            edit = forum_models.ForumPostEdit(
                post_id=self.post_mapping[old_edit.pid.id],
                editor=profile.alias,
                created_at=make_utc(old_edit.edit_time),
                message=old_edit.description
            )
            edit.save()
            count += 1
            if count % 100 == 0:
                self.log("post_edit", "{} migrated".format(count))

    def migrate_last_reads(self):
        for old_read in old_models.ForumLastReads.objects.using('old').all():
            if old_read.uid.id not in self.user_mapping:
                self.log("post_read", "{}/{} skipped due to deleted user".format(old_read.tid.id, old_read.uid.id))
            else:
                read = forum_models.ForumLastRead(
                    thread_id=self.thread_mapping[old_read.tid.id],
                    user_id=self.user_mapping[old_read.uid.id],
                    created_at=make_utc(old_read.time),
                )
                read.save()
                self.log("post_read", "{}/{} migrated".format(old_read.tid.id, old_read.uid.id))

    @transaction.atomic
    def handle(self, *args, **options):
        self.clear_target_db()
        self.create_groups()
        self.migrate_users()
        self.migrate_news()
        self.migrate_sections()
        self.migrate_boards()
        self.migrate_threads()
        self.migrate_posts()
        self.migrate_post_edits()
        self.migrate_last_reads()
