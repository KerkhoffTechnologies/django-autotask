
API_SECONDARY_RESOURCE_LIST = [
    {
        'id': 29684157,
        'UserDefinedFields': '',
        'TicketID': 7688,
        'ResourceID': 29683794,
        'RoleID': 29683394
    },
    {
        'id': 29684156,
        'UserDefinedFields': '',
        'TicketID': 7731,
        'ResourceID': 29683915,
        'RoleID': 29683395
    }
]

API_RESOURCE = {
    'AccountingReferenceID': '',
    'Active': True,
    'DateFormat': 'MM/dd/yyyy',
    'Email': '',
    'Email2': '',
    'Email3': '',
    'EmailTypeCode': 'PRIMARY',
    'FirstName': 'Autotask',
    'HireDate': '',
    'HomePhone': '',
    'Initials': '',
    'InternalCost': 1.0,
    'LastName': 'Administrator',
    'LicenseType': 1,
    'LocationID': 90682,
    'MiddleName': '',
    'MobilePhone': '',
    'NumberFormat': 'X,XXX.XX',
    'OfficeExtension': '',
    'OfficePhone': '(518) 720-3500',
    'Password': '******',
    'PayrollType': 1,
    'ResourceType': 'Employee',
    'TimeFormat': 'hh:mm a',
    'Title': '',
    'UserDefinedFields': '',
    'UserName': 'administrator',
    'UserType': 10,
    'id': 29683794,
}

API_RESOURCE_LIST = [API_RESOURCE]

API_QUEUE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Client Portal',
        'SortOrder': 0,
        'Value': 5,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Post Sale',
        'SortOrder': 1,
        'Value': 6,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Monitoring Alert',
        'SortOrder': 2,
        'Value': 8,
        'ParentValue': None,
    },
]


API_TICKET_PRIORITY_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'High',
        'SortOrder': 2,
        'Value': 1,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Medium',
        'SortOrder': 3,
        'Value': 2,
        'ParentValue': None,
    }
]


API_TICKET_STATUS_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Waiting Materials',
        'SortOrder': 6,
        'Value': 9,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Scheduled',
        'SortOrder': 3,
        'Value': 10,
        'ParentValue': None
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Escalate',
        'SortOrder': 5,
        'Value': 11,
        'ParentValue': None
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Waiting Vendor',
        'SortOrder': 8,
        'Value': 12,
        'ParentValue': None
    }
]

API_SERVICE_TICKET = {
    'AccountID': 29683561,
    'AllocationCodeID': 29683407,
    'AssignedResourceID': 29683794,
    'AssignedResourceRoleID': 29683396,
    'ChangeInfoField1': '',
    'ChangeInfoField2': '',
    'ChangeInfoField3': '',
    'ChangeInfoField4': '',
    'ChangeInfoField5': '',
    'CompletedByResourceID': 29682885,
    'CompletedDate': '2019-09-05T13:08:23.450+01:00',
    'ContactID': 29683586,
    'CreateDate': '2012-06-18T13:08:23.450+01:00',
    'CreatorResourceID': 4,
    'CreatorType': 1,
    'Description': 'Monthy Services Checkup',
    'DueDateTime': '2012-10-15T17:00:00+01:00',
    'EstimatedHours': 2.0,
    'ExternalID': '',
    'FirstResponseDateTime': '2012-06-18T13:08:23.683+01:00',
    'HoursToBeScheduled': 0.0,
    'IssueType': 10,
    'LastActivityDate': '2012-09-24T17:00:25.823+01:00',
    'LastActivityPersonType': 1,
    'LastActivityResourceID': 4,
    'Priority': 3,
    'PurchaseOrderNumber': '',
    'QueueID': 29682833,
    'Resolution': '',
    'Source': 6,
    'Status': 10,
    'SubIssueType': 136,
    'TicketCategory': 3,
    'TicketNumber': 'T20120604.0002.005',
    'TicketType': 1,
    'Title': 'Monthy Services Checkup*',
    'UserDefinedFields': '',
    'id': 7688
}

API_SERVICE_TICKET_LIST = [API_SERVICE_TICKET]
