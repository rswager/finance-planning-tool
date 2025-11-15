from datetime import date
from models.accountInformation import AccountInformation
from models.bankAccount import BankAccount
from models.enumType import AccountType, FrequencyType
from models.ledger import Ledger
from models.revolving_credit_bill import RevolvingCreditBill
from models.triggerDays import TriggerDays
from models.utils import round_value
from typing import Union


class RecurringBill:
    def __init__(self, name_in: str, minimum_payment_in: float, account_type_in: AccountType,
                 initial_pay_date_in: date, frequency_type_in: FrequencyType,
                 payment_method_in: Union['RevolvingCreditBill', 'BankAccount'],
                 round_up: bool=False) -> None:
        self._accountInfo = AccountInformation(name_in=name_in, balance_in=0, account_type_in=account_type_in)
        self._ledger = Ledger(columns=['No.', 'Date', 'Description', 'Credit', 'Total Paid To Date'])
        self._minimum_payment = minimum_payment_in if not round_up \
            else round_value(minimum_payment_in, round_up=round_up)
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union['RevolvingCreditBill','BankAccount'] = payment_method_in

    @property
    def ledger(self) -> list:
        # returns a deep copy of the ledger
        return self._ledger.ledger

    @property
    def raw_copy_ledger(self) -> list:
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        return self._ledger.col_count

    @property
    def account_name(self) -> str:
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        return self._accountInfo.account_type

    # Method to apply the payment to the balance
    def make_payment(self, date_in:date) -> None:
        # Apply minimum Payment to the Bank Account
        self._accountInfo.update_balance(credit=self._minimum_payment)
        #def make_a_transaction(self, date_in: date, action: str, credit: float, debit: float):
        self._payment_method.make_a_transaction(date_in=date_in, action=f'{self.account_name}-Payment',
                                                credit=0, debit=self._minimum_payment)
        self._ledger.add_entry_to_ledger([self._ledger.row_number, date_in, "Minimum Payment",
                                          self._minimum_payment, self._accountInfo.balance])

    def process_day(self, date_in:date) -> None:
        if self._trigger_days.date_triggered(date_in):
            # Make Account Contribution
            self.make_payment(date_in=date_in)
