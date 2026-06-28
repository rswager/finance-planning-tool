"""An abstract for denoting an account that can be charged against (I.E can pay a bill)"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from ..core.utils import (
    MinorUnit,
)


class Chargeable(ABC):
    @abstractmethod
    def make_a_transaction(self, date_in: date, action: str, credit: MinorUnit, debit: MinorUnit) -> None: ...

    @property
    @abstractmethod
    def account_name(self) -> str: ...
