# Generated by Django 2.0.8 on 2018-08-07 23:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forum", "0003_bbcodeimage"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bbcodeimage",
            options={"verbose_name": "BBCode Image", "verbose_name_plural": "BBCode Images"},
        ),
    ]
