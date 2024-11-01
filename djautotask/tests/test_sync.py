from dateutil.parser import parse

from django.test import TestCase

from copy import deepcopy
from djautotask import models
from djautotask import sync
from djautotask.sync import SyncResults
from djautotask.tests import fixtures, mocks, fixture_utils


class AssertSyncMixin:

    def assert_sync_job(self):
        qset = \
            models.SyncJob.objects.filter(
                entity_name=self.model_class.__bases__[0].__name__
            )
        assert qset.exists()


class SynchronizerTestMixin(AssertSyncMixin):
    synchronizer_class = None
    model_class = None
    fixture = None
    update_field = None
    lookup_key = 'id'

    def setUp(self):
        super().setUp()
        mocks.init_api_rest_connection()
        self.fixture_items = self.fixture["items"]

    def _call_api(self, return_data):
        raise NotImplementedError

    def _assert_fields(self, instance, json_data):
        raise NotImplementedError

    def _sync(self, return_data):
        _, get_patch = self._call_api(return_data)
        self.synchronizer = self.synchronizer_class()
        self.synchronizer.sync()
        return _, get_patch

    def _sync_with_results(self, return_data):
        _, get_patch = self._call_api(return_data)
        self.synchronizer = self.synchronizer_class()
        return self.synchronizer.sync()

    def _get_return_value(self, new_json_list):
        return {
            "items": new_json_list,
            "pageDetails": fixtures.API_PAGE_DETAILS
        }

    def _parse_datetime(self, datetime):
        return parse(datetime) if datetime else None

    def test_sync(self):
        self._sync(self.fixture)
        instance_dict = {
            self.synchronizer.get_record_id(c): c for c in self.fixture_items
        }

        for instance in self.model_class.objects.all():
            json_data = instance_dict[instance.id]
            self._assert_fields(instance, json_data)

        self.assert_sync_job()

    def test_save_instance(self):
        """
        Test to ensure synchronizer saves a instance locally.
        """
        self.synchronizer = self.synchronizer_class()
        self.assertGreater(self.model_class.objects.all().count(), 0)

        object_data = self.fixture_items[0]
        instance = self.model_class.objects.get(
            id=self.synchronizer.get_record_id(object_data)
        )

        self._assert_fields(instance, object_data)
        self.assert_sync_job()

    def test_sync_update(self):
        self._sync(self.fixture)

        json_data = self.fixture_items[0]

        instance_id = self.synchronizer.get_record_id(json_data)
        original = self.model_class.objects.get(id=instance_id)

        new_val = None
        update_field_type = type(getattr(original, self.update_field))
        if update_field_type is str:
            new_val = 'Some New Value'
        elif update_field_type is bool:
            new_val = not getattr(original, self.update_field)
        elif update_field_type is int:
            new_val = getattr(original, self.update_field) + 1

        new_json = deepcopy(self.fixture_items[0])
        new_json[self.update_field] = new_val
        new_json_list = [new_json]

        return_value = self._get_return_value(new_json_list)
        self._sync(return_value)

        changed = self.model_class.objects.get(id=instance_id)

        self.assertNotEqual(getattr(original, self.update_field), new_val)
        self._assert_fields(changed, new_json)

    def test_delete_stale_instances(self):
        """
        Local instance should be deleted if not returned during a full sync
        """
        self.synchronizer = self.synchronizer_class()
        instance_id = self.synchronizer.get_record_id(self.fixture_items[0])
        instance_qset = self.model_class.objects.filter(id=instance_id)
        self.assertEqual(instance_qset.count(), 1)

        _, patch = self._call_api(fixtures.API_EMPTY)

        synchronizer = self.synchronizer_class(full=True)
        synchronizer.sync()
        self.assertEqual(instance_qset.count(), 0)
        patch.stop()

    def test_sync_skips(self):
        self._sync(self.fixture)

        new_val = 'Some New Value'
        new_json = deepcopy(self.fixture_items[0])
        new_json[self.update_field] = new_val
        new_json_list = [new_json]

        # Sync it twice to be sure that the data will be updated, then ignored
        return_value = self._get_return_value(new_json_list)
        self._sync(return_value)
        _, updated_count, skipped_count, _ = \
            self._sync_with_results(return_value)

        self.assertGreater(skipped_count, 0)
        self.assertEqual(updated_count, 0)


class UDFSynchronizerTestMixin(SynchronizerTestMixin):
    update_field = 'label'
    lookup_key = 'name'

    def setUp(self):
        self.fixture_items = self.fixture["fields"]
        self._sync(self.fixture)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.name, object_data['name'])
        self.assertEqual(instance.label, object_data['label'])
        self.assertEqual(instance.type, object_data['type'])
        self.assertEqual(instance.is_picklist, object_data['isPickList'])

        if object_data['isPickList']:
            for item in object_data.get('picklistValues'):
                i = instance.picklist[item['value']]
                self.assertEqual(i['label'], item['label'])
                self.assertEqual(i['is_default_value'], item['isDefaultValue'])
                self.assertEqual(i['sort_order'], item['sortOrder'])
                self.assertEqual(i['is_active'], item['isActive'])
                self.assertEqual(i['is_system'], item['isSystem'])

    def _get_return_value(self, new_json_list):
        return {
            "fields": new_json_list,
        }


