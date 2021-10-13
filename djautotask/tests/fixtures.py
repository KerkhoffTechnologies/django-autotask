from datetime import datetime
from dateutil.tz import tzoffset


API_PAGE_DETAILS = {
        "count": 1,
        "requestCount": 500,
        "prevPageUrl": None,
        "nextPageUrl": None
    }

API_EMPTY = {
    "items": [],
    "pageDetails": {
        "count": 0,
        "requestCount": 500,
        "prevPageUrl": None,
        "nextPageUrl": None
    }
}

API_ACCOUNT_LIST = [
    {
        'id': 174,
        'UserDefinedFields': '',
        'Address1': '26 Tech Valley Drive',
        'Address2': 'Suite 2',
        'AlternatePhone1': '',
        'AlternatePhone2': '',
        'City': 'East Greenbush',
        'Country': 'United States',
        'CreateDate':
            datetime(2012, 10, 24, 5, 0, tzinfo=tzoffset(None, 3600)),
        'Fax': '555-555-6677',
        'LastActivityDate':
            datetime(2012, 6, 18, 13, 15, 47, tzinfo=tzoffset(None, 3600)),
        'MarketSegmentID': 29683456,
        'AccountName': 'Autotask Corporation',
        'AccountNumber': "289843",
        'OwnerResourceID': 29682885,
        'Phone': '555-555-5566',
        'PostalCode': 12061,
        'SICCode': '',
        'State': 'NY',
        'StockMarket': '',
        'StockSymbol': '',
        'TerritoryID': 29683453,
        'AccountType': 7,
        'WebAddress': 'www.autotask.com',
        'Active': True,
        'ClientPortalActive': True,
        'TaskFireActive': False,
        'TaxExempt': False,
        'TaxID': '',
        'AdditionalAddressInformation': '',
        'CountryID': 237,
        'BillToAddressToUse': 1,
        'BillToAttention': '',
        'BillToAddress1': '26 Tech Valley Drive',
        'BillToAddress2': 'Suite 2',
        'BillToCity': 'East Greenbush',
        'BillToState': 'NY',
        'BillToZipCode': 12061,
        'BillToCountryID': 237,
        'BillToAdditionalAddressInformation': '',
        'QuoteTemplateID': 1,
        'QuoteEmailMessageID': 2,
        'InvoiceTemplateID': 102,
        'InvoiceEmailMessageID': 1,
        'CurrencyID': 1,
        'CreatedByResourceID': 29682885,
    }
]

