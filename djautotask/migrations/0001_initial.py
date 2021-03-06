# Generated by Django 2.1.11 on 2019-08-28 16:25

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SyncJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('entity_name', models.CharField(max_length=100)),
                ('added', models.PositiveIntegerField(null=True)),
                ('updated', models.PositiveIntegerField(null=True)),
                ('deleted', models.PositiveIntegerField(null=True)),
                ('success', models.NullBooleanField()),
                ('message', models.TextField(blank=True, null=True)),
                ('sync_type', models.CharField(default='full', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('create_date', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, max_length=8000, null=True)),
                ('due_date_time', models.DateTimeField()),
                ('estimated_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('last_activity_date', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Ticket',
            },
        ),
    ]
