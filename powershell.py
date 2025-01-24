from subprocess import check_output
import subprocess
import sys

class PowerShell:
    """ Class to execute PowerShell commands """

    def __init__(self):
        self.power_shell_command = "powershell.exe"
        self.power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        self.commands = {
            "dir_protected_directory": '"dir "C:\\Users\\Neil"',
            "list_disks": '"Get-Disk"'
        }

    def run_command(self, command_string: str):
        #p = subprocess.Popen(self.power_shell_command,  + command_string, stdout=sys.stdout)
        p = subprocess.Popen(self.power_shell_command + " " + self.power_shell_command_args +  " " + command_string, stdout=subprocess.PIPE)
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
        for line in out_utf_8.splitlines():
            #line_right_strip = line.rstrip()
            #print(line_right_strip)
            if line.startswith("--"):
                # Calculate max column widths from line, as each path and hence line could be a different length.
                char = '-'
                last_char = '-'
                char_offset = 0
                line_length = len(line)
                for i in range(line_length):
                    last_char = char
                    char = line[i]
                    print(char, end="")
                    if (last_char == ' ') and (char == '-'):
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
                print(slices)
                field_widths_processed = True
                #processing_data_lines_start_time = time.time()
                #print(dash_field_lengths)
                break

        # Process the output again, but this time extract the headers and the data
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
                    if len(pieces_right_strip_array) > 0 and pieces_right_strip_array[0] != "":
                        print(pieces_right_strip_array)


ps = PowerShell()

ps.run_command(ps.commands["list_disks"])