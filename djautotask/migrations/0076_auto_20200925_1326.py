# Generated by Django 2.1.14 on 2020-09-25 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0075_taskpredecessor'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskpredecessor',
            options={'ordering': ('predecessor_task__title',)},
        ),
        migrations.AlterField(
            model_name='taskpredecessor',
            name='predecessor_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='predecessor_task_set', to='djautotask.Task'),
        ),
        migrations.AlterField(
            model_name='taskpredecessor',
            name='successor_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='successor_task_set', to='djautotask.Task'),
        ),
    ]
