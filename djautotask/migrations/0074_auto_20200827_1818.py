# Generated by Django 2.1.14 on 2020-08-27 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0073_syncjob_skipped'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicecall',
            name='duration',
            field=models.DecimalField(blank=True, decimal_places=4, max_digits=9, null=True),
        ),
    ]
