from __future__ import annotations

from datetime import date

from dateutil.relativedelta import relativedelta

from models.core.enum_type import FrequencyType


class TriggerDays:
    """
    Manages trigger dates for recurring events such as payments, deposits, or interest applications.
    The trigger date determines when an action should occur, and this class automatically advances
    the date based on the provided frequency.

    Attributes
    ----------
        _trigger_date : date | None
            The next scheduled date on which an event should trigger.
        _frequency : FrequencyType
            The frequency at which the trigger date should advance (e.g., MONTHLY, WEEKLY).
    """

    def __init__(self, frequency_in: FrequencyType) -> None:
        """
        Initialize a TriggerDays instance.

        Parameters
        ----------
            frequency_in : FrequencyType
                How often the trigger should occur.
        """
        self._trigger_date: date | None = None
        self._frequency: FrequencyType = frequency_in

    @property
    def trigger_date(self) -> date | None:
        """
        date | None: The currently scheduled trigger date.

        Notes
        -----
        If the frequency type is SINGULAR, this will eventually become None
        after the event has triggered once.
        """
        return self._trigger_date

    @trigger_date.setter
    def trigger_date(self, date_in: date) -> None:
        """
        Set the next trigger date.

        Parameters
        ----------
        date_in : date
            The new trigger date.
        """
        self._trigger_date = date_in

    def date_triggered(self, processed_day: date) -> bool:
        """
        Check whether the given date matches the scheduled trigger date.
        If triggered, the next date is automatically calculated based on frequency.

        Parameters
        ----------
        processed_day : date
            The date currently being processed.

        Returns
        -------
        bool
            True if triggered, False otherwise.
        """
        if self._trigger_date is None:
            return False

        if processed_day == self._trigger_date:
            # now add the next date
            self._set_next_trigger_date(processed_day)
            return True
        return False

    def bring_trigger_date_to_target_date(self, target_start_date: date) -> None:
        """
        Moves the trigger date to the first scheduled occurrence on or after the target date.
        Works in both directions: steps forward if the trigger is behind the target, or steps
        backward if the trigger is ahead, then corrects forward if it overshoots.
        Does nothing for SINGULAR frequency.

        Parameters
        ----------
        target_start_date : date
            The simulation start date to align the trigger date to.

        Raises
        -------
            TypeError
                When an invalid Target Date is provided
            ValueError
                When the Trigger Date isn't yet set.
        """
        if self._frequency == FrequencyType.SINGULAR:
            return

        if not isinstance(target_start_date, date):
            raise TypeError("Target date must be of type date.")

        if self._trigger_date is None:
            raise ValueError("Trigger date wasn't set!")

        if self._trigger_date < target_start_date:
            while self._trigger_date < target_start_date:
                self._set_next_trigger_date(self._trigger_date, forwards=True)

        elif self._trigger_date > target_start_date:
            while self._trigger_date > target_start_date:
                self._set_next_trigger_date(self._trigger_date, forwards=False)
            # it is possible we will go before so let's move forward if we are before
            if self._trigger_date < target_start_date:
                self._set_next_trigger_date(self._trigger_date, forwards=True)

    def _set_next_trigger_date(self, current_trigger_date: date, forwards: bool = True) -> None:
        """
        Advance the trigger date forward or backward based on frequency.

        Parameters
        ----------
            current_trigger_date : date
                The date from which the next trigger date will be calculated.
            forwards : bool, optional
                If True (default), advances the date forward by one interval.
                If False, moves the date backward by one interval.

        Raises
        ------
            ValueError
                If frequency is None or an unsupported FrequencyType is encountered.
        """
        direction_modifier = 1 if forwards else -1
        # 1x a Month frequency
        if self._frequency == FrequencyType.MONTHLY:
            current_trigger_date = current_trigger_date + (relativedelta(months=1) * direction_modifier)
            self._trigger_date = current_trigger_date
        # Every other Week frequency (2x a month)
        elif self._frequency == FrequencyType.BI_WEEKLY:
            current_trigger_date = current_trigger_date + (relativedelta(weeks=2) * direction_modifier)
            self._trigger_date = current_trigger_date
        # Every Week frequency (1x a month)
        elif self._frequency == FrequencyType.WEEKLY:
            current_trigger_date = current_trigger_date + (relativedelta(weeks=1) * direction_modifier)
            self._trigger_date = current_trigger_date
        # Every Day Frequency
        elif self._frequency == FrequencyType.DAILY:
            current_trigger_date = current_trigger_date + (relativedelta(days=1) * direction_modifier)
            self._trigger_date = current_trigger_date
        # 1x a Year Frequency
        elif self._frequency == FrequencyType.YEARLY:
            current_trigger_date = current_trigger_date + (relativedelta(years=1) * direction_modifier)
            self._trigger_date = current_trigger_date
        # We only want to trigger once, so no frequency
        elif self._frequency == FrequencyType.SINGULAR:
            self._trigger_date = None
        # We are missing a Frequency Type:
        else:
            if self._frequency is None:
                raise ValueError(f"Frequency wasn't set! {self._frequency=}")
            else:
                raise ValueError(f"Received an Unexpected Frequency Type! {self._frequency=}")
