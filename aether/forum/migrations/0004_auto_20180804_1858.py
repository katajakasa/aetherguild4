# Generated by Django 2.1 on 2018-08-04 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0003_auto_20180804_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumuser',
            name='avatar',
            field=models.ImageField(blank=True, default='', upload_to='avatars'),
            preserve_default=False,
        ),
    ]
