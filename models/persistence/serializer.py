def convert_objects_to_list(dict_of_objects: dict) -> list[dict]:
    """Convert a list of objects to a dictionary."""
    return_list = []
    for obj in dict_of_objects.keys():
        return_list.append(dict_of_objects[obj].to_dict())
    return return_list
