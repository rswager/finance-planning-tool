from models.persistence.serializer import convert_objects_to_persistence_dict


def test_convert_objects_to_persistence(bank_accounts):
    acc1, acc2 = bank_accounts
    object_list = {}
    object_list[acc1.account_name] = acc1
    object_list[acc2.account_name] = acc2
    return_list = convert_objects_to_persistence_dict(object_list)
    assert return_list[acc1.account_name] == acc1.to_dict()
    assert return_list[acc2.account_name] == acc2.to_dict()
