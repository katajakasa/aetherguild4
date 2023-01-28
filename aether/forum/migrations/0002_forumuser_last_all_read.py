# Generated by Django 2.1 on 2018-08-05 23:04

from django.db import migrations, models

import aether.forum.models


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="forumuser",
            name="last_all_read",
            field=models.DateTimeField(default=aether.forum.models.utc_now),
        ),
    ]
