from typing import NewType

money_cents = NewType("money_cents", int)
money_dollars = NewType("money_dollars", float)


def _calculate_rounded_value(value_in: money_cents, mod_value: int, round_up: bool) -> money_cents:
    """
    Round a numeric value to the nearest multiple of a given modulus.

    This helper function first casts the input value to an integer and
    then rounds it either up or down to the nearest multiple of `mod_value`.

    Parameters
    ----------
        value_in : float
            The value to be rounded. The decimal portion is discarded before rounding.
        mod_value : int
            The modulus to round to (e.g., 10, 100).
        round_up : bool
            If True, round up to the next multiple of `mod_value`.
            If False, round down to the previous multiple.

    Returns
    -------
        float
            The rounded integer value.
    """
    value_in = value_in
    if value_in % mod_value == 0:
        return value_in
    # Round UP
    elif round_up:
        return money_cents(value_in + (mod_value - (value_in % mod_value)))
    # Round Down
    else:
        return money_cents(value_in - (value_in % mod_value))


def round_value(amount_in: money_cents, round_up: bool = False) -> money_cents:
    """
    Round a monetary amount to the appropriate precision based on its size.

    Amounts ≥ 1,000 are rounded to the nearest hundred.
    Amounts < 1,000 are rounded to the nearest ten.

    Parameters
    ----------
    amount_in : float
        The monetary value to round.
    round_up : bool, optional
        If True, round upward. If False (default), round downward.

    Returns
    -------
    float
        The rounded value.
    """
    # If we are grater than $1_000, round to the nearest $100
    if amount_in >= 1_000_00:
        return _calculate_rounded_value(amount_in, 100_00, round_up)
    # Else we round to the nearest $10
    return _calculate_rounded_value(amount_in, 10_00, round_up)


def dollars_to_cents(dollars_in: money_dollars) -> money_cents:
    return money_cents(int(dollars_in * 100))


def cents_to_dollars(cents_in: money_cents) -> money_dollars:
    return money_dollars(cents_in / 100)
