# Generated by Django 4.0.7 on 2022-10-14 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0108_billingcodetype_billingcodetypetracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingcode',
            name='billing_code_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.billingcodetype'),
        ),
    ]
