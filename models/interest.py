from calendar import isleap
from datetime import date

DAYS_IN_NON_LEAP_YEAR = 365
DAYS_IN_LEAP_YEAR = 366


class Interest:
    """
        Represents an interest calculation utility for financial accounts using a fixed APR.

        Attributes
        ----------
            _apr_rate : float
                Annual Percentage Rate as a fraction (e.g., 5% → 0.05).
            _interest_to_date : float
                Cumulative interest accrued over time.
    """

    def __init__(self, apr_rate_in: float) -> None:
        """
        Initialize an Interest instance.

        Parameters
        ----------
        apr_rate_in : float
            Annual Percentage Rate as a fraction between 0 and 1.

        Raises
        ------
        ValueError
            If apr_rate_in is not between 0 and 1.
        """
        if not (0 <= apr_rate_in <= 1):
            raise ValueError("APR must be a percentage as a fraction between 0 and 1 (e.g., 5% → 0.05)")
        self._apr_rate: float = apr_rate_in
        self._interest_to_date: float = 0

    def calculate_daily_interest(self, balance_in: float, date_in: date) -> float:
        """
        Calculate the daily interest for a given balance and date.

        Parameters
        ----------
        balance_in : float
            The account balance on which to calculate interest.
        date_in : date
            The date for which the daily interest is being calculated. Determines
            whether to use 365 or 366 days in the year.

        Returns
        -------
        float
            The daily interest amount, rounded to two decimal places.

        Notes
        -----
        - Interest is always calculated on the absolute value of the balance.
        - The cumulative interest (`_interest_to_date`) is updated with this amount.
        """

        interest = 0
        if abs(balance_in) > 0:
            n_days = DAYS_IN_NON_LEAP_YEAR if not isleap(date_in.year) else DAYS_IN_LEAP_YEAR
            interest = round(abs(balance_in) * (self._apr_rate / n_days), 2)

            # Update cumulative interest
            self._interest_to_date += interest

        return interest

    @property
    def interest_to_date(self) -> float:
        """
        float: Returns the cumulative interest accrued to date.
        """
        return self._interest_to_date