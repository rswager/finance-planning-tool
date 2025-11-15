from datetime import date
from models.bankAccount import BankAccount
from models.enumType import  FrequencyType
from models.triggerDays import TriggerDays
from models.utils import round_value
from typing import List,Tuple


class Income:
    def __init__(self, name_in: str, income_in: float, initial_pay_date_in: date,
                 account_contributions_in:List[Tuple[BankAccount, float]],
                 frequency_type_in: FrequencyType, round_down=False) -> None:
        self._income_name = name_in
        self._income_amount = income_in if not round_down \
            else round_value(income_in, round_up=not round_down)
        self._trigger_days = TriggerDays(frequency_type_in)
        self._trigger_days.trigger_date=initial_pay_date_in
        self._account_contributions: List[Tuple[BankAccount, float]] = []
        self.set_account_contribution(account_contributions_in)

    def set_account_contribution(self, contributions:List[Tuple[BankAccount, float]]) -> None:
        for account_reference, percent_contribution in contributions:
            if not (0 <= percent_contribution <= 1):
                raise ValueError("Contribution must be a percentage as a fraction between 0 and 1 (e.g., 5% → 0.05)")
            current_contribution = sum(contribution for _, contribution in self._account_contributions)
            if (current_contribution + percent_contribution) <= 1:
                self._account_contributions.append((account_reference,percent_contribution))
            else:
                raise ValueError('Total Contribution cannot exceed 100%!')

    def process_day(self, date_in:date) -> None:
        if self._trigger_days.date_triggered(date_in):
            # Make Account Contribution
            self.deposit(transaction_date=date_in)

    def deposit(self,transaction_date:date) -> None:
        # Make Account Contribution
        for account_reference, contribution_percentage in self._account_contributions:
            payment = self._income_amount * contribution_percentage
            account_reference.make_a_transaction(date_in=transaction_date, action=f'{self._income_name} - Check',
                                                 credit=payment, debit=0)