class PicklistSynchronizerTestMixin(SynchronizerTestMixin):
    update_field = 'label'
    lookup_key = 'value'

    def setUp(self):
        self.fixture_items = self.fixture["fields"][0]["picklistValues"]
        self._sync(self.fixture)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, int(object_data['value']))
        self.assertEqual(instance.label, object_data['label'])
        self.assertEqual(instance.is_default_value,
                         object_data['isDefaultValue'])
        self.assertEqual(instance.sort_order, object_data['sortOrder'])
        self.assertEqual(instance.is_active, object_data['isActive'])
        self.assertEqual(instance.is_system, object_data['isSystem'])

    def test_sync_skips(self):
        self._sync(self.fixture)

        new_val = 'Some New Value'
        new_fixture = deepcopy(self.fixture)
        new_json = new_fixture['fields'][0]['picklistValues'][0]
        new_json[self.update_field] = new_val

        # Sync it twice to be sure that the data will be updated, then ignored
        return_value = new_fixture
        self._sync(return_value)
        _, updated_count, skipped_count, _ = \
            self._sync_with_results(return_value)

        self.assertGreater(skipped_count, 0)
        self.assertEqual(updated_count, 0)

    def test_sync_update(self):
        self._sync(self.fixture)

        json_data = self.fixture_items[0]

        instance_id = json_data[self.lookup_key]
        original = self.model_class.objects.get(id=instance_id)

        new_val = 'Some New Value'
        new_fixture = deepcopy(self.fixture)
        new_json = new_fixture['fields'][0]['picklistValues'][0]
        new_json[self.update_field] = new_val
        return_value = new_fixture

        self._sync(return_value)
        changed = self.model_class.objects.get(id=instance_id)

        self.assertNotEqual(getattr(original, self.update_field), new_val)
        self._assert_fields(changed, new_json)


class TestContactSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ContactSynchronizer
    model_class = models.ContactTracker
    fixture = fixtures.API_CONTACT
    update_field = 'phone'

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_contacts_call(return_data)

    def _assert_fields(self, instance, json_data):
        self.assertEqual(instance.id, json_data['id'])
        self.assertEqual(instance.first_name, json_data['firstName'])
        self.assertEqual(instance.last_name, json_data['lastName'])
        self.assertEqual(instance.email_address, json_data['emailAddress'])
        self.assertEqual(instance.email_address2, json_data['emailAddress2'])
        self.assertEqual(instance.email_address3, json_data['emailAddress3'])
        self.assertEqual(instance.account_id, json_data['companyID'])
        self.assertEqual(instance.phone, json_data['phone'])
        self.assertEqual(instance.alternate_phone, json_data['alternatePhone'])
        self.assertEqual(instance.mobile_phone, json_data['mobilePhone'])


class TestAssignNullRelationMixin:
    def test_sync_assigns_null_relation(self):
        model_type = self.model_class.__bases__[0].__name__
        model_object = self.model_class.objects.first()

        self.assertIsNotNone(model_object.assigned_resource)

        fixture_instance = deepcopy(
            getattr(fixtures, 'API_{}'.format(model_type.upper()))
        )
        fixture_instance['items'][0].pop(self.assign_null_relation_field)

        _, patch = self._call_api(fixture_instance)
        synchronizer = self.synchronizer_class(full=True)
        synchronizer.sync()

        model_object = self.model_class.objects.get(id=model_object.id)
        self.assertIsNone(model_object.assigned_resource)
        patch.stop()


class TestTicketNoteSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TicketNoteSynchronizer
    model_class = models.TicketNoteTracker
    fixture = fixtures.API_TICKET_NOTE
    update_field = 'title'

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_tickets()
        fixture_utils.init_note_types()
        fixture_utils.init_ticket_notes()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_notes_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['title'])
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.create_date_time,
                         self._parse_datetime(object_data['createDateTime']))
        self.assertEqual(instance.last_activity_date,
                         self._parse_datetime(object_data['lastActivityDate']))
        self.assertEqual(instance.ticket.id, object_data['ticketID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['creatorResourceID'])
        self.assertEqual(instance.note_type.id, object_data['noteType'])


class TestTaskNoteSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TaskNoteSynchronizer
    model_class = models.TaskNoteTracker
    fixture = fixtures.API_TASK_NOTE
    update_field = 'title'

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_note_types()
        fixture_utils.init_task_notes()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_task_notes_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['title'])
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.create_date_time,
                         self._parse_datetime(object_data['createDateTime']))
        self.assertEqual(instance.last_activity_date,
                         self._parse_datetime(object_data['lastActivityDate']))
        self.assertEqual(instance.task.id, object_data['taskID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['creatorResourceID'])
        self.assertEqual(instance.note_type.id, object_data['noteType'])


class TestTicketSynchronizer(
        SynchronizerTestMixin, TestAssignNullRelationMixin, TestCase):
    synchronizer_class = sync.TicketSynchronizer
    model_class = models.TicketTracker
    fixture = fixtures.API_TICKET
    update_field = 'title'
    assign_null_relation_field = 'assignedResourceID'

    def setUp(self):
        super().setUp()
        fixture_utils.init_contracts()
        fixture_utils.init_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_accounts()
        fixture_utils.init_account_physical_locations()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_tickets_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['title'])
        self.assertEqual(instance.ticket_number, object_data['ticketNumber'])
        self.assertEqual(instance.completed_date,
                         self._parse_datetime(object_data['completedDate']))
        self.assertEqual(instance.create_date,
                         self._parse_datetime(object_data['createDate']))
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.due_date_time,
                         self._parse_datetime(object_data['dueDateTime']))
        self.assertEqual(instance.estimated_hours,
                         object_data['estimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         self._parse_datetime(object_data['lastActivityDate']))
        self.assertEqual(instance.status.id, object_data['status'])
        self.assertEqual(instance.assigned_resource.id,
                         object_data['assignedResourceID'])
        self.assertEqual(instance.contract.id, object_data['contractID'])
        self.assertEqual(instance.account.id, object_data['companyID'])
        self.assertEqual(instance.account_physical_location.id,
                         object_data['companyLocationID'])

    def test_sync_ticket_related_records(self):
        """
        Test to ensure that a ticket will sync related objects,
        in its case notes, and time entries, and secondary resources
        """
        ticket = models.Ticket.objects.first()
        ticket.status = models.Status.objects.first()
        results = SyncResults()
        time_mock, time_patch = mocks.create_mock_call(
            'djautotask.sync.TimeEntrySynchronizer.fetch_records',
            results
        )
        note_mock, note_patch = mocks.create_mock_call(
            'djautotask.sync.TicketNoteSynchronizer.fetch_records',
            results
        )
        resource_mock, resource_patch = mocks.create_mock_call(
            'djautotask.sync.TicketSecondaryResourceSynchronizer.'
            'fetch_records',
            results
        )
        _, _checklist_patch = mocks.create_mock_call(
            "djautotask.sync.TicketChecklistItemsSynchronizer.sync_items",
            None
        )

        self.synchronizer.sync_related(ticket)

        self.assertEqual(time_mock.call_count, 1)
        self.assertEqual(note_mock.call_count, 1)
        self.assertEqual(resource_mock.call_count, 1)
        time_patch.stop()
        note_patch.stop()
        resource_patch.stop()
        _checklist_patch.stop()


class TestTicketUDFSynchronizer(UDFSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TicketUDFSynchronizer
    model_class = models.TicketUDFTracker
    fixture = fixtures.API_UDF

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_udf_call(return_data)


class TestTaskUDFSynchronizer(UDFSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TaskUDFSynchronizer
    model_class = models.TaskUDFTracker
    fixture = fixtures.API_UDF

    def _call_api(self, return_data):
        return mocks.service_api_get_task_udf_call(return_data)


class TestProjectUDFSynchronizer(UDFSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ProjectUDFSynchronizer
    model_class = models.ProjectUDFTracker
    fixture = fixtures.API_UDF

    def _call_api(self, return_data):
        return mocks.service_api_get_project_udf_call(return_data)


class TestStatusSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.StatusSynchronizer
    model_class = models.StatusTracker
    fixture = fixtures.API_STATUS_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestPrioritySynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.PrioritySynchronizer
    model_class = models.PriorityTracker
    fixture = fixtures.API_PRIORITY_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestQueueSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.QueueSynchronizer
    model_class = models.QueueTracker
    fixture = fixtures.API_QUEUE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestProjectStatusSynchronizer(PicklistSynchronizerTestMixin,
                                    TestCase):
    synchronizer_class = sync.ProjectStatusSynchronizer
    model_class = models.ProjectStatusTracker
    fixture = fixtures.API_PROJECT_STATUS_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_project_picklist_call(return_data)


class TestProjectTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ProjectTypeSynchronizer
    model_class = models.ProjectTypeTracker
    fixture = fixtures.API_PROJECT_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_project_picklist_call(return_data)


class TestSourceSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.SourceSynchronizer
    model_class = models.SourceTracker
    fixture = fixtures.API_SOURCE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestIssueTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.IssueTypeSynchronizer
    model_class = models.IssueTypeTracker
    fixture = fixtures.API_ISSUE_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestSubIssueTypeSynchronizer(PicklistSynchronizerTestMixin,
                                   TestCase):
    synchronizer_class = sync.SubIssueTypeSynchronizer
    model_class = models.SubIssueTypeTracker
    fixture = fixtures.API_SUB_ISSUE_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestTicketTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TicketTypeSynchronizer
    model_class = models.TicketTypeTracker
    fixture = fixtures.API_TICKET_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_picklist_call(return_data)


class TestDisplayColorSynchronizer(PicklistSynchronizerTestMixin,
                                   TestCase):
    synchronizer_class = sync.DisplayColorSynchronizer
    model_class = models.DisplayColorTracker
    fixture = fixtures.API_DISPLAY_COLOR_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_category_picklist_call(return_data)


class TestServiceCallStatusSynchronizer(PicklistSynchronizerTestMixin,
                                        TestCase):
    synchronizer_class = sync.ServiceCallStatusSynchronizer
    model_class = models.ServiceCallStatusTracker
    fixture = fixtures.API_SERVICE_CALL_STATUS_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_service_call_statuses_call(return_data)


class TestTicketCategorySynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TicketCategorySynchronizer
    model_class = models.TicketCategoryTracker
    fixture = fixtures.API_TICKET_CATEGORY
    update_field = "name"

    def setUp(self):
        super().setUp()
        fixture_utils.init_display_colors()
        fixture_utils.init_ticket_categories()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_categories_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['name'])
        self.assertEqual(instance.active, object_data['isActive'])
        self.assertEqual(instance.display_color.id,
                         object_data['displayColorRGB'])


class TestResourceSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ResourceSynchronizer
    model_class = models.ResourceTracker
    fixture = fixtures.API_RESOURCE
    update_field = 'last_name'

    def setUp(self):
        super().setUp()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_resources_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.user_name, object_data['userName'])
        self.assertEqual(instance.first_name, object_data['firstName'])
        self.assertEqual(instance.last_name, object_data['lastName'])
        self.assertEqual(instance.email, object_data['email'])
        self.assertEqual(instance.active, object_data['isActive'])


class TestAccountSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.AccountSynchronizer
    model_class = models.AccountTracker
    fixture = fixtures.API_ACCOUNT
    update_field = "name"

    def setUp(self):
        super().setUp()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_accounts_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['companyName'])
        self.assertEqual(instance.number, str(object_data['companyNumber']))
        self.assertEqual(instance.active, object_data['isActive'])
        self.assertEqual(instance.last_activity_date,
                         self._parse_datetime(object_data['lastActivityDate']))


class TestAccountPhysicalLocationSynchronizer(SynchronizerTestMixin,
                                              TestCase):
    synchronizer_class = sync.AccountPhysicalLocationSynchronizer
    model_class = models.AccountPhysicalLocationTracker
    fixture = fixtures.API_ACCOUNT_PHYSICAL_LOCATION
    update_field = 'name'

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_account_physical_locations_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.account.id, object_data['companyID'])
        self.assertEqual(instance.name, object_data['name'])
        self.assertEqual(instance.active, object_data['isActive'])
        self.assertEqual(instance.primary, object_data['isPrimary'])


class FilterProjectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        fixture_utils.init_project_statuses()
        cls.inactive_status = models.ProjectStatus.objects.create(
            label='New (Inactive)', is_active=False, id=9)
        cls.inactive_project = \
            models.Project.objects.create(name='Inactive Project')
        cls.inactive_project.status = cls.inactive_status
        cls.inactive_project.save()


class TestProjectSynchronizer(SynchronizerTestMixin,
                              FilterProjectTestCase):
    synchronizer_class = sync.ProjectSynchronizer
    model_class = models.ProjectTracker
    fixture = fixtures.API_PROJECT
    update_field = 'description'

    def setUp(self):
        super().setUp()
        fixture_utils.init_contracts()
        fixture_utils.init_resources()
        fixture_utils.init_accounts()
        fixture_utils.init_departments()
        fixture_utils.init_project_types()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_projects_call(return_data)

    def test_sync(self):
        instance_dict = {c['id']: c for c in self.fixture_items}

        for instance in self.model_class.objects.all():
            if instance.status.is_active:
                json_data = instance_dict[instance.id]
                self._assert_fields(instance, json_data)

        self.assert_sync_job()

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['projectName'])
        self.assertEqual(instance.number, object_data['projectNumber'])
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.actual_hours, object_data['actualHours'])
        self.assertEqual(instance.completed_date,
                         self._parse_datetime(
                             object_data['completedDateTime']).date())
        self.assertEqual(instance.completed_percentage,
                         object_data['completedPercentage'])
        self.assertEqual(instance.duration, object_data['duration'])
        self.assertEqual(instance.start_date,
                         self._parse_datetime(
                             object_data['startDateTime']).date())
        self.assertEqual(instance.end_date,
                         self._parse_datetime(
                             object_data['endDateTime']).date())
        self.assertEqual(instance.estimated_time, object_data['estimatedTime'])
        self.assertEqual(instance.last_activity_date_time,
                         self._parse_datetime(
                             object_data['lastActivityDateTime']))
        self.assertEqual(instance.project_lead_resource.id,
                         object_data['projectLeadResourceID'])
        self.assertEqual(instance.account.id, object_data['companyID'])
        self.assertEqual(instance.status.id, object_data['status'])
        self.assertEqual(instance.type.id, object_data['projectType'])
        self.assertEqual(instance.contract.id, object_data['contractID'])
        self.assertEqual(instance.department.id, object_data['department'])

    def test_sync_filters_projects_in_inactive_status(self):
        """
        Test to ensure that sync does not persist projects in an
        inactive project status.
        """
        project_in_active_status = fixtures.API_PROJECT
        project_fixture = deepcopy(project_in_active_status)
        project_fixture["items"][0]['id'] = '5'
        project_fixture["items"][0]['status'] = self.inactive_status.id

        project_instance = fixture_utils.generate_api_objects(
            [project_fixture, fixtures.API_PROJECT]
        )
        _, patch = mocks.service_api_get_projects_call(project_instance)
        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()

        synced_project_ids = \
            models.Project.objects.values_list('id', flat=True)
        self.assertGreater(models.Project.objects.all().count(), 0)
        self.assertNotIn(project_fixture["items"][0]['id'], synced_project_ids)
        self.assertIn(project_in_active_status["items"][0]['id'],
                      synced_project_ids)
        patch.stop()

    def test_sync_filters_projects_in_complete_status(self):
        """
        Test to ensure that sync does not persist projects in an
        inactive project status.
        """
        project_in_complete_status = fixtures.API_PROJECT
        project_fixture = deepcopy(project_in_complete_status)
        project_fixture["items"][0]['id'] = '6'
        # 5 Is the Autotask system complete status
        project_fixture["items"][0]['status'] = 5

        project_instance = fixture_utils.generate_api_objects(
            [project_fixture, fixtures.API_PROJECT]
        )
        _, patch = mocks.service_api_get_projects_call(project_instance)
        synchronizer = sync.ProjectSynchronizer(full=True)
        synchronizer.sync()

        synced_project_ids = \
            models.Project.objects.values_list('id', flat=True)
        self.assertGreater(models.Project.objects.all().count(), 0)
        self.assertNotIn(project_fixture["items"][0]['id'], synced_project_ids)
        self.assertIn(project_in_complete_status["items"][0]['id'],
                      synced_project_ids)
        patch.stop()


