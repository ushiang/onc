import os
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.translation import gettext as _


class Error(Exception):
    """
    Base class for exceptions
    """
    @staticmethod
    def log(error):
        from datetime import datetime

        # log this error in the appropriate text log
        txt_file = os.path.join(settings.BASE_DIR, 'logs', 'error_log')
        appendage = " Timestamp: %s" % datetime.now()
        with open(txt_file, "a") as f:
            f.write("\n"+error+appendage)


class AccountPolicyError(Error):
    """
    This exception is raised if an account policy rule is broken
    E.g. Crediting an account with a Dr policy
    """
    def __init__(self, policy, passed_policy):
        self.policy = policy
        self.passed_policy = passed_policy
        self.msg = _("Account policy violation. Tried doing a %s but policy is %s") % (passed_policy, policy)

        self.verify()

    def verify(self):
        if self.policy == "DR" and self.passed_policy != "DR":
            self.msg = _("The account selected has a Debit only policy")
            raise self
        elif self.policy == "CR" and self.passed_policy != "CR":
            self.msg = _("The account selected has a Credit only policy")
            raise self
        else:
            return True


class ItemPackError(Error):
    """
    This Exception is thrown when issues are found with the Item sections of
    1. Assets
    2. Payables
    3. Receivables
    4. Sales
    5. Expenses
    We will process the pack array and compare the total amount with the amount parsed,
    we'll also check account policies while doing so
    """
    def __init__(self, pack, passed_policy):
        self.pack = pack
        self.passed_policy = passed_policy
        self.msg = ""

        self.verify()

    def verify(self):

        from ..accounts.models import Account
        from packages.inventory.models import UoM

        i = 0

        if len(self.pack) < 1:
            self.msg = _("Illegal to post an empty transaction, please select some items")
            raise self

        print self.pack
        for x in self.pack:
            try:
                account_pk = int(x["account"]["originalObject"]["id"])
            except (KeyError, TypeError):
                continue

            try:
                uom_pk = int(x["item"]["originalObject"]["id"])
            except (KeyError, TypeError):
                continue

            if account_pk:
                i += 1
                try:
                    account = Account.pp.get(pk=account_pk)
                    UoM.pp.get(pk=uom_pk)

                    try:
                        AccountPolicyError(account.policy, self.passed_policy)
                    except AccountPolicyError as e:
                        self.msg = _("Account on row %s threw this error. %s") % (i, e.msg)
                        raise self
                except Account.DoesNotExist:
                    self.msg = _("Account selected on row %s does not exist") % i
                    raise self
                except UoM.DoesNotExist:
                    self.msg = _("Item select on row %s does not exist") % i
                    raise self
                except TypeError:
                    self.msg = _("Amount on row %s is invalid") % i
                    raise self
                except (KeyError, AttributeError):
                    self.msg = _("An unknown internal error occurred")
                    raise self
            else:
                continue

        if i == 0:
            self.msg = _("Your account table cannot be empty be enter values in your account table with "
                         "accounts to represent each item/administrative transactions")
            raise self


class PaymentPackError(Error):
    """
    This Exception is thrown when issues are found with the Payment Account sections of
    1. Assets
    2. Payables
    3. Receivables
    4. Sales
    5. Expenses
    We will process the pack array and compare the total amount with the amount parsed,
    we'll also check account policies while doing so
    """
    def __init__(self, pack, amount, passed_policy):
        self.pack = pack
        self.amount = amount
        self.passed_policy = passed_policy
        self.msg = ""

        self.verify()

    def verify(self):

        from ..accounts.models import Account

        t_amount = 0
        i = 0

        for x in self.pack:
            try:
                account_pk = int(x["account"]["originalObject"]["id"])
            except (KeyError, TypeError):
                continue

            if account_pk:
                i += 1
                try:
                    account = Account.pp.get(pk=account_pk)
                    t_amount += float(x["amount"])

                    try:
                        AccountPolicyError(account.policy, self.passed_policy)
                    except AccountPolicyError as e:
                        self.msg = _("Account on row %s threw this error. %s") % (i, e.msg)
                        raise self
                except Account.DoesNotExist:
                    self.msg = _("Account selected does not exist")
                    raise self
                except TypeError:
                    self.msg = _("Amount on row %s is invalid") % i
                    raise self
                except (KeyError, AttributeError):
                    self.msg = _("An unknown internal error occured")
                    raise self
            else:
                continue

        if t_amount != self.amount:
            self.msg = _("The amount on the payment section must match perfectly with that on the item section")
            raise self