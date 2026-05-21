from datetime import date
from typing import Protocol

from models.utils import MinorUnit


class Chargeable(Protocol):
    def make_a_transaction(self, date_in: date, action: str, credit: MinorUnit, debit: MinorUnit) -> None: ...
