# Generated by Django 3.1.2 on 2020-12-10 06:04

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0085_auto_20201022_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('first_name', models.TextField(blank=True, max_length=20, null=True)),
                ('last_name', models.TextField(blank=True, max_length=20, null=True)),
                ('middle_initial', models.TextField(blank=True, max_length=50, null=True)),
                ('additional_address_information', models.CharField(blank=True, max_length=100, null=True)),
                ('address_line', models.CharField(blank=True, max_length=128, null=True)),
                ('address_line1', models.CharField(blank=True, max_length=128, null=True)),
                ('city', models.CharField(blank=True, max_length=32, null=True)),
                ('state', models.CharField(blank=True, max_length=40, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=16, null=True)),
                ('email_address', models.CharField(blank=True, max_length=50, null=True)),
                ('email_address2', models.CharField(blank=True, max_length=50, null=True)),
                ('email_address3', models.CharField(blank=True, max_length=50, null=True)),
                ('primary_contact', models.BooleanField(null=True)),
                ('receives_email_notifications', models.BooleanField(null=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.account')),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContactTracker',
            fields=[
            ],
            options={
                'db_table': 'djautotask_contact',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('djautotask.contact',),
        ),
        migrations.AddField(
            model_name='project',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.contact'),
        ),
        migrations.AddField(
            model_name='ticket',
            name='contact',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='djautotask.contact'),
        ),
    ]
