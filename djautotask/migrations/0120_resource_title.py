# Generated by Django 4.2.16 on 2024-10-30 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0119_merge_20241024_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='title',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
