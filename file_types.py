import os.path
import urllib.request, urllib.error, urllib.parse
from time import sleep
import re
import csv

class FileTypes:

    def __init__(self):
        pass

    @staticmethod
    def download_file_types() -> str :
        url="https://en.wikipedia.org/w/index.php?title=List_of_file_formats&action=raw"
        response = urllib.request.urlopen(url)
        web_content = response.read().decode('UTF-8')
        return web_content

    @staticmethod
    def heading_level(heading: str) -> int:
        return int(heading.count("=") / 2)

    @staticmethod
    def remove_formatting_from_heading(heading: str) -> str:
        return heading.replace("=", "").strip()

    @staticmethod
    def clear_heading_dictionary_below_level(heading_dictionary: {}, heading_level: int):
        #print(f"clear_heading_dictionary_below_level():")
        #print(f"heading_level: {heading_level}")
        #print(f"heading_dictionary: {heading_dictionary}")
        for key, value in heading_dictionary.items():
            if int(key) > heading_level:
                heading_dictionary[key] = None
        #print(f"new heading_dictionary: {heading_dictionary}")

    @staticmethod
    def display_heading_level_counts(heading_level_dictionary):
        for key, value in heading_level_dictionary.items():
            if value != 0:
                print(f"heading_level: {key} - count: {value}")

    @staticmethod
    def display_heading_values(heading_dictionary):
        first_heading = True
        for key, value in heading_dictionary.items():
            if value is not None:
                if first_heading:
                    first_heading = False
                else:
                    print(", ", end="")
                print(f"{key} : '{value}'", end="")
        print()

    @staticmethod
    def process_file_extension_line(line: str):
        # Remove the * at the start of the line
        #print(f"line: {line}")
        line = line.replace("*", "").strip()
        #print(f"line: {line}")
        # Split the line in to extensions and the description
        find_string_length = 3
        # Hyphen type 1
        first_hyphen_index = line.find(" – ")
        if first_hyphen_index == -1:
            # Hyphen type 2
            first_hyphen_index = line.find(" - ")
        if first_hyphen_index == -1:
            # Hyphen type 3
            first_hyphen_index = line.find(" − ")
        if first_hyphen_index == -1:
            find_string_length = 4
            # Hyphen type 1
            first_hyphen_index = line.find(" –– ")
            if first_hyphen_index == -1:
                # Hyphen type 2
                first_hyphen_index = line.find(" -- ")
            if first_hyphen_index == -1:
                # Hyphen type 3
                first_hyphen_index = line.find(" −− ")
        if first_hyphen_index == -1:
            print(f"No '-' found in line. Ignoring line: {line}")
            #input("Press Enter to continue ")
            return None
        else:
            results_array = []
            # We've found a hyphen so split the line
            extensions_string = FileTypes.remove_formatting_from_string(line[:first_hyphen_index])
            description_string = FileTypes.remove_formatting_from_string(line[first_hyphen_index + find_string_length:])
            #print(f"extensions_string: '{extensions_string}'")
            #print(f"description_string: '{description_string}'")
            extensions_array = extensions_string.split(",")
            # Custom Split Comma Separated Words Using re.split()
            pattern = ",\\s*"
            extensions_array = re.split(pattern, extensions_string)
            for extension in extensions_array:
                #print(f"extension: '{extension}'")
                tmp_array = [extension, description_string]
                results_array.append(tmp_array)
            return results_array

    @staticmethod
    def remove_formatting_from_string(temp_string: str) -> str:
        # Replace Double square bracket links with just their texts
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
        # Replace Single square bracket links with just their texts
        while True:
            single_open_square_brackets_index = temp_string.find("[")
            single_close_square_brackets_index = temp_string.find("]", single_open_square_brackets_index)
            if single_open_square_brackets_index == -1 or single_close_square_brackets_index == -1:
                # All links processed so break out of the loop
                break
            else:
                # We've found a link so replace it with text
                link_string = temp_string[single_open_square_brackets_index + 1:single_close_square_brackets_index]
                link_text = link_string[link_string.find(" ") + 1:]
                temp_string = temp_string[:single_open_square_brackets_index] + link_text + temp_string[single_close_square_brackets_index + 2:]
        # Replace 'Visible Anchors' with just it's text
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
        # Remove italics and bold formatting
        temp_string = temp_string.replace("'''''", "")
        temp_string = temp_string.replace("''''", "")
        temp_string = temp_string.replace("'''", "")
        temp_string = temp_string.replace("''", "")
        return temp_string

    @staticmethod
    def start():
        line_number = 0
        #heading_dictionary = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None}
        #heading_level_dictionary = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        heading_dictionary = {2: None, 3: None, 4: None}
        heading_level_dictionary = {2: 0, 3: 0, 4: 0}

        # CSV column headers
        csv_headers=['Category 2', 'Category 3', 'Category 4', 'Extension', 'Description']
        csv_rows=[]
        csv_filename = "file_types.csv"

        wiki_page_filename = "file_types.wikitext"
        wiki_page_content = None
        if os.path.isfile(wiki_page_filename):
            print("Loading file types from local storage")
            with open(wiki_page_filename, 'r', encoding="utf-8") as wiki_file:
                wiki_page_content = wiki_file.read()
        else:
            print("Downloading file types from Wikipedia")
            wiki_page_content = FileTypes.download_file_types()
            print("Saving file types to local storage")
            with open(wiki_page_filename, 'w', encoding="utf-8") as wiki_file:
                wiki_file.write(wiki_page_content)
        for line in wiki_page_content.splitlines():
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
                if heading_text.lower() == "see also" or heading_text.lower() == "external links" or heading_text.lower() == "references":
                    # Reached the end of the data so stop processing the file
                    break
                heading_dictionary[heading_level] = FileTypes.remove_formatting_from_string(heading_text)
                #print(f"heading_new : {heading_dictionary[heading_level]}")
                #if heading_text.count("|") > 0 and heading_text != heading_dictionary[heading_level]:
                #    break
                FileTypes.clear_heading_dictionary_below_level(heading_dictionary, heading_level)
                #print(f"{heading_dictionary}")
                #FileTypes.display_heading_values(heading_dictionary)
            else:
                # OTHER TEXT LINE
                if line_striped.startswith("*"):
                    # FILE EXTENSIONS
                    pass
                    results = FileTypes.process_file_extension_line(line_striped)
                    #print(f"results: {results}")
                    if results is not None:
                        for result in results:
                            extension = result[0]
                            description = result[1]
                            if description.find("</") != -1:
                                description = description[:description.find("<")]
                            #print(f"{extension} : {description}")
                            csv_rows.append([heading_dictionary[2], heading_dictionary[3], heading_dictionary[4], extension, description])
                else:
                    if len(line_striped) > 0:
                        pass
                        #print(f"line_striped: {FileTypes.remove_formatting_from_string(line_striped)}")

        with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
            # creating a CSV writer object
            writer = csv.writer(csv_file, delimiter='|')

            # writing headers
            writer.writerow(csv_headers)

            # writing rows
            writer.writerows(csv_rows)

        FileTypes.display_heading_level_counts(heading_level_dictionary)

        print("Complete")

if __name__ == "__main__":
    FileTypes.start()
    #FileTypes.download_file_types()


