
class Data:

    def __init__(self):
        pass

    @staticmethod
    def find_dictionary_in_array(array_of_dictionary: dict, key: str, search_value: any) -> dict | None:
        #print(f"Value to match: '{search_value}'")
        for dictionary in array_of_dictionary:
            dictionary_value = dictionary[key]
            if type(search_value) is not type(dictionary_value):
                print("find_dictionary_in_array() - Types do not match")
                print(f"search value type: {type(search_value)}")
                print(f"dictionary value type: {type(search_value)}")
                exit(2)
            #print(f"dictionary['{key}'] == '{dictionary[key]}'")
            if dictionary[key] == search_value:
                return dictionary
        return None