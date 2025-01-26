from subprocess import check_output
import subprocess
import platform
import os
import sys
import string

def is_windows():
    return True if platform.system().lower() == "windows" else False

def is_macos():
    return True if platform.system().lower() == "darwin" else False

def is_linux():
    return True if platform.system().lower() == "linux" else False

def is_java():
    return True if platform.system().lower() == "java" else False

def is_android():
    return True if platform.system().lower() == "android" else False

def is_ios():
    return True if platform.system().lower() == "ios" else False

def is_ipados():
    return True if platform.system().lower() == "ipados" else False

def is_unix_like():
    return True if os.name == "posix" else False

def get_system_information():
    system_information = {'system': platform.system(), 'os name': os.name, 'system platform': sys.platform,
                          'platform release': platform.release(), 'platform version': platform.version(),
                          'platform platform': platform.platform(),
                          'platform platform terse': platform.platform(terse=True),
                          'platform platform aliased': platform.platform(aliased=True)}
    if system_information['system'] == "Windows":
        # Windows specific functions
        system_information['windows edition'] = platform.win32_edition()
        # Windows 11 Home = "Core"
        system_information['windows is iot'] = platform.win32_is_iot()
        # Windows 11 Home = False
    elif system_information['system'] == "Darwin":
        # MacOS specific function
        system_information['mac version'] = platform.mac_ver()
    elif system_information['system'] == "Linux":
        # We could import the "distro" module and get further Linux information (see below)
        # but I've decided not to include them to focus on using on modules built into Python
        # for easy of installation
        do_nothing = True
        #print(distro.name())
        # Ubuntu
        #print(distro.id())
        # ubuntu
        #print(distro.version())
        # 22.04
    return system_information

    # Examples:
def get_system_information_examples():
    # MacOS Sonoma 14.0
    macos = {
        'system': 'Darwin',
        'os name': 'posix',
        'system platform': 'darwin',
        'platform release': '23.0.0',
        'platform version': 'Darwin Kernel Version 23.0.0: Fri Sep 15 14:42:57 PDT 2023; root:xnu-10002.1.13~1/RELEASE_ARM64_T8112',
        'platform platform': 'macOS-14.0-arm64-arm-64bit',
        'mac version': ('14.0', ('', '', ''), 'arm64')
    }
    # Windows 11 Pro
    win = {
        'system': 'Windows',
        'os name': 'nt',
        'system platform': 'win32',
        'platform release': '11',
        'platform version': '10.0.26100',
        'platform platform': 'Windows-11-10.0.26100-SP0',
        'platform platform terse': 'Windows-11',
        'platform platform aliased': 'Windows-11-10.0.26100-SP0',
        'windows edition': 'Professional',
        'windows is iot': False
    }
    # Ubuntu 22.04.3 LTS
    ubuntu = {
        'system': 'Linux',
        'os name': 'posix',
        'system platform': 'linux',
        'platform release': '5.15.0-86-generic',
        'platform version': '#96-Ubuntu SMP Wed Sep 20 08:23:49 UTC 2023',
        'platform platform': 'Linux-5.15.0-86-generic-x86_64-with-glibc2.35',
    }


def display_dictionary(results_array: []):
    #print(f"results_array length: {len(results_array)}")
    print("[")
    results_array_length = len(results_array)
    array_element_counter = 0
    for results_dictionary in results_array:
        array_element_counter += 1
        print("  {")
        results_dictionary_length = len(results_dictionary)
        key_counter = 0
        for key, value in results_dictionary.items():
            key_counter += 1
            if key_counter != results_dictionary_length:
                print(f"    '{key}': '{value}',")
            else:
                print(f"    '{key}': '{value}'")
        if array_element_counter != results_array_length:
            print("  },")
        else:
            print("  }")
    print("]")

