from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..accounts import (
    BankAccount,
)
from ..bills import (
    BillBase,
)
from ..core import (
    Chargeable,
)
from ..income import (
    Income,
)
from ..persistence import (
    SerialTypeLookup,
)


def convert_objects_to_persistence_dict(dict_of_objects: Mapping[str, Any]) -> dict[str, Any]:
    """
    Convert a dict of objects to a persistence dict.

    Parameters
    ----------
        dict_of_objects : Mapping[str, Any]
            Dictionary of objects in the form of account_name: Object
            For Example:
            {
                "Primary Checking": BankAccount(),
                "Primary Savings": BankAccount(),
                "Spotify": RecurringBill(),
                ...
            }

    Returns
    ----------
        dict[str, Any]
            Dictionary of to_dict() objects in the form of account_name: Object.to_dict()
                        For Example:
            {
                "Primary Checking": BankAccount().to_dict(),
                "Primary Savings": BankAccount()to_dict(),
                "Spotify": RecurringBill()to_dict(),
                ...
            }

    """
    return {key: obj.to_dict() for key, obj in dict_of_objects.items()}


def convert_persistence_dict_to_dict_of_objects(persistence_dict: Mapping[str, Any]) -> dict[str, Any]:
    """Convert a persistence dict to a dict of objects in the form of account_name: Object.from_dict()."""
    return_dict = {}
    chargeable_dict = {}

    # Build all of our objects
    for key, p_dict in persistence_dict.items():
        try:
            ObjectCls = SerialTypeLookup[p_dict["serial_type_in"]].value
            return_dict[key] = ObjectCls.from_dict(dict_in=p_dict)
        except KeyError as e:
            print(f"BUILDING - Skipping {key}: {e} — malformed 'serial_type_in'")
            continue

        # if they are chargeable let's store them for later
        if issubclass(ObjectCls, Chargeable):
            chargeable_dict[key] = return_dict[key]

    # Lets updated payment methods and account contributions now that everything is built
    for key, account in return_dict.items():
        if isinstance(account, BillBase):
            try:
                chargeable_account = chargeable_dict[persistence_dict[key]["payment_method_in"]]
            except KeyError as e:
                print(f"UPDATE PAYMENT - Skipping {key}: {e} — malformed payment_method_in")
                continue

            assert isinstance(chargeable_account, Chargeable)
            account.update_payment_method(chargeable_account)

        # If we have account contributions to make we make them
        if isinstance(account, Income):
            contribution_list = []
            for acc in persistence_dict[key]["account_contributions_in"]:
                try:
                    cont_account = return_dict[acc["account_name"]]
                except KeyError as e:
                    print(f"ACCOUNT CONTRIBUTIONS - Skipping {key}: {e} — account not found in return_dict")
                    continue

                if not isinstance(cont_account, BankAccount):
                    print(f"ACCOUNT CONTRIBUTIONS - Skipping {key}: {acc['account_name']} — not a BankAccount")
                    continue

                contribution_list.append((cont_account, acc["contribution"]))
            account.set_account_contribution(contribution_list)

    return return_dict


if __name__ == "__main__":  # pragma: no cover
    from pathlib import Path

    from persistence.json_reader_writer import read_object_from_file
    from src.finance_planning_tool._dirs import SAVED_OBJECT_DATA

    print(f"{SAVED_OBJECT_DATA}/test.json")
    object_input = read_object_from_file(Path(f"{SAVED_OBJECT_DATA}/temp.json"))
    built = convert_persistence_dict_to_dict_of_objects(object_input)

    for key, obj in built.items():
        print(key, "-", obj)
