from datetime import date
from models.accountInformation import AccountInformation
from models.bankAccount import  BankAccount
from models.enumType import AccountType, FrequencyType
from models.interest import Interest
from models.ledger import Ledger
from models.triggerDays import TriggerDays
from models.utils import round_value
from typing import Union


# Possibly could make revolving a super of financed (with the option to pay only existing in revolving?)
class RevolvingCreditBill:
    def __init__(self, name_in:str, balance_in:float, account_type_in: AccountType,
                 initial_pay_date_in: date, frequency_type_in: FrequencyType, minimum_payment_in:float,
                 payment_method_in: Union['RevolvingCreditBill', 'BankAccount'],
                 apr_rate_in: float, credit_limit_in: float,
                 round_up: bool = False) -> None:
        self._interest = Interest(apr_rate_in)
        self._minimum_payment = minimum_payment_in if not round_up \
            else round_value(minimum_payment_in, round_up=round_up)
        self._credit_limit: float = credit_limit_in
        self._accountInfo = AccountInformation(name_in=name_in,balance_in=-balance_in,account_type_in=account_type_in)
        self._ledger = Ledger(['No.','Date', 'Description', 'Credit', 'Debit', 'Balance', 'Interest To Date'])
        self._trigger_days = TriggerDays(frequency_in=frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._payment_method: Union['RevolvingCreditBill','BankAccount'] = payment_method_in


    @property
    def ledger(self) -> list:
        return self._ledger.ledger

    @property
    def raw_copy_ledger(self) -> list:
        return self._ledger.raw_copy_ledger

    @property
    def ledger_col_count(self) -> int:
        return self._ledger.col_count

    @property
    def loan_balance(self) -> float:
        return self._accountInfo.balance

    @property
    def exceeded_credit_limit(self) -> bool:
        return abs(self._accountInfo.balance)>self._credit_limit

    @property
    def account_name(self) -> str:
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        return self._accountInfo.account_type

    # Method to apply the payment to the balance
    def make_payment(self, date_in: date) -> None:
        if self._accountInfo.balance != 0:
            min_payment = self._minimum_payment
            if abs(self._accountInfo.balance)<self._minimum_payment:
                min_payment = abs(self._accountInfo.balance)

            # Apply minimum Payment to the Bank Account
            self.make_a_transaction(date_in=date_in, action='Minimum Payment',credit=min_payment,debit=0)
            self._payment_method.make_a_transaction(date_in=date_in, action=f'{self.account_name}-Payment',
                                                    credit=0, debit=min_payment)

    def apply_daily_interest(self, date_in: date) -> None:
        if self._accountInfo.balance != 0:
            self.make_a_transaction(date_in=date_in,action='Daily Interest',credit=0,
                                    debit=self._interest.calculate_daily_interest(
                                        balance_in=self._accountInfo.balance,date_in=date_in))

    def process_day(self, date_in) -> None:
        # We apply interest EVERY dat
        self.apply_daily_interest(date_in=date_in)
        if self._trigger_days.date_triggered(date_in):
            # Make minimum payment
            self.make_payment(date_in=date_in)

    def make_a_transaction(self, date_in: date, action: str, credit: float, debit: float) -> None:
        self._accountInfo.update_balance(credit=credit,debit=debit)
        #['No.', 'Date', 'Description', 'Credit', 'Debit', 'Balance', 'Interest To Date']
        self._ledger.add_entry_to_ledger([self._ledger.row_number, date_in, action, credit, debit,
                                          self._accountInfo.balance, self._interest.interest_to_date])

