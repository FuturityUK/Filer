from subprocess import check_output
import subprocess
import sys

class PowerShell:
    """ Class to execute PowerShell commands """

    def __init__(self):
        self.power_shell_command = "powershell.exe"
        self.power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        self.power_shell_command_full_output = "| Format-Table -Wrap -AutoSize "
        self.commands = {
            "dir_protected_directory": '"dir "C:\\Users\\Neil"',
            "get disk": '"Get-Disk"',
            "wmic diskdrive": 'wmic diskdrive get',
            "wmic volume": 'wmic volume get'
        }

    def run_existing_command(self, command_name: str):
        try:
            return self.run_command(ps.commands[command_name])
        except KeyError as err:
            print(f"\"{command_name}\" command name not found.")
            print(f"KeyError: {err}")

    def run_command(self, command_string: str):
        #p = subprocess.Popen(self.power_shell_command,  + command_string, stdout=sys.stdout)
        p = subprocess.Popen(self.power_shell_command + " " + self.power_shell_command_args +  " " + command_string +  " " +  self.power_shell_command_full_output, stdout=subprocess.PIPE)
        #p = subprocess.Popen(command_string, stdout=subprocess.PIPE)
        out, err = p.communicate()
        if err is not None:
            err_utf_8 = err.decode('UTF-8')
            print(f"Error running command: \"{command_string}\"")
            print(f"Error: \"{err_utf_8}\"")
            exit(2)
        # If we reached here, no error were detected
        out_utf_8 = out.decode('UTF-8')
        #print(f"out: {out_utf_8}")

        header_line_processed = False
        field_widths_processed = False
        process_next_line = False
        line_number = 0
        lines_processed = 0
        field_widths = []
        slices = []
        offset = 0
        root_entity_not_found = True
        directory_dictionary = {}
        last_saved_directory_name = "" # Shouldn't use None because we can't use string operations on a None type
        last_saved_directory_id = 0 # IDs start at 1 so this 0 will never be used.

        # Hunt for line with dashes that define the width of the columns
        #for line in out_utf_8.splitlines():
        #    if line.startswith("--"):
        #        # Calculate max column widths from line, as each path and hence line could be a different length.
        #        char = '-'
        #        last_char = '-'
        #        char_offset = 0
        #        line_length = len(line)
        #        for i in range(line_length):
        #            last_char = char
        #            char = line[i]
        #            print(char, end="")
        #            if (last_char == ' ') and (char == '-'):
        #                field_length = i - char_offset
        #                char_offset = i
        #                field_widths.append(field_length)
        #        # Append Path field width
        #        field_length = line_length - char_offset
        #        # Check that the longest path doesn't get truncated
        #        field_widths.append(field_length)
        #        # print()
        #        # print(field_widths)
        #        # Create slices
        #        offset = 0
        #        for width in field_widths:
        #            slices.append(slice(offset, offset + width))
        #            offset += width
        #        print(slices)
        #        field_widths_processed = True
        #        #processing_data_lines_start_time = time.time()
        #        #print(dash_field_lengths)
        #        break

        # Find field widths within the fixed width output.
        # The first non-blank line will be the header line. For wmic commands this line will define the field widths
        # The second next line may contain dashes which defines the field width for PowerShell Get- commands
        # Hunt for line with headers that define the width of the columns as the won't have spaces in them
        lines_with_content = 0
        for line in out_utf_8.splitlines():
            if len(line.rstrip()) > 0:
                lines_with_content += 1
                print(f"lines_with_content: {lines_with_content}")
                if lines_with_content >= 2 and not line.startswith("--"):
                    # Dash line is missing, so this must be a wmic command so with have our widths already
                    print("Dash line is missing from content line 2")
                    break
                # If we have reached here, this is either a header line, or a dash line.
                # As the dash line is after the header line in the Get- command, it will replace the bad field widths with the correct ones
                # Calculate max column widths from line, as each path and hence line could be a different length.
                field_widths = []
                slices = []
                char = '-'
                last_char = '-'
                char_offset = 0
                line_length = len(line)
                for i in range(line_length):
                    last_char = char
                    char = line[i]
                    print(char, end="")
                    if (last_char == ' ') and (char != ' '):
                        field_length = i - char_offset
                        char_offset = i
                        field_widths.append(field_length)
                # Append Path field width
                field_length = line_length - char_offset
                # Check that the longest path doesn't get truncated
                field_widths.append(field_length)
                # print()
                # print(field_widths)
                # Create slices
                offset = 0
                for width in field_widths:
                    slices.append(slice(offset, offset + width))
                    offset += width
                print("")
                print(slices)
                header_line_processed = True
                # processing_data_lines_start_time = time.time()
                # print(dash_field_lengths)
                #break

        # Process the output again, but this time extract the headers and the data
        command_results = []
        headers_array = None
        first_content_line_found = False
        for line in out_utf_8.splitlines():
            line_right_strip = line.rstrip()
            if len(line_right_strip) == 0:
                continue
            else:
                if not line_right_strip.startswith("--"):
                    print(line_right_strip)
                    pieces_array = [line_right_strip[slice] for slice in slices]
                    pieces_right_strip_array = [piece.rstrip() for piece in pieces_array]
                    #print(pieces_right_strip_array)
                    if len(pieces_right_strip_array) > 0:
                        if not first_content_line_found:
                            headers_array = pieces_right_strip_array
                            print(f"HEADERS: {headers_array}")
                            first_content_line_found = True
                        else:
                            print(f"VALUES : {pieces_right_strip_array}")
                            if len(headers_array) != len(pieces_right_strip_array):
                                print("headers array and values array sizes don't match.")
                                print(f"Length headers_array: {len(headers_array)}")
                                print(f"Length pieces_right_strip_array: {len(pieces_right_strip_array)}")
                                exit(2)
                            else:
                                values_dictionary = {}
                                for index, header_name in enumerate(headers_array):

                                    values_dictionary[header_name] = pieces_right_strip_array[index]
                                print(f"values_dictionary: {values_dictionary}")
                                command_results.append(values_dictionary)
        return command_results

    def display_command_results(self, results_array: []):
        for results_dictionary in results_array:
            print(f"command_results:")
            print(f"- disk_details:")
            for key, value in results_dictionary.items():
                print(f"  - \"{key}\": \"{value}\"")

ps = PowerShell()

#disks_details = ps.run_command("Get-Disk")
#disks_details = ps.run_existing_command("wmic diskdrive")

disks_details = ps.run_existing_command("wmic volume")

ps.display_command_results(disks_details)

#yes_no = input("Yes / No? ")