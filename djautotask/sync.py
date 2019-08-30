import logging

from suds.client import Client
from atws import connect, Query

from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone


from djautotask import models

logger = logging.getLogger(__name__)


class InvalidObjectException(Exception):
    """
    If for any reason an object can't be created (for example, it references
    an unknown foreign object, or is missing a required field), raise this
    so that the synchronizer can catch it and continue with other records.
    """
    pass


def log_sync_job(f):
    def wrapper(*args, **kwargs):
        sync_instance = args[0]
        created_count = updated_count = deleted_count = 0
        sync_job = models.SyncJob()
        sync_job.start_time = timezone.now()
        if sync_instance.full:
            sync_job.sync_type = 'full'
        else:
            sync_job.sync_type = 'partial'

        try:
            created_count, updated_count, deleted_count = f(*args, **kwargs)
            sync_job.success = True
        except Exception as e:
            sync_job.message = str(e.args[0])
            sync_job.success = False
            raise
        finally:
            sync_job.end_time = timezone.now()
            sync_job.entity_name = sync_instance.model_class.__name__
            sync_job.added = created_count
            sync_job.updated = updated_count
            sync_job.deleted = deleted_count
            sync_job.save()

        return created_count, updated_count, deleted_count
    return wrapper


class SyncResults:
    """Track results of a sync job."""
    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.deleted_count = 0
        self.synced_ids = set()


class Synchronizer:
    lookup_key = 'id'

    def __init__(self, full=False, *args, **kwargs):
        self.full = full

        self.at_api_object = self.init_api_connection()

    def init_api_connection(self):
        return connect(
            username=settings.AUTOTASK_CREDENTIALS['username'],
            password=settings.AUTOTASK_CREDENTIALS['password'],
            integrationcode=settings.AUTOTASK_CREDENTIALS['integration_code'],
        )

    def _instance_ids(self, filter_params=None):
        if not filter_params:
            ids = self.model_class.objects.all().values_list(
                self.lookup_key, flat=True
            )
        else:
            ids = self.model_class.objects.filter(filter_params).values_list(
                self.lookup_key, flat=True
            )
        return set(ids)

    def get(self, query_object, results):
        """
        Fetch records from the API. ATWS automatically makes multiple separate
        queries if the request is over 500 records.
        """
        logger.info(
            'Fetching {} records'.format(self.model_class)
        )
        for record in query_object:
            self.persist_record(record, results)

        return results

    def persist_record(self, record, results):
        """Persist each record to the DB."""
        try:
            with transaction.atomic():
                _, created = self.update_or_create_instance(record)
            if created:
                results.created_count += 1
            else:
                results.updated_count += 1
        except InvalidObjectException as e:
            logger.warning('{}'.format(e))

        results.synced_ids.add(record['id'])

        return results

    def update_or_create_instance(self, record):
        """Creates and returns an instance if it does not already exist."""
        created = False
        api_instance = Client.dict(record)

        try:
            instance_pk = api_instance[self.lookup_key]
            instance = self.model_class.objects.get(pk=instance_pk)
        except self.model_class.DoesNotExist:
            instance = self.model_class()
            created = True

        try:
            self._assign_field_data(instance, api_instance)
            instance.save()
        except IntegrityError as e:
            msg = "IntegrityError while attempting to create {}." \
                  " Error: {}".format(self.model_class, e)
            logger.error(msg)
            raise InvalidObjectException(msg)

        logger.info(
            '{}: {} {}'.format(
                'Created' if created else 'Updated',
                self.model_class.__name__,
                instance
            )
        )

        return instance, created

    def prune_stale_records(self, initial_ids, synced_ids):
        """
        Delete records that existed when sync started but were
        not seen as we iterated through all records from the API.
        """
        stale_ids = initial_ids - synced_ids
        deleted_count = 0
        if stale_ids:
            delete_qset = self.model_class.objects.filter(pk__in=stale_ids)
            deleted_count = delete_qset.count()

            logger.info(
                'Removing {} stale records for model: {}'.format(
                    len(stale_ids), self.model_class,
                )
            )
            delete_qset.delete()

        return deleted_count

    @log_sync_job
    def sync(self):
        sync_job_qset = models.SyncJob.objects.filter(
            entity_name=self.model_class.__name__
        )
        results = SyncResults()
        query = Query(self.model_class.__name__)

        if sync_job_qset.exists() and not self.full:
            last_sync_job_time = sync_job_qset.last().start_time
            query.WHERE(self.last_updated_field,
                        query.GreaterThanorEquals, last_sync_job_time)

        else:
            query.WHERE('id', query.GreaterThan, 0)

        query_object = self.at_api_object.query(query)

        # Set of IDs of all records prior
        # to sync, to find stale records for deletion.
        initial_ids = self._instance_ids()
        results = self.get(query_object, results)

        if self.full:
            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return \
            results.created_count, results.updated_count, results.deleted_count


class TicketSynchronizer(Synchronizer):
    model_class = models.Ticket
    last_updated_field = 'LastActivityDate'

    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.title = object_data['Title']

        instance.ticket_number = object_data.get('TicketNumber')
        instance.completed_date = object_data.get('CompletedDate')
        instance.create_date = object_data.get('CreateDate')
        instance.description = object_data.get('Description')
        instance.due_date_time = object_data.get('DueDateTime')
        instance.estimated_hours = object_data.get('EstimatedHours')
        instance.last_activity_date = object_data.get('LastActivityDate')

        return instance
