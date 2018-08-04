# Generated by Django 2.1 on 2018-08-04 22:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_auto_20180804_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumboard',
            name='read_perm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='readable_boards', to='auth.Permission'),
        ),
        migrations.AlterField(
            model_name='forumboard',
            name='write_perm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='writable_boards', to='auth.Permission'),
        ),
        migrations.AlterField(
            model_name='forumlastread',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='last_reads', to='forum.ForumThread'),
        ),
        migrations.AlterField(
            model_name='forumlastread',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='last_reads', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='forumpost',
            name='thread',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='forum.ForumThread'),
        ),
        migrations.AlterField(
            model_name='forumpostedit',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edits', to='forum.ForumPost'),
        ),
        migrations.AlterField(
            model_name='forumthread',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='threads', to='forum.ForumBoard'),
        ),
    ]