API_ACCOUNT_PHYSICAL_LOCATION_ITEMS = [
    {
        'id': 55,
        'name': 'Primary Location',
        'companyID': 174,
        'isActive': True,
        'isPrimary': True
    }
]
API_ACCOUNT_PHYSICAL_LOCATION = {
    "items": API_ACCOUNT_PHYSICAL_LOCATION_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_PROJECT_ITEM = {
        'id': 4,
        'projectName': 'Software Project',
        'companyID': 174,
        'projectType': 5,
        'extProjectNumber': '',
        'projectNumber': 'P20120604.0001',
        'description': '',
        'department': 29683384,
        'contractID': 29684183,
        'createDateTime': '2012-06-18T06:00:00.000Z',
        'creatorResourceID': 4,
        'startDateTime': '2012-06-19T06:00:00.000Z',
        'endDateTime': '2012-10-24T06:00:00.000Z',
        'duration': 59,
        'actualHours': 0.0,
        'actualBilledHours': 0.0,
        'estimatedTime': 164.0,
        'laborEstimatedRevenue': 0.0,
        'laborEstimatedCosts': 0.0,
        'laborEstimatedMarginPercentage': 0.0,
        'projectCostsRevenue': 0.0,
        'projectCostsBudget': 0.0,
        'projectCostEstimatedMarginPercentage': 0.0,
        'changeOrdersRevenue': 0.0,
        'sgda': 0.0,
        'originalEstimatedRevenue': 0.0,
        'estimatedSalesCost': 0.0,
        'status': 1,
        'projectLeadResourceID': 29683794,
        'completedPercentage': 0,
        'completedDateTime': '2019-09-18T06:00:00.000Z',
        'statusDetail': '',
        'statusDateTime': '2012-06-18T06:00:00.000Z',
        'LineOfBusiness': 6,
        'purchaseOrderNumber': '',
        'businessDivisionSubdivisionID': 6,
        'lastActivityResourceID': 4,
        'lastActivityDateTime': '2012-06-18T02:00:00.000Z',
        'lastActivityPersonType': 1,
        'userDefinedFields': {},
    }
API_PROJECT_ITEMS = [API_PROJECT_ITEM]
API_PROJECT_BY_ID = {
    "item": API_PROJECT_ITEM
}
API_PROJECT = {
    "items": API_PROJECT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_LICENSE_TYPE_FIELD = {
    "fields": [
        {
            "name": "licenseType",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": True,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "1",
                    "label": "Administrator",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

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

API_SOURCE_FIELD = {
    "fields": [
        {
            "name": "source",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "2",
                    "label": "Insourced",
                    "isDefaultValue": False,
                    "sortOrder": 8,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_ISSUE_TYPE_FIELD = {
    "fields": [
        {
            "name": "issueType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "2",
                    "label": "Hardware",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_SUB_ISSUE_TYPE_FIELD = {
    "fields": [
        {
            "name": "subIssueType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': False,
                    'label': 'Rapid Response',
                    'sortOrder': 5,
                    'value': 2,
                    'parentValue': None,
                },
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': False,
                    'label': 'Hardware Request',
                    'sortOrder': 7,
                    'value': 3,
                    'parentValue': None,
                },
            ],
            "picklistParentValueField": "IssueType",
            "isSupportedWebhookField": False
        }
    ]
}

API_TICKET_TYPE_FIELD = {
    "fields": [
        {
            "name": "ticketType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': False,
                    'label': 'Service Request',
                    'sortOrder': 5,
                    'value': 3,
                    'parentValue': None,
                },
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': False,
                    'label': 'Incident',
                    'sortOrder': 6,
                    'value': 2,
                    'parentValue': None,
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_SERVICE_CALL_STATUS_FIELD = {
    "fields": [
        {
            "name": "status",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "3",
                    "label": "New",
                    "isDefaultValue": False,
                    "sortOrder": 5,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
                {
                    "value": "2",
                    "label": "Complete",
                    "isDefaultValue": False,
                    "sortOrder": 6,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_QUEUE_FIELD = {
    "fields": [
        {
            "name": "queueID",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "5",
                    "label": "Client Portal",
                    "isDefaultValue": False,
                    "sortOrder": 0,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_PRIORITY_FIELD = {
    "fields": [
        {
            "name": "priority",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "1",
                    "label": "High",
                    "isDefaultValue": False,
                    "sortOrder": 2,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_STATUS_FIELD = {
    "fields": [
        {
            "name": "status",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "9",
                    "label": "Waiting Materials",
                    "isDefaultValue": False,
                    "sortOrder": 6,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
                {
                    "value": "10",
                    "label": "Scheduled",
                    "isDefaultValue": False,
                    "sortOrder": 3,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
                {
                    "value": "11",
                    "label": "Escalate",
                    "isDefaultValue": False,
                    "sortOrder": 5,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
                {
                    "value": "12",
                    "label": "Waiting Vendor",
                    "isDefaultValue": False,
                    "sortOrder": 8,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        },
        {
            "name": "priority",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "1",
                    "label": "High",
                    "isDefaultValue": False,
                    "sortOrder": 2,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        },
        {
            "name": "queueID",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "5",
                    "label": "Client Portal",
                    "isDefaultValue": False,
                    "sortOrder": 0,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        },
        {
            "name": "issueType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "2",
                    "label": "Hardware",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        },
        {
            "name": "source",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "2",
                    "label": "Insourced",
                    "isDefaultValue": False,
                    "sortOrder": 8,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_TICKET_PICKLIST_FIELD = {
    "fields":
        API_STATUS_FIELD['fields']
        + API_PRIORITY_FIELD['fields']
        + API_QUEUE_FIELD['fields']
        + API_ISSUE_TYPE_FIELD['fields']
        + API_SUB_ISSUE_TYPE_FIELD['fields']
        + API_TICKET_TYPE_FIELD['fields']
        + API_SOURCE_FIELD['fields']
}

API_TICKET_CATEGORY_ITEMS = [
    {
        'id': 5,
        'name': 'Standard (non-editable)',
        'nickname': '',
        'isActive': False,
        'displayColorRGB': 19,
        'isGlobalDefault': False,
        'isApiOnly': False
    },
]
API_TICKET_CATEGORY = {
    "items": API_TICKET_CATEGORY_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_PROJECT_STATUS_FIELD = {
    "fields": [
        {
            "name": "status",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': True,
                    'label': 'Inactive',
                    'sortOrder': 1,
                    'value': 2,
                    'parentValue': None,
                },
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': True,
                    'label': 'New',
                    'sortOrder': 2,
                    'value': 1,
                    'parentValue': None,
                },
                {
                    'isActive': False,
                    'isDefaultValue': False,
                    'isSystem': True,
                    'label': 'Complete',
                    'sortOrder': 8,
                    'value': 5,
                    'parentValue': None,
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_PROJECT_TYPE_FIELD = {
    "fields": [
        {
            "name": "projectType",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': True,
                    'label': 'Client',
                    'sortOrder': 5,
                    'value': 5,
                    'parentValue': None,
                },
                {
                    'isActive': True,
                    'isDefaultValue': False,
                    'isSystem': True,
                    'label': 'Internal',
                    'sortOrder': 4,
                    'value': 4,
                    'parentValue': None,
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_PROJECT_PICKLIST_FIELD = {
    "fields":
        API_PROJECT_STATUS_FIELD['fields']
        + API_PROJECT_TYPE_FIELD['fields']
}

API_DISPLAY_COLOR_FIELD = {
    "fields": [
        {
            "name": "displayColorRgb",
            "dataType": "integer",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "19",
                    "label": "#ff6666",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": False
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_ACCOUNT_TYPE_FIELD = {
    "fields": [
        {
            "name": "companyType",
            "dataType": "short",
            "length": 0,
            "isRequired": True,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "3",
                    "label": "Customer",
                    "isDefaultValue": False,
                    "sortOrder": 5,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_PHASE = {
    'EstimatedHours': 23.0,
    'StartDate': datetime(2012, 8, 27, 5, 0, tzinfo=tzoffset(None, 3600)),
    'PhaseNumber': 'T20120604.0011',
    'ProjectID': 4,
    'UserDefinedFields': '',
    'Scheduled': False,
    'DueDate': datetime(2012, 9, 17, 5, 0, tzinfo=tzoffset(None, 3600)),
    'id': 7732,
    'Description': 'Unit Testing',
    'CreateDate': datetime(2012, 6, 18, 17, 50, 31, tzinfo=tzoffset(None, 3600)),
    'LastActivityDateTime': datetime(2019, 11, 5, 0, 28, 25, 490000, tzinfo=tzoffset(None, 3600)),
    'ExternalID': None,
    'Title': 'Unit Testing',
    'CreatorResourceID': 4
}

API_PHASE_LIST = [API_PHASE]

API_TASK_ITEM = {
    'id': 7733,
    'allocationCodeID': 29683415,
    'assignedResourceID': 29683794,
    'assignedResourceRoleID': 29682834,
    'canClientPortalUserCompleteTask': False,
    'createDateTime': '2018-01-20T12:00:00.000Z',
    'creatorResourceID': 4,
    'completedDateTime': None,
    'departmentID': 29683385,
    'description': 'Review modular code',
    'endDateTime': '2019-09-23T12:00:00.000Z',
    'estimatedHours': 5.0,
    'externalID': None,
    'hoursToBeScheduled': 5.0,
    'isVisibleInClientPortal': True,
    'lastActivityDateTime': '2019-10-06T12:00:00.000Z',
    'phaseID': 7732,
    'priority': 0,
    'priorityLabel': 1,
    'projectID': 4,
    'purchaseOrderNumber': None,
    'remainingHours': 5.0,
    'startDateTime': '2018-01-23T12:00:00.000Z',
    'status': 11,
    'taskIsBillable': False,
    'taskNumber': 'T20120604.0012',
    'taskType': 1,
    'title': 'Review modular code',
    'creatorType': 1,
    'lastActivityResourceID': 29683968,
    'lastActivityPersonType': 1,
    'userDefinedFields': {}
}
API_TASK_ITEMS = [API_TASK_ITEM]
API_TASK_BY_ID = {
    "item": API_TASK_ITEM
}
API_TASK = {
    "items": API_TASK_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TICKET_SECONDARY_RESOURCE_ITEMS = [
    {
        'id': 29684157,
        'ticketID': 7688,
        'resourceID': 29683794,
        'roleID': 29683396
    },
]
API_TICKET_SECONDARY_RESOURCE = {
    "items": API_TICKET_SECONDARY_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TASK_SECONDARY_RESOURCE_ITEMS = [
    {
        'id': 29684411,
        'taskID': 7733,
        'resourceID': 29683794,
        'roleID': 29683396,
    }
]
API_TASK_SECONDARY_RESOURCE = {
    "items": API_TASK_SECONDARY_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TICKET_NOTE_ITEMS = [
    {
        'id': 45,
        'createDateTime': '2018-01-23T11:00:00.00Z',
        'description': "Note description",
        'creatorResourceID': 29683794,
        'lastActivityDate': '2018-01-23T11:00:00.00Z',
        'noteType': 2,
        'publish': 1,
        'ticketID': 7688,
        'title': "Note Title",
    }
]
API_TICKET_NOTE = {
    "items": API_TICKET_NOTE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TASK_NOTE_ITEMS = [
    {
        'id': 45,
        'createDateTime': '2018-01-23T11:00:00.00Z',
        'description': "Note description",
        'creatorResourceID': 29683794,
        'lastActivityDate': '2018-01-23T11:00:00.00Z',
        'noteType': 2,
        'publish': 1,
        'taskID': 7733,
        'title': "Note Title",
    }
]
API_TASK_NOTE = {
    "items": API_TASK_NOTE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_NOTE_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Task Detail',
        'SortOrder': 1,
        'Value': 2,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Client Portal Note',
        'SortOrder': 1,
        'Value': 18,
        'ParentValue': None,
    },
]

API_TASK_TYPE_LINK_FIELD = {
    "fields": [
        {
            "name": "timeEntryType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": True,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "19",
                    "label": "ITServiceRequest",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_TIME_ENTRY_TICKET = {
    'id': 4,
    'ticketID': 7688,
    'taskID': None,
    'internalBillingCodeID': 29683403,
    'timeEntryType': 2,
    'dateWorked': '2018-01-23T00:00:00.00Z',
    'startDateTime': '2018-01-23T10:00:00.00Z',
    'endDateTime': '2018-01-23T12:30:00.00Z',
    'hoursWorked': 1.0000,
    'hoursToBill': 1.0000,
    'offsetHours': 0.0000,
    'summaryNotes': 'Initial triage of issue',
    'internalNotes': 'We will need to get more information',
    'roleID': 29683396,
    'createDateTime': '2018-01-23T09:50:00.00Z',
    'resourceID': 28,
    'creatorUserID': 29683794,
    'lastModifiedUserID': 29683794,
    'lastModifiedDateTime': '2018-01-23T13:00:00.00Z',
    'billingCodeID': 29683403,
    'contractID': 29684054,
    'showOnInvoice': True,
    'isNonBillable': False,
    'billingApprovalLevelMostRecent': 0,
}

API_TIME_ENTRY_TASK = {
    'id': 5,
    'ticketID': None,
    'taskID': 7733,
    'internalBillingCodeID': 29683403,
    'timeEntryType': 10,
    'dateWorked': '2018-01-23T00:00:00.00Z',
    'startDateTime': '2018-01-23T10:00:00.00Z',
    'endDateTime': '2018-01-23T12:30:00.00Z',
    'hoursWorked': 1.0000,
    'hoursToBill': 1.0000,
    'offsetHours': 0.0000,
    'summaryNotes': 'Entering time for task',
    'internalNotes': 'We will need to get more information',
    'roleID': 29683396,
    'createDateTime': '2018-01-23T09:50:00.00Z',
    'resourceID': 28,
    'creatorUserID': 29683794,
    'lastModifiedUserID': 29683794,
    'lastModifiedDateTime': '2018-01-23T13:00:00.00Z',
    'billingCodeID': 29683403,
    'contractID': 29684054,
    'showOnInvoice': True,
    'isNonBillable': False,
    'billingApprovalLevelMostRecent': 0,
}
API_TIME_ENTRY_ITEMS = [API_TIME_ENTRY_TICKET, API_TIME_ENTRY_TASK]
API_TIME_ENTRY = {
    "items": API_TIME_ENTRY_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}


API_USE_TYPE_FIELD = {
    "fields": [
        {
            "name": "useType",
            "dataType": "integer",
            "length": 0,
            "isRequired": False,
            "isReadOnly": False,
            "isQueryable": True,
            "isReference": False,
            "referenceEntityType": "",
            "isPickList": True,
            "picklistValues": [
                {
                    "value": "2",
                    "label": "General Allocation Code",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                }
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
}

API_ALLOCATION_CODE_ITEMS = [
    {
        'id': 2,
        'name': 'Finance',
        'useType': 2,
        'isActive': True,
        'unitCost': 0.0000,
        'unitPrice': 0.0000,
        'externalNumber': 0,
        'isExcludedFromNewContracts': False,
    }
]
API_ALLOCATION_CODE = {
    "items": API_ALLOCATION_CODE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_ROLE_ITEM = {
    'id': 29683396,
    'name': "IT:Technician I",
    'description': "",
    'isActive': True,
    'hourlyFactor': 1,
    'hourlyRate': 100,
    'roleType': 0,
    'isSystemRole': False,
    }
API_ROLE_ITEMS = [API_ROLE_ITEM]
API_ROLE = {
    "items": API_ROLE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_DEPARTMENT_ITEM = {
    'id': 29683384,
    'name': "Finance",
    'description': "Finance Dept",
    'number': "",
    }
API_DEPARTMENT_ITEMS = [API_DEPARTMENT_ITEM]
API_DEPARTMENT = {
    "items": API_DEPARTMENT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_RESOURCE_ROLE_DEPARTMENT_ITEM = {
    "id": 32,
    "departmentID": 29683384,
    "isActive": True,
    "isDefault": True,
    "isDepartmentLead": True,
    "resourceID": 29683794,
    "roleID": 29683396,
}
API_RESOURCE_ROLE_DEPARTMENT_ITEMS = [API_RESOURCE_ROLE_DEPARTMENT_ITEM]
API_RESOURCE_ROLE_DEPARTMENT = {
    "items": API_RESOURCE_ROLE_DEPARTMENT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_RESOURCE_SERVICE_DESK_ROLE_ITEM = {
    "id": 32,
    "isActive": True,
    "isDefault": True,
    "resourceID": 29683794,
    "roleID": 29683396,
}
API_RESOURCE_SERVICE_DESK_ROLE_ITEMS = [API_RESOURCE_SERVICE_DESK_ROLE_ITEM]
API_RESOURCE_SERVICE_DESK_ROLE = {
    "items": API_RESOURCE_SERVICE_DESK_ROLE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_CONTRACT_ITEMS = [
    {
        'id': 29684183,
        'userDefinedFields': "",
        'companyID': 174,
        'billingPreference': 2,
        'contractCategory': 15,
        'contractName': "Upstate Document Providers - Hosted SaaS",
        'contractNumber': "2343451",
        'contractPeriodType': "m",
        'contractType': 7,
        'isDefaultContract': True,
        'endDate': '2020-02-23T13:00:00Z',
        'estimatedCost': 0.0000,
        'estimatedHours': 0.0000,
        'estimatedRevenue': 5795.00,
        'setupFee': 995.0000,
        'startDate': '2020-02-23T13:00:00Z',
        'status': 1,
        'timeReportingRequiresStartAndStopTimes': 1,
        'serviceLevelAgreementID': 1,
        'purchaseOrderNumber': "",
        'internalCurrencySetupFee': 995.0000,
    }
]
API_CONTRACT = {
    "items": API_CONTRACT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_SERVICE_CALL_ITEMS = [
    {
        'id': 2,
        'description': 'Email just in, printer is down.',
        'isComplete': 0,
        'duration': 1.0000,
        'createDateTime': '2020-01-22T13:00:00Z',
        'startDateTime': '2020-02-23T13:00:00Z',
        'endDateTime': '2020-03-23T13:00:00Z',
        'canceledDateTime': None,
        'lastModifiedDateTime': None,
        'companyID': 174,
        'status': 2,
        'creatorResourceID': 29683794,
        'canceledByResourceID': 29683794,
    }
]
API_SERVICE_CALL = {
    "items": API_SERVICE_CALL_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_SERVICE_CALL_TICKET_ITEMS = [
    {
        'id': 4,
        'serviceCallID': 2,
        'ticketID': 7688,
    }
]
API_SERVICE_CALL_TICKET = {
    "items": API_SERVICE_CALL_TICKET_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_SERVICE_CALL_TASK_ITEMS = [
    {
        'id': 4,
        'serviceCallID': 2,
        'taskID': 7733,
    }
]
API_SERVICE_CALL_TASK = {
    "items": API_SERVICE_CALL_TASK_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_SERVICE_CALL_TICKET_RESOURCE_ITEMS = [
    {
        'id': 4,
        'serviceCallTicketID': 4,
        'resourceID': 29683794,
    }
]
API_SERVICE_CALL_TICKET_RESOURCE = {
    "items": API_SERVICE_CALL_TICKET_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_SERVICE_CALL_TASK_RESOURCE_ITEMS = [
    {
        'id': 4,
        'serviceCallTaskID': 4,
        'resourceID': 29683794,
    }
]
API_SERVICE_CALL_TASK_RESOURCE = {
    "items": API_SERVICE_CALL_TASK_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TASK_PREDECESSOR_ITEMS = [
    {
        'id': 1,
        'lagDays': 0,
        'predecessorTaskID': API_TASK_ITEM['id'],
        'successorTaskID': 7755,
    }
]
API_TASK_PREDECESSOR = {
    "items": API_TASK_PREDECESSOR_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_UDF_LIST = [
    {
        'Name': "Test UDF",
        'Label': "Test UDF",
        'Type': "String",
        'Length': 8000,
        'IsPickList': False,
    },
    {
        'Name': "Test UDF",
        'Label': "Test UDF",
        'Type': "String",
        'Length': 8000,
        'IsPickList': True,
        'PicklistValues': [
            {
                 'Value': "1",
                 'Label': "One",
                 'IsDefaultValue': False,
                 'SortOrder': 0,
                 'parentValue': None,
                 'IsActive': True,
                 'IsSystem': False
            }
        ]
    },

]

API_CONTACT_ITEMS = [
    {
        "id": 29683589,
        "companyID": 174,
        "emailAddress": "brobertson@autotaskdemo.com",
        "emailAddress2": "brobertson2@autotaskdemo.com",
        "emailAddress3": "brobertson3@autotaskdemo.com",
        "firstName": "Mary",
        "isActive": 1,
        "lastActivityDate": "2012-05-25T15:14:29.033Z",
        "lastModifiedDate": "2015-06-10T13:22:29.877Z",
        "lastName": "Smith",
        "phone": "551-555-5513",
        "alternatePhone": "551-555-5522",
        "mobilePhone": "551-555-3502",
    }
]
API_CONTACT = {
    "items": API_CONTACT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TICKET_ITEM = {
        'companyID': 174,
        'companyLocationID': 55,
        'billingCodeID': 29683407,
        'assignedResourceID': 29683794,
        'assignedResourceRoleID': 29683396,
        'changeInfoField1': '',
        'changeInfoField2': '',
        'changeInfoField3': '',
        'changeInfoField4': '',
        'changeInfoField5': '',
        'completedByResourceID': 29682885,
        'completedDate': '2019-09-05T08:23:00.000Z',
        'contactID': 29683586,
        'contractID': 29684183,
        'createDate': '2019-08-18T01:00:00.000Z',
        'creatorResourceID': 4,
        'creatorType': 1,
        'description': 'Monthy Services Checkup',
        'dueDateTime': '2012-09-07T01:00:00.000Z',
        'estimatedHours': 2.0,
        'externalID': '',
        'firstResponseDateTime': '2012-06-18T01:00:00.000Z',
        'hoursToBeScheduled': 0.0,
        'issueType': 10,
        'lastActivityDate': '2019-09-23T11:00:00.000Z',
        'lastActivityPersonType': 1,
        'lastActivityResourceID': 4,
        'priority': 3,
        'purchaseOrderNumber': '',
        'queueID': 29682833,
        'resolution': '',
        'source': 6,
        'status': 10,
        'subIssueType': 136,
        'ticketCategory': 3,
        'ticketNumber': 'T20120604.0002.005',
        'ticketType': 1,
        'title': 'Monthy Services Checkup*',
        'userDefinedFields': {},
        'id': 7688
    }
API_TICKET_ITEMS = [API_TICKET_ITEM]
API_TICKET_BY_ID = {
    "item": API_TICKET_ITEM
}
API_TICKET = {
    "items": API_TICKET_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}
