from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, NewType, SupportsIndex


@dataclass(frozen=True)
class Currency:
    symbol: str
    conversion: int  # minor units per major unit


class CurrencyType(Enum):
    USD = Currency(symbol="$", conversion=100)
    GBP = Currency(symbol="£", conversion=100)
    EUR = Currency(symbol="€", conversion=100)
    JPY = Currency(symbol="¥", conversion=1)


MajorUnit = NewType("MajorUnit", float)


class MinorUnit(int):
    """
    Integer type representing the smallest denomination of the active currency
    (e.g. cents for USD, pence for GBP). All monetary arithmetic is done in
    this unit to avoid floating-point errors.

    The active currency defaults to USD and can be changed for the entire
    application by calling MinorUnit.set_currency(CurrencyType.GBP).
    """

    _currency: ClassVar[Currency] = CurrencyType.USD.value

    def __new__(cls, value: int | float) -> MinorUnit:
        return super().__new__(cls, int(value))

    def __add__(self, other: int) -> MinorUnit:
        return MinorUnit(int.__add__(self, other))

    def __sub__(self, other: int) -> MinorUnit:
        return MinorUnit(int.__sub__(self, other))

    def __neg__(self) -> MinorUnit:
        return MinorUnit(int.__neg__(self))

    def __abs__(self) -> MinorUnit:
        return MinorUnit(int.__abs__(self))

    def __mul__(self, other: int | float) -> MinorUnit:
        return MinorUnit(int(int(self) * other))

    def __truediv__(self, other: int | float) -> MinorUnit:
        return MinorUnit(int(int(self) / other))

    def __radd__(self, other: int) -> MinorUnit:
        return MinorUnit(int.__add__(self, other))

    def __mod__(self, other: int) -> MinorUnit:
        return MinorUnit(int.__mod__(self, other))

    def __floordiv__(self, other: int | float) -> MinorUnit:
        return MinorUnit(int(int(self) // other))

    def __round__(self, ndigits: SupportsIndex = 0) -> MinorUnit:
        return MinorUnit(int.__round__(self, ndigits))

    def to_major(self) -> MajorUnit:
        """Convert to the major unit (e.g. dollars) for display."""
        return MajorUnit(int(self) / self._currency.conversion)

    @classmethod
    def from_major(cls, value: float) -> MinorUnit:
        """Convert from the major unit (e.g. dollars) into minor units."""
        return cls(int(value * cls._currency.conversion))

    @classmethod
    def set_currency(cls, currency: CurrencyType) -> None:
        """Switch the active currency for all MinorUnit instances."""
        cls._currency = currency.value

    @property
    def symbol(self) -> str:
        return self._currency.symbol


def round_value(amount_in: MinorUnit, round_up: bool = False) -> MinorUnit:
    """
    Round a monetary amount to the appropriate precision based on its size.

    Amounts >= 1,000 major units are rounded to the nearest 100 major units.
    Amounts < 1,000 major units are rounded to the nearest 10 major units.
    """
    conversion = MinorUnit._currency.conversion
    if amount_in >= 1_000 * conversion:
        return _calculate_rounded_value(amount_in, 100 * conversion, round_up)
    return _calculate_rounded_value(amount_in, 10 * conversion, round_up)


def _calculate_rounded_value(value_in: MinorUnit, mod_value: int, round_up: bool) -> MinorUnit:
    if value_in % mod_value == 0:
        return value_in
    elif round_up:
        return value_in + (mod_value - (value_in % mod_value))
    else:
        return value_in - (value_in % mod_value)
