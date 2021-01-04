import logging

from django.db import transaction, IntegrityError

from djautotask import api_rest as api
from djautotask import models
from .sync import InvalidObjectException, SyncResults, log_sync_job

CREATED = 1
UPDATED = 2
SKIPPED = 3

logger = logging.getLogger(__name__)


class Synchronizer:
    lookup_key = 'id'

    def __init__(self, full=False, *args, **kwargs):
        self.api_conditions = []
        self.client = self.client_class()
        self.full = full

    def set_relations(self, instance, json_data):
        for json_field, value in self.related_meta.items():
            model_class, field_name = value
            self._assign_relation(
                instance,
                json_data,
                json_field,
                model_class,
                field_name
            )

    @staticmethod
    def _assign_null_relation(instance, model_field):
        """
        Set the FK to null, but handle issues like the FK being non-null.
        """
        try:
            setattr(instance, model_field, None)
        except ValueError:
            # The model_field may have been non-null.
            raise InvalidObjectException(
                "Unable to set field {} on {} to null, as it's required.".
                format(model_field, instance)
            )

    def _assign_relation(self, instance, json_data,
                         json_field, model_class, model_field):
        """
        Look up the given foreign relation, and set it to the given
        field on the instance.
        """
        uid = json_data.get(json_field)

        try:
            related_instance = model_class.objects.get(pk=uid)
            setattr(instance, model_field, related_instance)
        except model_class.DoesNotExist:
            logger.warning(
                'Failed to find {} {} for {} {}.'.format(
                    json_field,
                    uid,
                    type(instance),
                    instance.id
                )
            )
            self._assign_null_relation(instance, model_field)

    def _instance_ids(self, filter_params=None):
        if not filter_params:
            ids = self.model_class.objects.all().order_by(self.lookup_key)\
                .values_list(self.lookup_key, flat=True)
        else:
            ids = self.model_class.objects.filter(filter_params)\
                .order_by(self.lookup_key)\
                .values_list(self.lookup_key, flat=True)
        return set(ids)

    def get(self, results):
        return self.fetch_records(results)

    def fetch_records(self, results):
        """
        For all pages of results, save each page of results to the DB.
        """
        next_url = None
        while True:
            logger.info(
                'Fetching {} records'.format(
                    self.model_class.__bases__[0].__name__)
            )
            api_return = self.get_page(next_url)
            page = api_return.get("items")
            next_url = api_return.get("pageDetails").get("nextPageUrl")
            self.persist_page(page, results)

            if not next_url:
                break

        return results

    def persist_page(self, records, results):
        """Persist one page of records to DB."""
        for record in records:
            try:
                with transaction.atomic():
                    instance, result = self.update_or_create_instance(record)
                if result == CREATED:
                    results.created_count += 1
                elif result == UPDATED:
                    results.updated_count += 1
                else:
                    results.skipped_count += 1
            except InvalidObjectException as e:
                logger.warning('{}'.format(e))

            results.synced_ids.add(record['id'])

        return results

    def get_page(self, *args, **kwargs):
        raise NotImplementedError

    def get_single(self, *args, **kwargs):
        raise NotImplementedError

    def _assign_field_data(self, instance, api_instance):
        raise NotImplementedError

    def update_or_create_instance(self, api_instance):
        """
        Creates and returns an instance if it does not already exist.
        """
        result = None
        api_instance = self.remove_null_characters(api_instance)
        try:
            instance_pk = api_instance[self.lookup_key]
            instance = self.model_class.objects.get(pk=instance_pk)
        except self.model_class.DoesNotExist:
            instance = self.model_class()
            result = CREATED

        try:
            self._assign_field_data(instance, api_instance)

            # This will return the created instance, the updated instance, or
            # if the instance is skipped an unsaved copy of the instance.
            if result == CREATED:
                if self.model_class is models.TicketTracker:
                    instance.save(force_insert=True)
                else:
                    instance.save()
            elif instance.tracker.changed():
                instance.save()
                result = UPDATED
            else:
                result = SKIPPED
        except IntegrityError as e:
            # This can happen when multiple threads are creating the
            # same ticket at once.
            msg = "IntegrityError while attempting to create {}." \
                  " Error: {}".format(self.model_class, e)
            logger.error(msg)
            raise InvalidObjectException(msg)

        if result == CREATED:
            result_log = 'Created'
        elif result == UPDATED:
            result_log = 'Updated'
        else:
            result_log = 'Skipped'

        logger.info('{}: {} {}'.format(
            result_log,
            self.model_class.__bases__[0].__name__,
            instance
        ))

        return instance, result

    def prune_stale_records(self, initial_ids, synced_ids):
        """
        Delete records that existed when sync started but were
        not seen as we iterated through all records from REST API.
        """
        stale_ids = initial_ids - synced_ids
        deleted_count = 0
        if stale_ids:
            delete_qset = self.get_delete_qset(stale_ids)
            deleted_count = delete_qset.count()

            logger.info(
                'Removing {} stale records for model: {}'.format(
                    len(stale_ids), self.model_class.__bases__[0].__name__,
                )
            )
            delete_qset.delete()

        return deleted_count

    def get_delete_qset(self, stale_ids):
        return self.model_class.objects.filter(pk__in=stale_ids)

    def get_sync_job_qset(self):
        return models.SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__
        )

    @log_sync_job
    def sync(self):
        sync_job_qset = self.get_sync_job_qset().filter(success=True)

        if sync_job_qset.count() > 1 and not self.full:
            last_sync_job_time = sync_job_qset.last().start_time.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            self.api_conditions.append(
                ["lastActivityDate", last_sync_job_time, "gt"]
            )
        results = SyncResults()
        results = self.get(results)

        if self.full:
            # Set of IDs of all records prior to sync,
            # to find stale records for deletion.
            initial_ids = self._instance_ids()

            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def remove_null_characters(self, json_data):
        for value in json_data:
            if isinstance(json_data.get(value), str):
                json_data[value] = json_data[value].replace('\x00', '')

        return json_data


class ContactSynchronizer(Synchronizer):
    client_class = api.ContactsAPIClient
    model_class = models.ContactTracker

    related_meta = {
        'companyID': (models.Account, 'account'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_conditions = [['IsActive', 'true']]

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.first_name = json_data.get('firstName')
        instance.last_name = json_data.get('lastName')
        instance.email_address = json_data.get('emailAddress')
        self.set_relations(instance, json_data)

        return instance

    def get_page(self, next_url=None, *args, **kwargs):
        kwargs['conditions'] = self.api_conditions
        return self.client.get_contacts(next_url, *args, **kwargs)