class TestTaskSynchronizer(SynchronizerTestMixin,
                           TestAssignNullRelationMixin,
                           FilterProjectTestCase):
    synchronizer_class = sync.TaskSynchronizer
    model_class = models.TaskTracker
    fixture = fixtures.API_TASK
    update_field = "title"
    assign_null_relation_field = 'assignedResourceID'

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_statuses()
        fixture_utils.init_priorities()
        fixture_utils.init_project_statuses()
        fixture_utils.init_projects()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_tasks_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['title'])
        self.assertEqual(instance.number, object_data['taskNumber'])
        self.assertEqual(instance.completed_date,
                         self._parse_datetime(
                             object_data['completedDateTime']))
        self.assertEqual(instance.create_date,
                         self._parse_datetime(object_data['createDateTime']))
        self.assertEqual(instance.start_date,
                         self._parse_datetime(object_data['startDateTime']))
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.remaining_hours,
                         object_data['remainingHours'])
        self.assertEqual(instance.estimated_hours,
                         object_data['estimatedHours'])
        self.assertEqual(instance.last_activity_date,
                         self._parse_datetime(
                             object_data['lastActivityDateTime']))

        self.assertEqual(instance.status.id, object_data['status'])
        self.assertEqual(instance.priority.id, object_data['priorityLabel'])
        self.assertEqual(instance.project.id, object_data['projectID'])
        self.assertEqual(instance.assigned_resource.id,
                         object_data['assignedResourceID'])

    def test_sync_filters_tasks_on_inactive_project(self):

        # Add copied task to project in 'Complete' status to ensure it is
        # filtered out during the sync.
        task_fixture = deepcopy(fixtures.API_TASK)
        task_fixture["items"][0]['id'] = '7740'
        task_fixture["items"][0]['projectID'] = self.inactive_project.id

        task_instance = fixture_utils.generate_api_objects(
            [task_fixture, fixtures.API_TASK]
        )
        _, patch = mocks.service_api_get_tasks_call(task_instance)

        synchronizer = sync.TaskSynchronizer(full=True)
        synchronizer.sync()

        synced_task_ids = models.Task.objects.values_list('id', flat=True)
        self.assertGreater(models.Task.objects.all().count(), 0)
        self.assertNotIn(task_fixture["items"][0]['id'], synced_task_ids)
        self.assertIn(fixtures.API_TASK["items"][0]['id'], synced_task_ids)
        patch.stop()

    def test_sync_filters_tasks_on_complete_project(self):
        """
        Test to ensure that sync does not persist tasks on a complete project.
        """
        project = models.Project.objects.create(name='Complete Project')
        project.status = models.ProjectStatus.objects.get(id=5)
        project.save()

        task_fixture = deepcopy(fixtures.API_TASK)
        task_fixture["items"][0]['id'] = '7741'
        task_fixture["items"][0]['projectID'] = project.id

        task_instance = fixture_utils.generate_api_objects(
            [task_fixture, fixtures.API_TASK]
        )
        _, patch = mocks.service_api_get_tasks_call(task_instance)

        synchronizer = sync.TaskSynchronizer(full=True)
        synchronizer.sync()

        synced_task_ids = models.Task.objects.values_list('id', flat=True)
        self.assertGreater(models.Task.objects.all().count(), 0)
        self.assertNotIn(task_fixture["items"][0]['id'], synced_task_ids)
        self.assertIn(fixtures.API_TASK["items"][0]['id'], synced_task_ids)
        patch.stop()


class TestLicenseTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.LicenseTypeSynchronizer
    model_class = models.LicenseTypeTracker
    fixture = fixtures.API_LICENSE_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_license_types_call(return_data)


class TestUseTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.UseTypeSynchronizer
    model_class = models.UseTypeTracker
    fixture = fixtures.API_USE_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_use_types_call(return_data)


class TestTaskTypeLinkSynchronizer(PicklistSynchronizerTestMixin,
                                   TestCase):
    synchronizer_class = sync.TaskTypeLinkSynchronizer
    model_class = models.TaskTypeLinkTracker
    fixture = fixtures.API_TASK_TYPE_LINK_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_task_type_links_call(return_data)


class TestAccountTypeSynchronizer(PicklistSynchronizerTestMixin, TestCase):
    synchronizer_class = sync.AccountTypeSynchronizer
    model_class = models.AccountTypeTracker
    fixture = fixtures.API_ACCOUNT_TYPE_FIELD

    def _call_api(self, return_data):
        return mocks.service_api_get_account_types_call(return_data)


class TestTicketSecondaryResourceSynchronizer(SynchronizerTestMixin,
                                              TestCase):
    synchronizer_class = sync.TicketSecondaryResourceSynchronizer
    model_class = models.TicketSecondaryResourceTracker
    fixture = fixtures.API_TICKET_SECONDARY_RESOURCE
    update_field = 'resource_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()
        fixture_utils.init_resources()
        fixture_utils.init_roles()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_ticket_secondary_resources_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.ticket.id, object_data['ticketID'])
        self.assertEqual(instance.resource.id, object_data['resourceID'])
        self.assertEqual(instance.role.id, object_data['roleID'])


