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

API_ACCOUNT_PHYSICAL_LOCATION = {
    'id': 55,
    'Name': 'Primary Location',
    'AccountID': 174,
    'Active': True
}

API_ACCOUNT_PHYSICAL_LOCATION_LIST = [API_ACCOUNT_PHYSICAL_LOCATION]

API_PROJECT_STATUS_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Inactive',
        'SortOrder': 1,
        'Value': 0,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'New',
        'SortOrder': 2,
        'Value': 1,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Complete',
        'SortOrder': 8,
        'Value': 5,
        'parentValue': None,
    }
]

API_PROJECT_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Client',
        'SortOrder': 5,
        'Value': 5,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Internal',
        'SortOrder': 4,
        'Value': 4,
        'parentValue': None,
    }
]

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
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Post Sale',
        'SortOrder': 1,
        'Value': 6,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Monitoring Alert',
        'SortOrder': 2,
        'Value': 8,
        'parentValue': None,
    },
]

API_PRIORITY_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'High',
        'SortOrder': 2,
        'Value': 1,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Medium',
        'SortOrder': 3,
        'Value': 2,
        'parentValue': None,
    }
]

API_STATUS_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Waiting Materials',
        'SortOrder': 6,
        'Value': 9,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Scheduled',
        'SortOrder': 3,
        'Value': 10,
        'parentValue': None
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Escalate',
        'SortOrder': 5,
        'Value': 11,
        'parentValue': None
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Waiting Vendor',
        'SortOrder': 8,
        'Value': 12,
        'parentValue': None
    }
]

API_TICKET_CATEGORY_LIST = [
    {
        'id': 5,
        'UserDefinedFields': '',
        'Name': 'Standard (non-editable)',
        'Nickname': '',
        'Active': False,
        'DisplayColorRGB': 19,
        'GlobalDefault': False,
        'ApiOnly': False
    },
    {
        'id': 3,
        'UserDefinedFields': '',
        'Name': '',
        'Nickname': 'AEM Alert',
        'Active': False,
        'DisplayColorRGB': 21,
        'GlobalDefault': False,
        'ApiOnly': False
    }
]

API_DISPLAY_COLOR_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': '#ff6666',
        'SortOrder': 1,
        'Value': 19,
        'parentValue': None
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': '#ff855d',
        'SortOrder': 2,
        'Value': 21,
        'parentValue': None
    },
]

API_SOURCE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Monitoring Alert',
        'SortOrder': 8,
        'Value': 2,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Web Portal',
        'SortOrder': 6,
        'Value': 9,
        'parentValue': None,
    },

]

API_ISSUE_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Hardware',
        'SortOrder': 1,
        'Value': 2,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Internal',
        'SortOrder': 2,
        'Value': 3,
        'parentValue': None,
    },
]

API_TICKET_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Service Request',
        'SortOrder': 5,
        'Value': 3,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Incident',
        'SortOrder': 6,
        'Value': 2,
        'parentValue': None,
    },
]

API_SUB_ISSUE_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Rapid Response',
        'SortOrder': 5,
        'Value': 2,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Hardware Request',
        'SortOrder': 7,
        'Value': 3,
        'parentValue': None,
    },
]

API_LICENSE_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'API User',
        'SortOrder': 7,
        'Value': 7,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Team Member',
        'SortOrder': 4,
        'Value': 4,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'Administrator',
        'SortOrder': 1,
        'Value': 1,
        'parentValue': None,
    },
]

API_ACCOUNT_TYPE_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Customer',
        'SortOrder': 5,
        'Value': 3,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Vendor',
        'SortOrder': 6,
        'Value': 2,
        'parentValue': None,
    },
]

API_SERVICE_CALL_STATUS_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'New',
        'SortOrder': 5,
        'Value': 3,
        'parentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': False,
        'Label': 'Complete',
        'SortOrder': 6,
        'Value': 2,
        'parentValue': None,
    },
]

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

API_TASK_SECONDARY_RESOURCE = {
    'id': 29684411,
    'UserDefinedFields': None,
    'TaskID': 7733,
    'ResourceID': 29683794,
    'RoleID': 29683461,
}
API_TASK_SECONDARY_RESOURCE_LIST = [API_TASK_SECONDARY_RESOURCE]

API_TICKET_NOTE = {
    'id': 45,
    'CreateDateTime':
        datetime(2018, 1, 23, 11, 0, tzinfo=tzoffset(None, 3600)),
    'Description': "Note description",
    'CreatorResourceID': 29683794,
    'LastActivityDate':
        datetime(2018, 1, 23, 11, 0, tzinfo=tzoffset(None, 3600)),
    'NoteType': 2,
    'Publish': 1,
    'TicketID': 7688,
    'Title': "Note Title",
}
API_TICKET_NOTE_LIST = [API_TICKET_NOTE]

