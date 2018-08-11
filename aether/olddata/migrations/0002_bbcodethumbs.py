# Generated by Django 2.0.8 on 2018-08-11 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olddata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bbcodethumbs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveIntegerField()),
                ('source_url', models.CharField(max_length=256, unique=True)),
                ('date_added', models.DateTimeField()),
                ('date_last_use', models.DateTimeField()),
                ('width', models.PositiveIntegerField()),
                ('height', models.PositiveIntegerField()),
                ('filesize', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'bbcodethumbs',
                'managed': False,
            },
        ),
    ]
