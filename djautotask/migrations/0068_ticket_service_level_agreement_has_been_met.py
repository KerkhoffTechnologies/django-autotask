# Generated by Django 2.1.14 on 2020-05-14 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0067_ticket_service_level_agreement'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='service_level_agreement_has_been_met',
            field=models.BooleanField(default=False),
        ),
    ]