API_TASK_NOTE = {
    'id': 45,
    'CreateDateTime':
        datetime(2018, 1, 23, 11, 0, tzinfo=tzoffset(None, 3600)),
    'Description': "Note description",
    'CreatorResourceID': 29683794,
    'LastActivityDate':
        datetime(2018, 1, 23, 11, 0, tzinfo=tzoffset(None, 3600)),
    'NoteType': 2,
    'Publish': 1,
    'TaskID': 7733,
    'Title': "Note Title",
}
API_TASK_NOTE_LIST = [API_TASK_NOTE]

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

API_TASK_TYPE_LINK_LIST = [
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'ITServiceRequest',
        'SortOrder': 1,
        'Value': 19,
        'ParentValue': None,
    },
    {
        'IsActive': True,
        'IsDefaultValue': False,
        'IsSystem': True,
        'Label': 'ProjectTask',
        'SortOrder': 2,
        'Value': 20,
        'ParentValue': None,
    }
]

API_TIME_ENTRY_TICKET = {
    'id': 4,
    'UserDefinedFields': None,
    'TicketID': 7689,
    'InternalAllocationCodeID': 29683403,
    'Type': 2,
    'DateWorked': datetime(2018, 1, 23, 0, 0, tzinfo=tzoffset(None, 3600)),
    'StartDateTime': datetime(2018, 1, 23, 10, 0, tzinfo=tzoffset(None, 3600)),
    'EndDateTime': datetime(2018, 1, 23, 12, 30, tzinfo=tzoffset(None, 3600)),
    'HoursWorked': 1.0000,
    'HoursToBill': 1.0000,
    'OffsetHours': 0.0000,
    'SummaryNotes': 'Initial triage of issue',
    'InternalNotes': 'We will need to get more information',
    'RoleID': 29683396,
    'CreateDateTime':
        datetime(2018, 1, 23, 9, 50, tzinfo=tzoffset(None, 3600)),
    'ResourceID': 28,
    'CreatorUserID': 29683794,
    'LastModifiedUserID': 29683794,
    'LastModifiedDateTime':
        datetime(2018, 1, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'AllocationCodeID': 29683403,
    'ContractID': 29684054,
    'ShowOnInvoice': True,
    'NonBillable': False,
    'BillingApprovalLevelMostRecent': 0,
}

API_TIME_ENTRY_TASK = {
    'id': 5,
    'UserDefinedFields': None,
    'TaskID': 7734,
    'InternalAllocationCodeID': 29683403,
    'Type': 2,
    'DateWorked': datetime(2018, 1, 23, 0, 0, tzinfo=tzoffset(None, 3600)),
    'StartDateTime': datetime(2018, 1, 23, 10, 0, tzinfo=tzoffset(None, 3600)),
    'EndDateTime': datetime(2018, 1, 23, 12, 30, tzinfo=tzoffset(None, 3600)),
    'HoursWorked': 1.0000,
    'HoursToBill': 1.0000,
    'OffsetHours': 0.0000,
    'SummaryNotes': 'Entering time for task',
    'InternalNotes': 'We will need to get more information',
    'RoleID': 29683396,
    'CreateDateTime':
        datetime(2018, 1, 23, 9, 50, tzinfo=tzoffset(None, 3600)),
    'ResourceID': 28,
    'CreatorUserID': 29683794,
    'LastModifiedUserID': 29683794,
    'LastModifiedDateTime':
        datetime(2018, 1, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'AllocationCodeID': 29683403,
    'ContractID': 29684054,
    'ShowOnInvoice': True,
    'NonBillable': False,
    'BillingApprovalLevelMostRecent': 0,
}
API_TIME_ENTRY_LIST = [API_TIME_ENTRY_TICKET, API_TIME_ENTRY_TASK]

API_USE_TYPE_LIST = [
    {
        'Value': 1,
        'Label': 'General Allocation Code',
        'IsDefaultValue': False,
        'SortOrder': 1,
        'parentValue': None,
        'IsActive': True,
        'IsSystem': True,
    },
    {
        'Value': 2,
        'Label': 'Internal Allocation Code',
        'IsDefaultValue': False,
        'SortOrder': 1,
        'parentValue': None,
        'IsActive': True,
        'IsSystem': True,
    }
]

API_ALLOCATION_CODE = {
    'id': 2,
    'UserDefinedFields': None,
    'Name': 'Finance',
    'Type': 1,
    'UseType': 2,
    'Active': True,
    'UnitCost': 0.0000,
    'UnitPrice': 0.0000,
    'ExternalNumber': 0,
    'IsExcludedFromNewContracts': False,
}
API_ALLOCATION_CODE_LIST = [API_ALLOCATION_CODE]

API_ROLE = {
    'id': 29683396,
    'Name': "IT:Technician I",
    'Description': "",
    'Active': True,
    'HourlyFactor': 1,
    'HourlyRate': 100,
    'RoleType': 0,
    'SystemRole': False,
}
API_ROLE_LIST = [API_ROLE]

API_DEPARTMENT = {
    'id': 29683384,
    'Name': "Finance",
    'Description': "Finance Dept",
    'Number': "",
}
API_DEPARTMENT_LIST = [API_DEPARTMENT]

API_RESOURCE_ROLE_DEPARTMENT = {
    'id': 32,
    'Default': True,
    'DepartmentID': 29683384,
    'Active': True,
    'ResourceID': 29683794,
    'RoleID': 29683396,
    'DepartmentLead': True,
}
API_RESOURCE_ROLE_DEPARTMENT_LIST = [API_RESOURCE_ROLE_DEPARTMENT]

API_RESOURCE_SERVICE_DESK_ROLE = {
    'id': 32,
    'Default': True,
    'Active': True,
    'ResourceID': 29683794,
    'RoleID': 29683396,
}
API_RESOURCE_SERVICE_DESK_ROLE_LIST = [API_RESOURCE_SERVICE_DESK_ROLE]

API_CONTRACT = {
    'id': 29684183,
    'UserDefinedFields': "",
    'AccountID': 174,
    'BillingPreference': 2,
    'Compliance': True,
    'ContractCategory': 15,
    'ContractName': "Upstate Document Providers - Hosted SaaS",
    'ContractNumber': "2343451",
    'ContractPeriodType': "m",
    'ContractType': 7,
    'IsDefaultContract': True,
    'EndDate': datetime(2020, 2, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'EstimatedCost': 0.0000,
    'EstimatedHours': 0.0000,
    'EstimatedRevenue': 5795.00,
    'SetupFee': 995.0000,
    'StartDate': datetime(2020, 2, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'Status': 1,
    'TimeReportingRequiresStartAndStopTimes': 1,
    'ServiceLevelAgreementID': 1,
    'PurchaseOrderNumber': "",
    'InternalCurrencySetupFee': 995.0000,
}
API_CONTRACT_LIST = [API_CONTRACT]

API_SERVICE_CALL = {
    'id': 2,
    'Description': 'Email just in, printer is down.',
    'Complete': False,
    'Duration': 1,
    'CreateDateTime': datetime(
        2020, 1, 22, 13, 0, tzinfo=tzoffset(None, 3600)),
    'StartDateTime': datetime(2020, 2, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'EndDateTime': datetime(2020, 3, 23, 13, 0, tzinfo=tzoffset(None, 3600)),
    'CanceledDateTime': None,
    'LastModifiedDateTime': None,
    'AccountID': 174,
    'Status': 2,
    'CreatorResourceID': 29683794,
    'CanceledByResource': 29683794,
}
API_SERVICE_CALL_LIST = [API_SERVICE_CALL]

API_SERVICE_CALL_TICKET = {
    'id': 4,
    'ServiceCallID': 2,
    'TicketID': 7688,
}
API_SERVICE_CALL_TICKET_LIST = [API_SERVICE_CALL_TICKET]

API_SERVICE_CALL_TASK = {
    'id': 4,
    'ServiceCallID': 2,
    'TaskID': 7733,
}
API_SERVICE_CALL_TASK_LIST = [API_SERVICE_CALL_TASK]

API_SERVICE_CALL_TICKET_RESOURCE = {
    'id': 4,
    'ServiceCallTicketID': 4,
    'ResourceID': 29683794,
}
API_SERVICE_CALL_TICKET_RESOURCE_LIST = [API_SERVICE_CALL_TICKET_RESOURCE]

API_SERVICE_CALL_TASK_RESOURCE = {
    'id': 4,
    'ServiceCallTaskID': 4,
    'ResourceID': 29683794,
}
API_SERVICE_CALL_TASK_RESOURCE_LIST = [API_SERVICE_CALL_TASK_RESOURCE]

API_TASK_PREDECESSOR = {
    'id': 1,
    'UserDefinedFields': None,
    'LagDays': 0,
    'PredecessorTaskID': API_TASK_ITEM['id'],
    'SuccessorTaskID': 7755,
}
API_TASK_PREDECESSOR_LIST = [API_TASK_PREDECESSOR]

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
        'companyID': 29683561,
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
