


class FileTypes:

    def __init__(self):
        pass

    @staticmethod
    def heading_level(heading: str) -> int:
        return int(heading.count("=") / 2)

    @staticmethod
    def remove_formatting_from_heading(heading: str) -> str:
        return heading.replace("=", "").strip()

    @staticmethod
    def clear_heading_dictionary_below_level(heading_dictionary: {}, heading_level: int):
        for index, key in enumerate(heading_dictionary):
            if index + 1 > heading_level:
                heading_dictionary[key] = None

    @staticmethod
    def remove_formatting_from_string(temp_string: str) -> str:
        # Replace Link with just it's Text
        while True:
            double_open_square_brackets_index = temp_string.find("[[")
            double_close_square_brackets_index = temp_string.find("]]", double_open_square_brackets_index)
            if double_open_square_brackets_index == -1 or double_close_square_brackets_index == -1:
                # All links processed so break out of the loop
                break
            else:
                # We've found a link so replace it with text
                link_string = temp_string[double_open_square_brackets_index + 2:double_close_square_brackets_index]
                link_text = link_string[link_string.find("|") + 1:]
                temp_string = temp_string[:double_open_square_brackets_index] + link_text + temp_string[double_close_square_brackets_index + 2:]
        # Replace Visible Anchors
        while True:
            open_visible_anchor_index = temp_string.find("{{visible anchor")
            close_visible_anchor_index = temp_string.find("}}", open_visible_anchor_index)
            if open_visible_anchor_index == -1 or close_visible_anchor_index == -1:
                # All links processed so break out of the loop
                break
            else:
                # We've found a link so replace it with text
                link_string = temp_string[open_visible_anchor_index + 2:close_visible_anchor_index]
                link_text = link_string[link_string.find("|") + 1:] # Extract the text after the anchor definition
                link_text = link_text[:link_text.find("|")] # Extract the first value before the '|'
                temp_string = temp_string[:open_visible_anchor_index] + link_text + temp_string[close_visible_anchor_index + 2:]
        return temp_string

    @staticmethod
    def start():
        line_number = 0
        #heading_dictionary = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None}
        #heading_level_dictionary = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        heading_dictionary = {2: None, 3: None, 4: None}
        heading_level_dictionary = {2: 0, 3: 0, 4: 0}

        for filelineno, line in enumerate(open("wiki_file_types.txt", encoding="utf-8")):
            line_number += 1
            line_striped = line.strip()

            if line_striped.startswith("="):
                # HEADING LINE
                #print(f"line_striped: {line_striped}")
                heading_level = FileTypes.heading_level(line_striped)
                heading_level_dictionary[heading_level] += 1
                #print(f"heading_level: {heading_level}")
                heading_text = FileTypes.remove_formatting_from_heading(line_striped)
                #print(f"heading_text: {heading_text}")
                heading_dictionary[heading_level] = FileTypes.remove_formatting_from_string(heading_text)
                #print(f"heading_new : {heading_dictionary[heading_level]}")
                #if heading_text.count("|") > 0 and heading_text != heading_dictionary[heading_level]:
                #    break
                FileTypes.clear_heading_dictionary_below_level(heading_dictionary, heading_level)
                print(f"heading_dictionary: {heading_dictionary}")
            else:
                # OTHER TEXT LINE
                if line_striped.startswith("*"):
                    # FILE EXTENSIONS
                    pass
                    #file_extension = line_striped.replace("*", "").strip()
                else:
                    if len(line_striped) > 0:
                        pass
                        print(f"line_striped: {FileTypes.remove_formatting_from_string(line_striped)}")

        print(f"{heading_level_dictionary}")



if __name__ == "__main__":
    FileTypes.start()

