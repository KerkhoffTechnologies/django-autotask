# Generated by Django 4.2.16 on 2024-12-02 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0123_alter_project_account_alter_task_project_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='create_date_time',
            field=models.DateTimeField(null=True),
        ),
    ]
