from models.persistence.serializer import convert_objects_to_list


def test_convert_objects_to_list(bank_accounts):
    acc1, acc2 = bank_accounts
    object_list = {}
    object_list[acc1.account_name] = acc1
    object_list[acc2.account_name] = acc2
    return_list = convert_objects_to_list(object_list)
    assert acc1.to_dict() in return_list
    assert acc2.to_dict() in return_list
