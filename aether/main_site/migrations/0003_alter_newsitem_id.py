# Generated by Django 3.2.4 on 2021-06-16 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_site", "0002_auto_20180808_0216"),
    ]

    operations = [
        migrations.AlterField(
            model_name="newsitem",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
