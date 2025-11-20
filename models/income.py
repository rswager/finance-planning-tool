from datetime import date
from math import floor
from models.bankAccount import BankAccount
from models.enumType import  FrequencyType
from models.triggerDays import TriggerDays
from models.utils import money_cents, round_value
from typing import List,Tuple

class Income:
    """
    Represents a recurring income source that deposits funds into one or more bank accounts
    according to specified contribution percentages and payment frequency.
    """
    def __init__(self, name_in: str, income_in: money_cents, initial_pay_date_in: date,
                 account_contributions_in:List[Tuple[BankAccount, float]],
                 frequency_type_in: FrequencyType, round_down=False) -> None:
        """
        Initialize an Income instance.

        Parameters
        ----------
            name_in : str
                The name of the income source (e.g., "Salary").
            income_in : money_cents
                The total income amount per payment period in cents
            initial_pay_date_in : date
                The date of the first payment.
            account_contributions_in : List[Tuple[BankAccount, float]]
                A list of tuples, each containing a BankAccount and a fraction representing
                the portion of the income to deposit into that account. Fractions must sum ≤ 1.
            frequency_type_in : FrequencyType
                The frequency of payments (e.g., MONTHLY, BI_WEEKLY).
            round_down : bool, optional
                Whether to round down the income amount for convenience, by default False.

        Returns
        -------
            None
        """
        self._income_name = name_in
        self._income_amount = income_in if not round_down \
            else round_value(income_in, round_up=not round_down)
        self._trigger_days = TriggerDays(frequency_type_in)
        self._trigger_days.trigger_date=initial_pay_date_in
        self._account_contributions: List[Tuple[BankAccount, float]] = []
        self.set_account_contribution(account_contributions_in)

    def set_account_contribution(self, contributions:List[Tuple[BankAccount, float]]) -> None:
        """
        Set or update the account contributions for this income.

        Parameters
        ----------
            contributions : List[Tuple[BankAccount, float]]
                A list of tuples pairing a BankAccount with a fraction of the income to deposit.

        Returns
        -------
            None

        Raises
        ------
        ValueError
            If any individual contribution is not between 0 and 1, or if total contributions
            exceed 100%.
        """
        for account_reference, percent_contribution in contributions:
            if not (0 <= percent_contribution <= 1):
                raise ValueError("Contribution must be a percentage as a fraction between 0 and 1 (e.g., 5% → 0.05)")
            current_contribution = sum(contribution for _, contribution in self._account_contributions)
            if (current_contribution + percent_contribution) <= 1:
                self._account_contributions.append((account_reference,percent_contribution))
            else:
                raise ValueError('Total Contribution cannot exceed 100%!')

    def process_day(self, date_in:date) -> None:
        """
        Process income for a given day.

        Parameters
        ----------
        date_in : date
            The day to process.

        Returns
        -------
            None

        Notes
        -----
        - If the day matches a trigger day, the income is deposited to the assigned accounts.
        """
        if self._trigger_days.date_triggered(date_in):
            # Make Account Contribution
            self.deposit(transaction_date=date_in)

    def deposit(self,transaction_date:date) -> None:
        """
        Deposit the income into the configured bank accounts based on their contribution fractions.

        Parameters
        ----------
        transaction_date : date
            The date of the deposit.

        Returns
        -------
            None

        Notes
        -----
        - Deposits are recorded as transactions in each BankAccount's ledger.
        """
        # Make Account Contribution
        for account_reference, contribution_percentage in self._account_contributions:
            payment: money_cents = money_cents(floor(int(self._income_amount) * contribution_percentage))
            account_reference.make_a_transaction(date_in=transaction_date, action=f'{self._income_name} - Check',
                                                 credit=payment, debit=money_cents(0))
