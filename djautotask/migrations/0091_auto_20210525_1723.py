# Generated by Django 3.1.7 on 2021-05-25 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0090_auto_20210309_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, max_length=8000, null=True),
        ),
    ]