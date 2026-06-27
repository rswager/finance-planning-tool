from models.persistence import SerialTypeLookup
from models.persistence.serializer import (
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
        print(each.account_name)
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
