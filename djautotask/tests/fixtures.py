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

API_EMPTY_FIELDS = {"fields": []}

API_UDF = {
    "fields": [
        {
            'name': "Test UDF",
            'label': "Test UDF",
            'type': "string",
            'length': 8000,
            'isPickList': True,
            'picklistValues': [
                {
                    'value': "1",
                    'label': "One",
                    'isDefaultValue': False,
                    'sortOrder': 0,
                    'parentValue': None,
                    'isActive': True,
                    'isSystem': False
                }
            ]
        },
    ],
}

API_ACCOUNT_ITEMS = [
    {
        'id': 174,
        'userDefinedFields': [],
        'address1': '26 Tech Valley Drive',
        'address2': 'Suite 2',
        'alternatePhone1': '',
        'alternatePhone2': '',
        'city': 'East Greenbush',
        'createDate': '2012-10-24T05:00:00.000Z',
        'fax': '555-555-6677',
        'lastActivityDate': '2012-06-18T13:15:47.000Z',
        'marketSegmentID': 29683456,
        'companyName': 'Autotask Corporation',
        'companyNumber': "289843",
        'ownerResourceID': 29682885,
        'phone': '555-555-5566',
        'postalCode': 12061,
        'sicCode': '',
        'state': 'NY',
        'stockMarket': '',
        'stockSymbol': '',
        'territoryID': 29683453,
        'companyType': 7,
        'webAddress': 'www.autotask.com',
        'isActive': True,
        'isClientPortalActive': True,
        'isTaskFireActive': False,
        'taxID': '',
        'additionalAddressInformation': '',
        'countryID': 237,
        'billToAddressToUse': 1,
        'billToAttention': '',
        'billToAddress1': '26 Tech Valley Drive',
        'billToAddress2': 'Suite 2',
        'billToCity': 'East Greenbush',
        'billToState': 'NY',
        'billToZipCode': 12061,
        'billToCountryID': 237,
        'billToAdditionalAddressInformation': '',
        'quoteTemplateID': 1,
        'quoteEmailMessageID': 2,
        'invoiceTemplateID': 102,
        'invoiceEmailMessageID': 1,
        'currencyID': 1,
        'createdByResourceID': 29682885,
    }
]
API_ACCOUNT = {
    "items": API_ACCOUNT_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

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
    'projectLeadResourceID': 10,
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

API_RESOURCE_ITEMS = [
    {
        'accountingReferenceID': '',
        'isActive': True,
        'dateFormat': 'MM/dd/yyyy',
        'email': '',
        'email2': '',
        'email3': '',
        'emailTypeCode': 'PRIMARY',
        'firstName': 'Autotask',
        'hireDate': '',
        'homePhone': '',
        'initials': '',
        'internalCost': 1.0,
        'lastName': 'Administrator',
        'licenseType': 1,
        'locationID': 90682,
        'middleName': '',
        'mobilePhone': '',
        'numberFormat': 'X,XXX.XX',
        'officeExtension': '',
        'officePhone': '(518) 720-3500',
        'payrollType': 1,
        'resourceType': 'Employee',
        'timeFormat': 'hh:mm a',
        'title': '',
        'userName': 'administrator',
        'userType': 10,
        'id': 10,
    }
]
API_RESOURCE = {
    "items": API_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

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

API_TASK_CATEGORY_FIELD = {
    "fields": [
        {
            "name": "taskCategoryID",
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
                    'value': 100,
                    'label': 'New category',
                    'isDefaultValue': False,
                    'sortOrder': 0,
                    'isActive': True,
                    'isSystem': False,
                    'parentValue': None,
                },
                {
                    'value': 2,
                    'label': 'Standard',
                    'isDefaultValue': True,
                    'sortOrder': 0,
                    'isActive': True,
                    'isSystem': True,
                    'parentValue': None,
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        }
    ]
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

API_PHASE_ITEMS = [
    {
        'estimatedHours': 23.0,
        'startDate': '2012-08-27T05:00:00.000Z',
        'phaseNumber': 'T20120604.0011',
        'projectID': 4,
        'dueDate': '2012-09-17T05:00:00.000Z',
        'id': 7732,
        'description': 'Unit Testing',
        'createDate': '2012-06-18T17:50:31.000Z',
        'lastActivityDateTime': '2019-11-05T00:28:25.000Z',
        'externalID': None,
        'title': 'Unit Testing',
        'creatorResourceID': 4
    }
]
API_PHASE = {
    "items": API_PHASE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TASK_ITEM = {
    'id': 101,
    'billingCodeID': 29683415,
    'assignedResourceID': 10,
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
    'taskCategoryID': 2,
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
        'ticketID': 100,
        'resourceID': 10,
        'roleID': 8
    },
]
API_TICKET_SECONDARY_RESOURCE = {
    "items": API_TICKET_SECONDARY_RESOURCE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_TASK_SECONDARY_RESOURCE_ITEMS = [
    {
        'id': 29684411,
        'taskID': 101,
        'resourceID': 10,
        'roleID': 8,
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
        'creatorResourceID': 10,
        'lastActivityDate': '2018-01-23T11:00:00.00Z',
        'noteType': 2,
        'publish': 1,
        'ticketID': 100,
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
        'creatorResourceID': 10,
        'lastActivityDate': '2018-01-23T11:00:00.00Z',
        'noteType': 2,
        'publish': 1,
        'taskID': 101,
        'title': "Note Title",
    }
]
API_TASK_NOTE = {
    "items": API_TASK_NOTE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_NOTE_TYPE_FIELD = {
    "fields": [
        {
            "name": "noteType",
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
                    "value": "2",
                    "label": "Task Detail",
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

API_PROJECT_NOTE_TYPE_FIELD = {
    "fields": [
        {
            "name": "noteType",
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
                    "value": "5",
                    "label": "Project Notes",
                    "isDefaultValue": False,
                    "sortOrder": 2,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                },
            ],
            "picklistParentValueField": "",
            "isSupportedWebhookField": False
        },
    ]
}

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

API_TIME_ENTRY_TICKET_ITEM = {
    'id': 4,
    'ticketID': 100,
    'taskID': None,
    'internalBillingCodeID': 3,
    'timeEntryType': 2,
    'dateWorked': '2018-01-23T00:00:00.00Z',
    'startDateTime': '2018-01-23T10:00:00.00Z',
    'endDateTime': '2018-01-23T12:30:00.00Z',
    'hoursWorked': 1.0000,
    'hoursToBill': 1.0000,
    'offsetHours': 0.0000,
    'summaryNotes': 'Initial triage of issue',
    'internalNotes': 'We will need to get more information',
    'roleID': 8,
    'createDateTime': '2018-01-23T09:50:00.00Z',
    'resourceID': 10,
    'creatorUserID': 10,
    'lastModifiedUserID': 10,
    'lastModifiedDateTime': '2018-01-23T13:00:00.00Z',
    'billingCodeID': 3,
    'contractID': 5,
    'showOnInvoice': True,
    'isNonBillable': False,
    'billingApprovalLevelMostRecent': 0,
}

API_TIME_ENTRY_TASK_ITEM = {
    'id': 5,
    'ticketID': None,
    'taskID': 101,
    'internalBillingCodeID': 3,
    'timeEntryType': 6,
    'dateWorked': '2018-01-23T00:00:00.00Z',
    'startDateTime': '2018-01-23T10:00:00.00Z',
    'endDateTime': '2018-01-23T12:30:00.00Z',
    'hoursWorked': 1.0000,
    'hoursToBill': 1.0000,
    'offsetHours': 0.0000,
    'summaryNotes': 'Entering time for task',
    'internalNotes': 'We will need to get more information',
    'roleID': 8,
    'createDateTime': '2018-01-23T09:50:00.00Z',
    'resourceID': 10,
    'creatorUserID': 10,
    'lastModifiedUserID': 10,
    'lastModifiedDateTime': '2018-01-23T13:00:00.00Z',
    'billingCodeID': 3,
    'contractID': 5,
    'showOnInvoice': True,
    'isNonBillable': False,
    'billingApprovalLevelMostRecent': 0,
}
API_TIME_ENTRY_ITEMS = [API_TIME_ENTRY_TICKET_ITEM, API_TIME_ENTRY_TASK_ITEM]
API_TIME_ENTRY_TICKET = {
    "items": [API_TIME_ENTRY_TICKET_ITEM],
    "pageDetails": API_PAGE_DETAILS
}
API_TIME_ENTRY_TASK = {
    "items": [API_TIME_ENTRY_TASK_ITEM],
    "pageDetails": API_PAGE_DETAILS
}
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
                    "label": "General Billing Code",
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

API_BILLING_CODE_TYPE_FIELD = {
    "fields": [
        {
            "name": "billingCodeType",
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
                    "value": "0",
                    "label": "Normal",
                    "isDefaultValue": False,
                    "sortOrder": 1,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                },
                {
                    "value": "1",
                    "label": "System",
                    "isDefaultValue": False,
                    "sortOrder": 2,
                    "parentValue": "",
                    "isActive": True,
                    "isSystem": True
                },
                {
                    "value": "2",
                    "label": "Non-Billable",
                    "isDefaultValue": False,
                    "sortOrder": 3,
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

API_BILLING_CODE_ITEMS = [
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
API_BILLING_CODE = {
    "items": API_BILLING_CODE_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}

API_ROLE_ITEM = {
    'id': 8,
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
    "resourceID": 10,
    "roleID": 8,
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
    "resourceID": 10,
    "roleID": 8,
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
        'creatorResourceID': 10,
        'canceledByResourceID': 10,
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
        'ticketID': 100,
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
        'taskID': 101,
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
        'resourceID': 10,
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
        'resourceID': 10,
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
    'assignedResourceID': 10,
    'assignedResourceRoleID': 8,
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
    'id': 100
}
API_TICKET_ITEMS = [API_TICKET_ITEM]
API_TICKET_BY_ID = {
    "item": API_TICKET_ITEM
}
API_TICKET = {
    "items": API_TICKET_ITEMS,
    "pageDetails": API_PAGE_DETAILS
}
