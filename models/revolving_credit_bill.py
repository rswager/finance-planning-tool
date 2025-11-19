from datetime import date
from models.accountInformation import AccountInformation
from models.bankAccount import  BankAccount
from models.enumType import AccountType, FrequencyType
from models.interest import Interest
from models.ledger import Ledger
from models.triggerDays import TriggerDays
from models.utils import cents_to_dollars, money_cents, money_dollars, round_value
from typing import Union


class RevolvingCreditBill:
    """
    Represents a revolving credit bill, such as a credit card, that accrues daily interest
    and requires minimum payments at specified intervals. Payments are applied to a linked
    BankAccount or another RevolvingCreditBill.

    Attributes
    ----------
        _interest : Interest
            calculator based on the APR.
        _minimum_payment : money_cents
            Minimum required payment for each period.
        _credit_limit : money_cents
            Maximum allowed credit for the account.
        _accountInfo : AccountInformation
            Stores the account name, balance, and account type.
        _ledger : Ledger
            for tracking all transactions and interest accrual.
        _trigger_days : TriggerDays
            Manages the schedule of payments.
        _payment_method : BankAccount | RevolvingCreditBill
            The account or bill used to make the payment.
    """
    def __init__(self, name_in:str, balance_in: money_cents, account_type_in: AccountType,
                 initial_pay_date_in: date, frequency_type_in: FrequencyType, minimum_payment_in:money_cents,
                 payment_method_in: Union['RevolvingCreditBill', 'BankAccount'],
                 apr_rate_in: float, credit_limit_in: money_cents,
                 round_up: bool = False) -> None:
        """
        Initialize a RevolvingCreditBill instance.

        Parameters
        ----------
        name_in : str
            The name of the revolving credit account.
        balance_in : money_cents
            The starting balance (amount owed).
        account_type_in : AccountType
            Type of the account (e.g., CREDIT, CHECKING).
        initial_pay_date_in : date
            The first date a minimum payment is due.
        frequency_type_in : FrequencyType
            Payment frequency (e.g., MONTHLY, BI_WEEKLY).
        minimum_payment_in : money_cents
            The required minimum payment per period.
        payment_method_in : BankAccount | RevolvingCreditBill
            The account used to make the payment.
        apr_rate_in : float
            The annual percentage rate as a decimal (e.g., 0.05 for 5% APR).
        credit_limit_in : money_cents
            Maximum credit allowed on this account.
        round_up : bool, optional
            Whether to round the minimum payment up.
        """
        self._interest = Interest(apr_rate_in)
        self._minimum_payment : money_cents = minimum_payment_in if not round_up \
            else round_value(minimum_payment_in, round_up=round_up)
        self._credit_limit: money_cents = credit_limit_in
        self._accountInfo = AccountInformation(name_in=name_in,balance_in=-balance_in if balance_in>0 else balance_in,
                                               account_type_in=account_type_in)
        self._ledger = Ledger(['No.','Date', 'Description', 'Credit', 'Debit', 'Balance', 'Interest To Date'])
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
    def loan_balance_cents(self) -> money_cents:
        """
        money_cents: Returns the current balance owed.
        """
        return self._accountInfo.balance

    @property
    def loan_balance_dollars(self) -> money_dollars:
        """
        money_cents: Returns the current balance owed.
        """
        return cents_to_dollars(self._accountInfo.balance)

    @property
    def exceeded_credit_limit(self) -> bool:
        """
        bool: Returns True if the current balance exceeds the credit limit.
        """
        return abs(self._accountInfo.balance)>self._credit_limit

    @property
    def account_name(self) -> str:
        """
        str: Returns the name of the account.
        """
        return self._accountInfo.account_name

    @property
    def account_type(self) -> AccountType:
        """
        AccountType: Returns the type of account.
        """
        return self._accountInfo.account_type

    # Method to apply the payment to the balance
    def make_payment(self, date_in: date) -> None:
        """
        Apply the minimum payment to the balance and record the transaction in the ledger.
        Also deducts the payment from the linked payment method.

        Parameters
        ----------
            date_in : date
                The date the payment is made.
        """
        if self._accountInfo.balance != 0:
            min_payment = self._minimum_payment
            if abs(self._accountInfo.balance)<self._minimum_payment:
                min_payment = abs(self._accountInfo.balance)

            # Apply minimum Payment to the Bank Account
            self.make_a_transaction(date_in=date_in, action='Minimum Payment',credit=min_payment,debit=money_cents(0))
            self._payment_method.make_a_transaction(date_in=date_in, action=f'{self.account_name}-Payment',
                                                    credit=money_cents(0), debit=min_payment)

    def apply_daily_interest(self, date_in: date) -> None:
        """
        Calculate and apply daily interest to the account balance, recording it in the ledger.

        Parameters
        ----------
            date_in : date
                The date the interest is applied.
        """
        if self._accountInfo.balance != 0:
            self.make_a_transaction(date_in=date_in,action='Daily Interest',credit=money_cents(0),
                                    debit=self._interest.calculate_daily_interest(
                                        balance_in=self._accountInfo.balance,date_in=date_in))

    def process_day(self, date_in) -> None:
        """
        Process a single day: apply daily interest and make a minimum payment if it is a trigger date.

        Parameters
        ----------
            date_in : date
                The date being processed.
        """
        # We apply interest EVERY dat
        self.apply_daily_interest(date_in=date_in)
        if self._trigger_days.date_triggered(date_in):
            # Make minimum payment
            self.make_payment(date_in=date_in)

    def make_a_transaction(self, date_in: date, action: str, credit: money_cents, debit: money_cents) -> None:
        """
        Record a transaction in the ledger and update the account balance.

        Parameters
        ----------
            date_in : date
                The date of the transaction.
            action : str
                Description of the transaction.
            credit : money_cents
                Amount credited to the account.
            debit : money_cents
                Amount debited from the account.
        """
        self._accountInfo.update_balance(credit=credit,debit=debit)
        #['No.', 'Date', 'Description', 'Credit', 'Debit', 'Balance', 'Interest To Date']
        self._ledger.add_entry_to_ledger([self._ledger.row_number, date_in, action,
                                          cents_to_dollars(credit),
                                          cents_to_dollars(debit),
                                          self.loan_balance_dollars,
                                          cents_to_dollars(self._interest.interest_to_date)])

