from django.apps import AppConfig


class DjangoAutotaskConfig(AppConfig):
    name = 'djautotask'
    # Django 6.0 changed the DEFAULT_AUTO_FIELD default from AutoField to
    # BigAutoField. Our models and their migrations were built with AutoField,
    # so pin it here: otherwise every project installing this app would get a
    # spurious migration altering the primary key of every model.
    default_auto_field = 'django.db.models.AutoField'