class TestTaskSecondaryResourceSynchronizer(SynchronizerTestMixin,
                                            TestCase):
    synchronizer_class = sync.TaskSecondaryResourceSynchronizer
    model_class = models.TaskSecondaryResourceTracker
    fixture = fixtures.API_TASK_SECONDARY_RESOURCE
    update_field = 'resource_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_roles()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_task_secondary_resources_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.resource.id, object_data['resourceID'])
        self.assertEqual(instance.task.id, object_data['taskID'])
        self.assertEqual(instance.role.id, object_data['roleID'])


class TestPhaseSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.PhaseSynchronizer
    model_class = models.PhaseTracker
    fixture = fixtures.API_PHASE
    update_field = "title"

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_phases()
        fixture_utils.init_tasks()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_phases_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.title, object_data['title'])
        self.assertEqual(instance.start_date,
                         self._parse_datetime(object_data['startDate']))
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.estimated_hours,
                         object_data['estimatedHours'])
        self.assertEqual(
            instance.last_activity_date,
            self._parse_datetime(object_data['lastActivityDateTime'])
        )
        self.assertEqual(instance.number, object_data['phaseNumber'])


class TestTimeEntrySynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TimeEntrySynchronizer
    model_class = models.TimeEntryTracker
    fixture = fixtures.API_TIME_ENTRY
    update_field = 'summary_notes'

    def setUp(self):
        super().setUp()
        fixture_utils.init_resources()
        fixture_utils.init_tickets()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_time_entries_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.date_worked,
                         self._parse_datetime(object_data['dateWorked']))
        self.assertEqual(instance.start_date_time,
                         self._parse_datetime(object_data['startDateTime']))
        self.assertEqual(instance.end_date_time,
                         self._parse_datetime(object_data['endDateTime']))
        self.assertEqual(instance.summary_notes, object_data['summaryNotes'])
        self.assertEqual(instance.internal_notes, object_data['internalNotes'])
        self.assertEqual(instance.non_billable, object_data['isNonBillable'])
        self.assertEqual(instance.hours_worked, object_data['hoursWorked'])
        self.assertEqual(instance.hours_to_bill, object_data['hoursToBill'])
        self.assertEqual(instance.offset_hours, object_data['offsetHours'])
        if object_data['ticketID']:
            self.assertEqual(instance.ticket.id, object_data['ticketID'])
        if object_data['taskID']:
            self.assertEqual(instance.task.id, object_data['taskID'])
        self.assertEqual(instance.resource.id, object_data['resourceID'])


class TestBillingCodeSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.BillingCodeSynchronizer
    model_class = models.BillingCodeTracker
    fixture = fixtures.API_BILLING_CODE
    update_field = 'name'

    def setUp(self):
        super().setUp()
        fixture_utils.init_use_types()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_billing_codes_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data.get('name'))
        self.assertEqual(instance.description, object_data.get('description'))
        self.assertEqual(instance.active, object_data.get('isActive'))
        self.assertEqual(instance.use_type.id, object_data.get('useType'))


class TestRoleSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.RoleSynchronizer
    model_class = models.RoleTracker
    fixture = fixtures.API_ROLE
    update_field = 'description'

    def setUp(self):
        super().setUp()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_roles_call(return_data)

    def _assert_fields(self, instance, json_data):
        self.assertEqual(instance.id, json_data['id'])
        self.assertEqual(instance.name, json_data['name'])
        self.assertEqual(instance.description, json_data['description'])
        self.assertEqual(instance.active, json_data['isActive'])
        self.assertEqual(instance.hourly_factor, json_data['hourlyFactor'])
        self.assertEqual(instance.hourly_rate, json_data['hourlyRate'])
        self.assertEqual(instance.role_type, json_data['roleType'])
        self.assertEqual(instance.system_role, json_data['isSystemRole'])


