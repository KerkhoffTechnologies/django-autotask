# Generated by Django 3.1.7 on 2022-01-04 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0101_auto_20220104_1349'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='task_category',
            new_name='category',
        ),
    ]
