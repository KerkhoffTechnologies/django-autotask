from django.core.management.base import BaseCommand
from djautotask.models import Resource


class Command(BaseCommand):
    help = 'List active Autotask resources.'

    def handle(self, *args, **options):
        for resource in Resource.objects.filter(active=True):
            self.stdout.write(
                '{:15} {:20} {:43}'.format(
                    resource.user_name,
                    resource.__str__(),
                    resource.email,
                )
            )
