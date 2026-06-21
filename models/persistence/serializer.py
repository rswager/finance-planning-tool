def convert_objects_to_list(dict_of_objects: dict) -> dict:
    """
    Convert a list of objects to a dictionary.

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
