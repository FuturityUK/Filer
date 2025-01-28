class Print:

    def __init__(self):
        pass

    @staticmethod
    def print_dictionary(dictionary_to_print: {}, indent_string: str = "", last_element: int = True):
        print(indent_string+"{")
        dictionary_to_print_length = len(dictionary_to_print)
        key_counter = 0
        for key, value in dictionary_to_print.items():
            key_counter += 1
            if key_counter != dictionary_to_print_length:
                print(indent_string+f"  '{key}': '{value}',")
            else:
                print(indent_string+f"  '{key}': '{value}'")
        if not last_element:
            print(indent_string + "},")
        else:
            print(indent_string + "}")

    @staticmethod
    def print_array_of_dictionaries(array_to_print: [], indent_string: str = ""):
        #print(f"results_array length: {len(results_array)}")
        print(indent_string+"[")
        array_to_print_length = len(array_to_print)
        array_element_counter = 0
        for element_to_print in array_to_print:
            array_element_counter += 1
            last_element = True if array_element_counter == array_to_print_length else False
            if isinstance(element_to_print, dict):
                Print.print_dictionary(element_to_print, indent_string+"  ", last_element)
            else:
                print(indent_string+"  "+element_to_print)
        print(indent_string+"]")

    @staticmethod
    def print_diff_dictionaries(first_dict: dict, second_dict: dict):
        print("first_dict, second_dict")
        for key, value in first_dict.items():
            if first_dict[key] != second_dict[key]:
                print(f"['{key}']: {value} != ['{key}']: {second_dict[key]} ")