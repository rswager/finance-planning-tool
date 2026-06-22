from models.accounts.bank_account import BankAccount
from models.bills.bill_base import BillBase
from models.core.chargeable import Chargeable
from models.income.income import Income
from models.persistence.serial_lookup import SerialTypeLookup


def convert_objects_to_persistence_dict(dict_of_objects: dict) -> dict:
    """
    Convert a dict of objects to a persistence dict.

    Parameters
    ----------
        dict_of_objects : dict
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
        dict
            Dictionary of to_dict() objects in the form of account_name: Object.to_dict()
                        For Example:
            {
                "Primary Checking": BankAccount().to_dict(),
                "Primary Savings": BankAccount()to_dict(),
                "Spotify": RecurringBill()to_dict(),
                ...
            }

    """
    return_list = {}
    for obj in dict_of_objects.keys():
        return_list[obj] = dict_of_objects[obj].to_dict()
    return return_list


def convert_persistence_dict_to_dict_of_objects(persistence_dict: dict) -> dict:
    """Convert a persistence dict to a dict of objects in the form of account_name: Object.from_dict()."""
    return_dict = {}
    chargeable_dict = {}

    # Build all of our objects
    for each in persistence_dict.keys():
        ObjectCls = SerialTypeLookup[persistence_dict[each]["serial_type_in"]].value
        return_dict[each] = ObjectCls.from_dict(dict_in=persistence_dict[each])

        # if they are chargeable let's store them for later
        if issubclass(ObjectCls, Chargeable):
            chargeable_dict[each] = return_dict[each]

    # Let's updated payment methods and account contributions now that everything is built
    for each in return_dict.keys():
        account = return_dict[each]
        # If we have to add a payment_method then we need to do that.
        if isinstance(account, BillBase):
            chargeable_acccount = chargeable_dict[persistence_dict[each]["payment_method_in"]]
            assert isinstance(chargeable_acccount, Chargeable)
            assert hasattr(account, "update_payment_method")
            account.update_payment_method(chargeable_acccount)

        # If we have account contributions to make we make them
        if isinstance(account, Income):
            contribution_list = []
            for acc in persistence_dict[each]["account_contributions_in"]:
                cont_account = return_dict[acc["account_name"]]
                assert isinstance(cont_account, BankAccount)
                contribution_list.append((cont_account, acc["contribution"]))
            account.set_account_contribution(contribution_list)

    return return_dict


if __name__ == "__main__":  # pragma: no cover
    from pathlib import Path

    from _dirs import SAVED_OBJECT_DATA
    from models.persistence.json_reader_writer import read_object_from_file

    print(f"{SAVED_OBJECT_DATA}/test.json")
    object_input = read_object_from_file(Path(f"{SAVED_OBJECT_DATA}/temp.json"))
    built = convert_persistence_dict_to_dict_of_objects(object_input)

    for each in built.keys():
        print(built[each])
