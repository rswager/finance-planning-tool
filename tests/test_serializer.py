import pytest

from src.finance_planning_tool.models.persistence import (
    SerialTypeLookup,
    convert_objects_to_persistence_dict,
    convert_persistence_dict_to_dict_of_objects,
)


def test_convert_objects_to_persistence(bank_accounts):
    acc1, acc2 = bank_accounts
    object_dict = {}
    object_dict[acc1.account_name] = acc1
    object_dict[acc2.account_name] = acc2
    return_list = convert_objects_to_persistence_dict(object_dict)
    assert return_list[acc1.account_name] == acc1.to_dict()
    assert return_list[acc2.account_name] == acc2.to_dict()


def test_convert_persistence_dict_to_dict_of_objects(all_accounts):
    object_dict = {}
    for each in all_accounts:
        object_dict[each.account_name] = each
    # Convert to the Persistence Dict
    persistence_dict = convert_objects_to_persistence_dict(object_dict)
    # Rebuild the Object Dict (they will be new instance so they cannot be comparable)
    new_object_dict = convert_persistence_dict_to_dict_of_objects(persistence_dict)
    # We can convert these to a new persistence dict that is the same as the persistence_dict
    assert persistence_dict == convert_objects_to_persistence_dict(new_object_dict)


def test_convert_persistence_dict_to_dict_of_objects_drops_malformed_serial_key():
    object_dict = {
        "Gas": {
            "name_in": "Gas",
            "minimum_payment_in": 1000,
            "account_type_in": 6,
            "initial_pay_date_in": "2025-11-01",
            "frequency_type_in": 3,
            "payment_method_in": "primary_checking",
            "round_up": False,
            "serial_type_in": "malformed_serial_key",
        }
    }
    assert object_dict["Gas"]["serial_type_in"] not in SerialTypeLookup
    new_object_dict = convert_persistence_dict_to_dict_of_objects(object_dict)
    assert len(new_object_dict) == 0


@pytest.mark.parametrize("payment_method", [None, "", "primary_Income"])
def test_convert_persistence_dict_to_dict_of_objects_drops_invalid_payment_method(payment_method):
    object_dict = {
        "Gas": {
            "name_in": "Gas",
            "minimum_payment_in": 1000,
            "account_type_in": 6,
            "initial_pay_date_in": "2025-11-01",
            "frequency_type_in": 3,
            "payment_method_in": payment_method,
            "round_up": False,
            "serial_type_in": "bill_recurring",
        },
        "primary_Income": {
            "name_in": "primary_Income",
            "income_in": 260490,
            "initial_pay_date_in": "2025-11-06",
            "account_contributions_in": [],
            "frequency_type_in": 2,
            "round_down_in": False,
            "serial_type_in": "income",
        },
    }
    new_object_dict = convert_persistence_dict_to_dict_of_objects(object_dict)
    with pytest.raises(ValueError):
        _ = new_object_dict["Gas"].payment_method


@pytest.mark.parametrize(
    "contributions_in, contributions_out",
    [
        ([], []),
        (
            [
                {"account_name": "Checking", "contribution": 0.9},
                {"account_name": "primary_savings", "contribution": 0.1},
            ],
            [
                {"account_name": "Checking", "contribution": 0.9},
            ],
        ),
        (
            [
                {"account_name": "Checking", "contribution": 0.9},
                {"account_name": "Visa", "contribution": 0.1},
            ],
            [
                {"account_name": "Checking", "contribution": 0.9},
            ],
        ),
    ],
)
def test_convert_persistence_dict_to_dict_of_objects_drops_invalid_account_contributions(
    bank_accounts, credit_bill, contributions_in, contributions_out
):
    acc1, acc2 = bank_accounts
    object_dict = {
        "primary_Income": {
            "name_in": "primary_Income",
            "income_in": 260490,
            "initial_pay_date_in": "2025-11-06",
            "account_contributions_in": contributions_in,
            "frequency_type_in": 2,
            "round_down_in": False,
            "serial_type_in": "income",
        },
        credit_bill.account_name: credit_bill.to_dict(),
        acc1.account_name: acc1.to_dict(),
        acc2.account_name: acc2.to_dict(),
    }
    new_object_dict = convert_persistence_dict_to_dict_of_objects(object_dict)
    persisitence_dict = convert_objects_to_persistence_dict(new_object_dict)
    test_income = persisitence_dict["primary_Income"]
    assert test_income["account_contributions_in"] == contributions_out
