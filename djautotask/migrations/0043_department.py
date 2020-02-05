# Generated by Django 2.1.14 on 2020-02-05 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0042_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('number', models.TextField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
