from datetime import date
from models.accountInformation import AccountInformation
from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.ledger import Ledger
from models.revolving_credit_bill import RevolvingCreditBill
from models.triggerDays import TriggerDays
from models.utils import cents_to_dollars, money_cents, money_dollars, round_value
from typing import Union


class RecurringBill:
    """
    Represents a recurring bill with a fixed minimum payment that is applied at
    a specified frequency to a designated payment method (BankAccount or RevolvingCreditBill).

    Attributes
    ----------
        _accountInfo : AccountInformation
            Contains the bill's name, balance, and account type.
        _ledger : Ledger
            for tracking payments made to this bill.
        _minimum_payment : float
            The minimum amount to pay each cycle.
        _trigger_days : TriggerDays
            Manages when payments are due based on frequency.
        _payment_method : BankAccount | RevolvingCreditBill
            The account or bill that receives the payment.
    """
    def __init__(self, name_in: str, minimum_payment_in: money_cents, account_type_in: AccountType,
                 initial_pay_date_in: date, frequency_type_in: FrequencyType,
                 payment_method_in: Union['RevolvingCreditBill', 'BankAccount'],
                 round_up: bool=False) -> None:
        """
        Initialize a RecurringBill instance.

        Parameters
        ----------
            name_in : str
                The name of the bill.
            minimum_payment_in : money_cents
                The minimum payment amount per period -> in cents
            account_type_in : AccountType
                Type of account associated with the bill (e.g., CHECKING, CREDIT).
            initial_pay_date_in : date
                The first date the payment should be applied.
            frequency_type_in : FrequencyType
                How often the payment is made (e.g., MONTHLY, BI_WEEKLY).
            payment_method_in : BankAccount | RevolvingCreditBill
                The account or credit bill that receives the payment.
            round_up : bool, optional
                If True, rounds the minimum payment up to a desired precision.
        """
        self._accountInfo = AccountInformation(name_in=name_in, balance_in=money_cents(0), account_type_in=account_type_in)
        self._ledger = Ledger(columns=['No.', 'Date', 'Description', 'Credit', 'Total Paid To Date'])
        self._minimum_payment = minimum_payment_in if not round_up \
            else round_value(minimum_payment_in, round_up=round_up)
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union['RevolvingCreditBill','BankAccount'] = payment_method_in

    @property
    def raw_copy_ledger(self) -> list:
        """
        list: Returns a deep copy of the ledger to prevent accidental modification.
        """
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        """
        int: Returns the number of columns in the ledger.
        """
        return self._ledger.col_count

    @property
    def account_name(self) -> str:
        """
        str: Returns the name of the bill.
        """
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """
        AccountType: Returns the type of the bill's account.
        """
        return self._accountInfo.account_type

    @property
    def min_payment_dollars(self) -> money_dollars:
        return cents_to_dollars(self._minimum_payment)

    @property
    def frequency(self) -> FrequencyType:
        return self._trigger_days.frequency

    # Method to apply the payment to the balance
    def make_payment(self, date_in:date) -> None:
        """
        Apply the minimum payment to the bill and record it in the ledger.

        Parameters
        ----------
            date_in : date
                The date on which the payment is applied.
        """
        # Apply minimum Payment to the Bank Account
        self._accountInfo.update_balance(credit=self._minimum_payment)
        #def make_a_transaction(self, date_in: date, action: str, credit: float, debit: float):
        self._payment_method.make_a_transaction(date_in=date_in, action=f'{self.account_name}-Payment',
                                                credit=money_cents(0), debit=self._minimum_payment)
        self._ledger.add_entry_to_ledger([self._ledger.row_number, date_in, "Minimum Payment",
                                          cents_to_dollars(self._minimum_payment),
                                          cents_to_dollars(self._accountInfo.balance)])

    def process_day(self, date_in:date) -> None:
        """
        Process a single day, applying a payment if it matches a trigger date.

        Parameters
        ----------
            date_in : date
                The date being processed.
        """
        if self._trigger_days.date_triggered(date_in):
            # Make Account Contribution
            self.make_payment(date_in=date_in)