class Windows:
    """ Class to execute Windows commands """

    __verbose = False

    def __init__(self):
        self.commands = {
            "dir_protected_directory": '"dir "C:\\Users\\Neil"',
            "list_disks": '"Get-Disk"'
        }

    def __vprint(self, string: str):
        if self.__verbose:
            print(string)

    def run_powershell_command_with_fix_width_output(self, command_string: str):
        power_shell_command = "powershell.exe"
        power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        powershell_post_command_pipe_to_prevent_truncation = "| Format-Table -Wrap -AutoSize"
        command_string = power_shell_command + " " + power_shell_command_args +  " " + command_string +  " " + powershell_post_command_pipe_to_prevent_truncation
        return self.run_command_with_fix_width_output(command_string)

    def run_command_with_fix_width_output(self, command_string: str):
        try:
            #p = subprocess.Popen(self.power_shell_command,  + command_string, stdout=sys.stdout)
            p = subprocess.Popen(command_string, stdout=subprocess.PIPE)
            #p = subprocess.Popen(command_string, stdout=subprocess.PIPE)
            out, err = p.communicate()
            if err is not None:
                err_utf_8 = err.decode('UTF-8')
                print(f"Error running command: \"{command_string}\"")
                print(f"Error: \"{err_utf_8}\"")
                exit(2)
        except FileNotFoundError as e:
            print(f"Error running command: \"{command_string}\"")
            print(f"Error: \"{e}\"")
            exit(2)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: \"{command_string}\"")
            print(f"Error: \"{e}\"")
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

        # Find field widths within the fixed width output.
        # The first non-blank line will be the header line. For wmic commands this line will define the field widths
        # The second next line may contain dashes which defines the field width for PowerShell Get- commands
        # Hunt for line with headers that define the width of the columns as the won't have spaces in them
        lines_with_content = 0
        for line in out_utf_8.splitlines():
            if len(line.rstrip()) > 0:
                lines_with_content += 1
                self.__vprint(f"lines_with_content: {lines_with_content}")
                if lines_with_content >= 2 and not line.startswith("--"):
                    # Dash line is missing, so this must be a wmic command so with have our widths already
                    self.__vprint("Dash line is missing from content line 2")
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
                    if self.__verbose:
                        print(char, end="")
                    if (last_char == ' ') and (char != ' '):
                        field_length = i - char_offset
                        char_offset = i
                        field_widths.append(field_length)
                # Append Path field width
                field_length = line_length - char_offset
                # Check that the longest path doesn't get truncated
                field_widths.append(field_length)
                # self.__vprint()
                # self.__vprint(field_widths)
                # Create slices
                offset = 0
                for width in field_widths:
                    slices.append(slice(offset, offset + width))
                    offset += width
                self.__vprint("")
                self.__vprint(slices)
                header_line_processed = True
                # processing_data_lines_start_time = time.time()
                # self.__vprint(dash_field_lengths)
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
                    self.__vprint(line_right_strip)
                    pieces_array = [line_right_strip[slice] for slice in slices]
                    pieces_right_strip_array = [piece.rstrip() for piece in pieces_array]
                    #self.__vprint(pieces_right_strip_array)
                    if len(pieces_right_strip_array) > 0:
                        if not first_content_line_found:
                            headers_array = pieces_right_strip_array
                            self.__vprint(f"HEADERS: {headers_array}")
                            first_content_line_found = True
                        else:
                            self.__vprint(f"VALUES : {pieces_right_strip_array}")
                            if len(headers_array) != len(pieces_right_strip_array):
                                print("headers array and values array sizes don't match.")
                                print(f"Length headers_array: {len(headers_array)}")
                                print(f"Length pieces_right_strip_array: {len(pieces_right_strip_array)}")
                                exit(2)
                            else:
                                values_dictionary = {}
                                for index, header_name in enumerate(headers_array):
                                    values_dictionary[header_name] = pieces_right_strip_array[index]
                                self.__vprint(f"values_dictionary: {values_dictionary}")
                                command_results.append(values_dictionary)
        return command_results


class Linux:
    """ Class to execute Linux commands """

class System:
    """ Class to execute System commands """

    def __init__(self):
        self.windows = is_windows()
        if self.windows:
            self.windows = Windows()
            self.unix = None
        else:
            self.windows = None
            self.unix = Linux()

    def get_drives_details(self):
        if self.windows:
            #return self.windows.run_powershell_command_with_fix_width_output("Get-Disk")
            return self.windows.run_command_with_fix_width_output("wmic diskdrive")

    def get_volumes(self):
        if self.windows:
            return self.windows.run_command_with_fix_width_output("wmic volume")


if __name__ == "__main__":
    sys_info = get_system_information()
    print(f"system_information: {sys_info}")

    system = System()

    drives = system.get_drives_details()
    print(f"drives_details: {drives}")
    display_dictionary(drives)

    volumes = system.get_volumes()
    print(f"volumes: {volumes}")
#    display_dictionary(volumes)

    #available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    #print(f"available_drives: {available_drives}")

    #import psutil
    #partitions = psutil.disk_partitions()
    #for p in partitions:
    #    print(p.mountpoint, psutil.disk_usage(p.mountpoint).percent)

    #ps = PowerShell()

    #ps.run_command(ps.commands["list_disks"])