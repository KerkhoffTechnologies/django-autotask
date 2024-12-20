# Generated by Django 4.2.16 on 2024-12-10 11:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0124_project_create_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.account'),
        ),
        migrations.AlterField(
            model_name='task',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djautotask.project'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.account'),
        ),
    ]
