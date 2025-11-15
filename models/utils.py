def _calculate_rounded_value(value_in:float, mod_value:int, round_up: bool) -> float:
    value_in = int(value_in)
    if value_in % mod_value == 0:
        return value_in
    # Round UP
    elif round_up:
        return value_in + (mod_value - (value_in % mod_value))
    # Round Down
    else:
        return value_in - (value_in % mod_value)

def round_value(amount_in:float, round_up:bool = False) -> float:
        # If we are grater than $1_000, round to the nearest $100
        if amount_in >= 1_000:
            return _calculate_rounded_value(amount_in, 100,round_up)
        # Else we round to the nearest $10
        return _calculate_rounded_value(amount_in, 10,round_up)