# Generated by Django 2.1 on 2018-08-12 21:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
        ('forum', '0005_merge_20180811_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumpost',
            name='attached_gallery',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linked_posts', to='gallery.GalleryGroup'),
        ),
    ]
