from datetime import date
from typing import Self

from models.bank_account import BankAccount
from models.enum_type import FrequencyType
from models.trigger_days import TriggerDays
from models.utils import MinorUnit, round_value


class Income:
    """
    Represents a recurring income source that deposits funds into one or more bank accounts
    according to specified contribution percentages and payment frequency.
    """

    def __init__(
        self,
        name_in: str,
        income_in: MinorUnit,
        initial_pay_date_in: date,
        account_contributions_in: list[tuple[BankAccount, float]],
        frequency_type_in: FrequencyType,
        round_down: bool = False,
    ) -> None:
        """
        Initialize an Income instance.

        Parameters
        ----------
            name_in : str
                The name of the income source (e.g., "Salary").
            income_in : MinorUnit
                The total income amount per payment period in minor units (e.g. cents).
            initial_pay_date_in : date
                The date of the first payment.
            account_contributions_in : List[Tuple[BankAccount, float]]
                A list of tuples, each containing a BankAccount and a fraction representing
                the portion of the income to deposit into that account. Fractions must sum ≤ 1.
            frequency_type_in : FrequencyType
                The frequency of payments (e.g., MONTHLY, BI_WEEKLY).
            round_down : bool, optional
                Whether to round down the income amount for conservative budgeting, by default False.
        """
        self._income_name = name_in
        self._income_amount = income_in if not round_down else round_value(income_in, round_up=not round_down)
        self._round_down = round_down
        self._trigger_days = TriggerDays(frequency_type_in)
        self._trigger_days.trigger_date = initial_pay_date_in
        self._initial_pay_date = initial_pay_date_in
        self._account_contributions: list[tuple[BankAccount, float]] = []
        self.set_account_contribution(account_contributions_in)

    @classmethod
    def from_dict(cls, dict_in, chargeable_registry: dict[str, BankAccount]) -> Self:
        """Given a dictionary, create a Income object from it."""
        try:
            return cls(
                name_in=dict_in["name_in"],
                income_in=MinorUnit(dict_in["income_in"]),
                initial_pay_date_in=date.fromisoformat(dict_in["initial_pay_date_in"]),
                account_contributions_in=[
                    (chargeable_registry[account["account_name"]], account["contribution"])
                    for account in dict_in["account_contributions_in"]
                ],
                frequency_type_in=FrequencyType(dict_in["frequency_type_in"]),
                round_down=dict_in["round_down_in"],
            )
        except KeyError as e:
            raise KeyError(f"Missing required field: {e.args[0]}") from e

    def to_dict(self) -> dict:
        """Return the Dictionary representation of the Income object."""
        return {
            "name_in": self._income_name,
            "income_in": int(self._income_amount),
            "initial_pay_date_in": self._initial_pay_date.isoformat(),
            "account_contributions_in": [
                {"account_name": account.account_name, "contribution": contribution}
                for account, contribution in self._account_contributions
            ],
            "frequency_type_in": self._trigger_days._frequency.value,
            "round_down_in": self._round_down,
        }

    def set_account_contribution(self, contributions: list[tuple[BankAccount, float]]) -> None:
        """
        Set or update the account contributions for this income.

        Parameters
        ----------
            contributions : List[Tuple[BankAccount, float]]
                A list of tuples pairing a BankAccount with a fraction of the income to deposit.

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
                self._account_contributions.append((account_reference, percent_contribution))
            else:
                raise ValueError("Total Contribution cannot exceed 100%!")

    def process_day(self, date_in: date) -> None:
        """
        Process income for a given day, depositing funds if it is a trigger date.

        Parameters
        ----------
        date_in : date
            The day to process.
        """
        if self._trigger_days.date_triggered(date_in):
            self.deposit(transaction_date=date_in)

    def deposit(self, transaction_date: date) -> None:
        """
        Deposit the income into the configured bank accounts based on their contribution fractions.

        Parameters
        ----------
        transaction_date : date
            The date of the deposit.
        """
        allocated = MinorUnit(0)
        for i, (account_reference, contribution_percentage) in enumerate(self._account_contributions):
            if i < len(self._account_contributions) - 1:
                payment = self._income_amount * contribution_percentage
                allocated += payment
            else:
                payment = self._income_amount - allocated
            account_reference.make_a_transaction(
                date_in=transaction_date,
                action=f"{self._income_name} - Check",
                credit=payment,
                debit=MinorUnit(0),
            )

    def initialize_simulation_date(self, simulation_start_date: date) -> None:
        """
        Align the trigger date to the simulation start date before the simulation runs.

        Parameters
        ----------
        simulation_start_date : date
            The date the simulation begins. The trigger date will be advanced or
            rewound to the first scheduled occurrence on or after this date.
        """
        self._trigger_days.bring_trigger_date_to_target_date(simulation_start_date)
