from django.test import TestCase

from djautotask.models import Account


class AccountModelTest(TestCase):
    # Trivial test to confirm name is string
    def test_account_name_string(self):
        account = Account(account_name='Some string')
        self.assertEqual(str(account), account.account_name)