class TestDepartmentSynchronizer(SynchronizerTestMixin,
                                 TestCase):
    synchronizer_class = sync.DepartmentSynchronizer
    model_class = models.DepartmentTracker
    fixture = fixtures.API_DEPARTMENT
    update_field = 'description'

    def setUp(self):
        super().setUp()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_departments_call(return_data)

    def _assert_fields(self, instance, json_data):
        self.assertEqual(instance.id, json_data['id'])
        self.assertEqual(instance.name, json_data['name'])
        self.assertEqual(instance.description, json_data['description'])
        self.assertEqual(instance.number, json_data['number'])


class TestResourceRoleDepartmentSynchronizer(SynchronizerTestMixin,
                                             TestCase):
    synchronizer_class = sync.ResourceRoleDepartmentSynchronizer
    model_class = models.ResourceRoleDepartmentTracker
    fixture = fixtures.API_RESOURCE_ROLE_DEPARTMENT
    update_field = 'active'

    def setUp(self):
        super().setUp()
        fixture_utils.init_departments()
        fixture_utils.init_roles()
        fixture_utils.init_resources()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_resource_role_departments_call(
            return_data)

    def _assert_fields(self, instance, json_data):
        self.assertEqual(instance.id, json_data['id'])
        self.assertEqual(instance.active, json_data['isActive'])
        self.assertEqual(instance.default, json_data['isDefault'])
        self.assertEqual(instance.resource.id, json_data['resourceID'])
        self.assertEqual(instance.role.id, json_data['roleID'])
        self.assertEqual(instance.department.id, json_data['departmentID'])
        self.assertEqual(instance.department_lead,
                         json_data['isDepartmentLead'])


class TestResourceServiceDeskRoleSynchronizer(SynchronizerTestMixin,
                                              TestCase):
    synchronizer_class = sync.ResourceServiceDeskRoleSynchronizer
    model_class = models.ResourceServiceDeskRoleTracker
    fixture = fixtures.API_RESOURCE_SERVICE_DESK_ROLE
    update_field = 'active'

    def setUp(self):
        super().setUp()
        fixture_utils.init_roles()
        fixture_utils.init_resources()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_resource_service_desk_roles_call(
            return_data)

    def _assert_fields(self, instance, json_data):
        self.assertEqual(instance.id, json_data['id'])
        self.assertEqual(instance.active, json_data['isActive'])
        self.assertEqual(instance.default, json_data['isDefault'])
        self.assertEqual(instance.resource.id, json_data['resourceID'])
        self.assertEqual(instance.role.id, json_data['roleID'])


class TestContractSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ContractSynchronizer
    model_class = models.ContractTracker
    fixture = fixtures.API_CONTRACT
    update_field = 'name'

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_contracts_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.name, object_data['contractName'])
        self.assertEqual(instance.number, object_data['contractNumber'])
        self.assertEqual(instance.status, str(object_data['status']))
        self.assertEqual(instance.account.id, object_data['companyID'])
        self.assertEqual(instance.contract_exclusion_set_id,
                         object_data['contractExclusionSetID'])


class TestContractExclusionSetSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ContractExclusionSetSynchronizer
    model_class = models.ContractExclusionSetTracker
    fixture = fixtures.API_CONTRACT_EXCLUSION_SET
    update_field = 'name'

    def setUp(self):
        super().setUp()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_contract_exclusion_sets_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.is_active, object_data['isActive'])
        self.assertEqual(instance.name, object_data['name'])


class TestContractExclusionRoleSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ContractExcludedRoleSynchronizer
    model_class = models.ContractExcludedRoleTracker
    fixture = fixtures.API_CONTRACT_EXCLUSION_ROLE
    update_field = 'excluded_role_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_roles()
        fixture_utils.init_contract_exclusion_sets()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_contract_excluded_roles_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.contract_exclusion_set.id,
                         object_data['contractExclusionSetID'])
        self.assertEqual(instance.excluded_role.id,
                         object_data['excludedRoleID'])


class TestContractExclusionWorkTypeSynchronizer(SynchronizerTestMixin,
                                                TestCase):
    synchronizer_class = sync.ContractExcludedWorkTypeSynchronizer
    model_class = models.ContractExcludedWorkTypeTracker
    fixture = fixtures.API_CONTRACT_EXCLUSION_WORK_TYPE
    update_field = 'excluded_work_type_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_billing_codes()
        fixture_utils.init_contract_exclusion_sets()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_contract_excluded_work_types_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.contract_exclusion_set.id,
                         object_data['contractExclusionSetID'])
        self.assertEqual(instance.excluded_work_type.id,
                         object_data['excludedWorkTypeID'])


class TestCompanyAlertsSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.CompanyAlertSynchronizer
    model_class = models.CompanyAlertTracker
    fixture = fixtures.API_COMPANY_ALERTS
    update_field = 'alert_text'

    def setUp(self):
        super().setUp()
        fixture_utils.init_accounts()
        fixture_utils.init_company_alerts()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_company_alerts_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.alert_text, object_data['alertText'])
        self.assertEqual(instance.alert_type, object_data['alertTypeID'])
        self.assertEqual(instance.account.id, object_data['companyID'])


class TestServiceCallSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ServiceCallSynchronizer
    model_class = models.ServiceCallTracker
    fixture = fixtures.API_SERVICE_CALL
    update_field = 'description'

    def setUp(self):
        super().setUp()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_resources()
        fixture_utils.init_account_types()
        fixture_utils.init_accounts()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_service_calls_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.description, object_data['description'])
        self.assertEqual(instance.duration, object_data['duration'])
        self.assertEqual(instance.complete, object_data['isComplete'])
        self.assertEqual(
            instance.create_date_time,
            self._parse_datetime(object_data['createDateTime'])
        )
        self.assertEqual(
            instance.start_date_time,
            self._parse_datetime(object_data['startDateTime'])
        )
        self.assertEqual(
            instance.end_date_time,
            self._parse_datetime(object_data['endDateTime'])
        )
        self.assertEqual(
            instance.canceled_date_time,
            self._parse_datetime(object_data['canceledDateTime'])
        )
        self.assertEqual(
            instance.last_modified_date_time,
            self._parse_datetime(object_data['lastModifiedDateTime'])
        )
        self.assertEqual(instance.status.id, object_data['status'])
        self.assertEqual(instance.account.id, object_data['companyID'])
        self.assertEqual(
            instance.creator_resource.id, object_data['creatorResourceID'])
        self.assertEqual(
            instance.canceled_by_resource.id,
            object_data['canceledByResourceID']
        )


class TestServiceCallTicketSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ServiceCallTicketSynchronizer
    model_class = models.ServiceCallTicketTracker
    fixture = fixtures.API_SERVICE_CALL_TICKET
    update_field = 'ticket_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_service_call_tickets_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.service_call.id,
                         object_data['serviceCallID'])
        self.assertEqual(instance.ticket.id, object_data['ticketID'])

    def test_sync_update(self):
        ticket = models.Ticket.objects.first()
        extra_ticket = deepcopy(ticket)
        extra_ticket.id = extra_ticket.id + 1
        extra_ticket.save()
        super().test_sync_update()


class TestServiceCallTaskSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.ServiceCallTaskSynchronizer
    model_class = models.ServiceCallTaskTracker
    fixture = fixtures.API_SERVICE_CALL_TASK
    update_field = 'task_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_service_call_statuses()
        fixture_utils.init_accounts()
        fixture_utils.init_service_calls()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_service_call_tasks_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.service_call.id,
                         object_data['serviceCallID'])
        self.assertEqual(instance.task.id, object_data['taskID'])

    def test_sync_update(self):
        task = models.Task.objects.first()
        extra_task = deepcopy(task)
        extra_task.id = extra_task.id + 1
        extra_task.save()
        super().test_sync_update()


class TestServiceCallTicketResourceSynchronizer(SynchronizerTestMixin,
                                                TestCase):
    synchronizer_class = sync.ServiceCallTicketResourceSynchronizer
    model_class = models.ServiceCallTicketResourceTracker
    fixture = fixtures.API_SERVICE_CALL_TICKET_RESOURCE
    update_field = 'resource_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_tickets()
        fixture_utils.init_resources()
        fixture_utils.init_service_call_tickets()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_service_call_ticket_resources_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.service_call_ticket.id,
                         object_data['serviceCallTicketID'])
        self.assertEqual(instance.resource.id, object_data['resourceID'])


class TestServiceCallTaskResourceSynchronizer(SynchronizerTestMixin,
                                              TestCase):
    synchronizer_class = sync.ServiceCallTaskResourceSynchronizer
    model_class = models.ServiceCallTaskResourceTracker
    fixture = fixtures.API_SERVICE_CALL_TASK_RESOURCE
    update_field = 'resource_id'

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()
        fixture_utils.init_resources()
        fixture_utils.init_service_call_tasks()
        self._sync(self.fixture)

    def _call_api(self, return_data):
        return mocks.service_api_get_service_call_task_resources_call(
            return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.service_call_task.id,
                         object_data['serviceCallTaskID'])
        self.assertEqual(instance.resource.id, object_data['resourceID'])


class TestTaskPredecessorSynchronizer(SynchronizerTestMixin, TestCase):
    synchronizer_class = sync.TaskPredecessorSynchronizer
    model_class = models.TaskPredecessorTracker
    fixture = fixtures.API_TASK_PREDECESSOR
    update_field = 'lag_days'

    def setUp(self):
        super().setUp()
        fixture_utils.init_projects()
        fixture_utils.init_tasks()

        project = models.Project.objects.first()
        models.Task.objects.create(
            id=fixtures.API_TASK_PREDECESSOR_ITEMS[0]['successorTaskID'],
            title='Successor Task', project=project)
        fixture_utils.init_task_predecessors()

    def _call_api(self, return_data):
        return mocks.service_api_get_task_predecessors_call(return_data)

    def _assert_fields(self, instance, object_data):
        self.assertEqual(instance.id, object_data['id'])
        self.assertEqual(instance.lag_days, object_data['lagDays'])
        self.assertEqual(instance.predecessor_task.id,
                         object_data['predecessorTaskID'])
        self.assertEqual(instance.successor_task.id,
                         object_data['successorTaskID'])
