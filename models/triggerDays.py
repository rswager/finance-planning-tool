import typing
from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta
from models.enumType import FrequencyType

class TriggerDays:
    def __init__(self, frequency_in: FrequencyType) -> None:
        self._trigger_date: typing.Optional[date] = None
        self._frequency:FrequencyType = frequency_in

    @property
    def trigger_date(self) -> typing.Optional[None]:
        return self._trigger_date

    @trigger_date.setter
    def trigger_date(self, date_in: date):
        self._trigger_date = date_in

    def date_triggered(self, processed_day:date) -> bool:
        if processed_day == self._trigger_date:
              # now add the next date
            self._set_next_trigger_date(processed_day)
            return True
        return False

    def _set_next_trigger_date(self, current_trigger_date:date) -> None:
        # We make a payment 1 time a month
        if self._frequency == FrequencyType.MONTHLY:
            current_trigger_date = current_trigger_date + relativedelta(months=1)
        # Bi weekly payment
        elif self._frequency == FrequencyType.BI_WEEKLY:
            current_trigger_date = current_trigger_date + relativedelta(weeks=2)
        # Weekly payments
        elif self._frequency == FrequencyType.WEEKLY:
            current_trigger_date = current_trigger_date + relativedelta(weeks=1)
        self._trigger_date= current_trigger_date

    # def update_trigger_day_by