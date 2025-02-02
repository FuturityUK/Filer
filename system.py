from subprocess import check_output
import subprocess
import platform
import os
import sys
from typing import List, Optional

class Windows:
    """ Class to execute Windows commands """

    POWERSHELL_COMMAND: str = "powershell.exe"
    #EXECUTION_POLICY_ARGUMENT: str = "-ExecutionPolicy RemoteSigned"
    EXECUTION_POLICY_ARGUMENT: str = ""
    COMMAND_ARGUMENT: str = "-command"
    FORMAT_LIST_ARGUMENT: str = "| Format-List"
    FORMAT_TABLE_ARGUMENT: str = "| Format-Table -Wrap -AutoSize"
    OUT_STRING_ARGUMENT: str = "| out-string -width 4096"

    __verbose = False

    def __init__(self):
        self.commands = {
            "dir_protected_directory": '"dir "C:\\Users\\Neil"',
            "list_disks": '"Get-Disk"'
        }

    def __vprint(self, string: str):
        if self.__verbose:
            print(string)

    @staticmethod
    def run_command(command_array: []) -> str:
        try:
            #p = subprocess.Popen(self.power_shell_command,  + command_string, stdout=sys.stdout)
            p = subprocess.Popen(command_array, stdout=subprocess.PIPE)
            #p = subprocess.Popen(command_string, stdout=subprocess.PIPE)
            out, err = p.communicate()
            if err is not None:
                err_utf_8 = err.decode('UTF-8')
                print(f"Error running command: \"{command_array}\"")
                print(f"Error: \"{err_utf_8}\"")
                exit(2)
        except FileNotFoundError as e:
            print(f"Error running command: \"{command_array}\"")
            print(f"Error: \"{e}\"")
            exit(2)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: \"{command_array}\"")
            print(f"Error: \"{e}\"")
            exit(2)
        # If we reached here, no error were detected
        out_utf_8 = out.decode('UTF-8')
        #print(f"out: {out_utf_8}")
        return out_utf_8

    def run_powershell_command(self, command_string: str) -> str:
        #command_array = ["powershell.exe", "-ExecutionPolicy RemoteSigned", "-command", command_string, "| out-string -width 4096"] # Potentially remove the out-string part for the listing creation
        command_array = [self.POWERSHELL_COMMAND,
                         self.EXECUTION_POLICY_ARGUMENT,
                         self.COMMAND_ARGUMENT,
                         command_string]
        return self.run_command(command_array)

    def run_powershell_command_with_value_per_line(self, command_string: str):
        #power_shell_command = "powershell.exe"
        #power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        #powershell_post_command_pipe_to_prevent_truncation = "| Format-List " + self.OUT_STRING_ARGUMENT
        #new_command_string = power_shell_command + " " + power_shell_command_args + " " + command_string + " " + powershell_post_command_pipe_to_prevent_truncation
        command_array = [self.POWERSHELL_COMMAND,
                         self.EXECUTION_POLICY_ARGUMENT,
                         self.COMMAND_ARGUMENT,
                         command_string,
                         self.FORMAT_LIST_ARGUMENT,
                         self.OUT_STRING_ARGUMENT]
        return self.run_command_with_value_per_line(command_array)

    def run_command_with_value_per_line(self, command_array: []):
        out_utf_8 = self.run_command(command_array)
        command_results = []
        dictionary_results = {}
        for line in out_utf_8.splitlines():
            #print(f"{line}")
            if len(line.strip()) == 0:
                # Start of a new dictionary
                if len(dictionary_results) != 0:
                    command_results.append(dictionary_results)
                    #print(dictionary_results)
                    #print("Saved Dictionary")
                dictionary_results = {}
                #print("Cleared Dictionary")
            else:
                # Values for dictionary
                colon_index = line.find(':')
                #print(f"colon_index: {colon_index}")
                key = line[:colon_index].strip()
                value = line[colon_index+1:].strip()
                #print(f"key: {key}")
                #print(f"value: {value}")
                dictionary_results[key] = value
                #print(f"dictionary_results[{key}] = {value}")
        if len(dictionary_results) != 0 and dictionary_results not in command_results:
            command_results.append(dictionary_results)
            # print(dictionary_results)
            # print("Saved Dictionary")
        return command_results

    def run_powershell_command_with_fix_width_output(self, command_string: str):
        #power_shell_command = "powershell.exe"
        #power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        #powershell_post_command_pipe_to_prevent_truncation = "| Format-Table -Wrap -AutoSize" +  " | out-string -width 4096"
        #new_command_string = power_shell_command + " " + power_shell_command_args +  " " + command_string +  " " + powershell_post_command_pipe_to_prevent_truncation
        command_array = [self.POWERSHELL_COMMAND,
                         self.EXECUTION_POLICY_ARGUMENT,
                         self.COMMAND_ARGUMENT,
                         command_string,
                         self.FORMAT_TABLE_ARGUMENT,
                         self.OUT_STRING_ARGUMENT]
        return self.run_command_with_fix_width_output(command_array)

    def run_command_with_fix_width_output(self, command_array: []):
        out_utf_8 = self.run_command(command_array)
        slices = []

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
        self.windows = self.is_windows()
        if self.windows:
            self.windows = Windows()
            self.unix = None
        else:
            self.windows = None
            self.unix = Linux()

    def get_logical_drives_details(self, disk_number: int = None):
        if self.windows:
            get_disk_parameters = ""
            if disk_number is not None:
                get_disk_parameters = f"-Number {disk_number}"
            return self.windows.run_powershell_command_with_value_per_line(f"get-disk {get_disk_parameters} | Select-Object -Property * | Format-List")
            #return self.windows.run_powershell_command_with_fix_width_output("Get-Disk")
            #return self.windows.run_command_with_fix_width_output("wmic diskdrive")

    def get_physical_drives_details(self, device_id: int = None):
        if self.windows:
            get_disk_parameters = ""
            if device_id is not None:
                get_disk_parameters = f"-DeviceId {device_id}"
            return self.windows.run_powershell_command_with_value_per_line(f"Get-PhysicalDisk {get_disk_parameters} | Select-Object -Property * | Format-List")

    def get_partition_details(self, drive_number: int = None):
        if self.windows:
            get_disk_parameters = ""
            if drive_number is not None:
                get_disk_parameters = f"-DiskNumber {drive_number}"
            return self.windows.run_powershell_command_with_value_per_line(f"Get-Partition {get_disk_parameters} | Select-Object -Property * | Format-List")

    def get_volumes(self, mount: int = None):
        volumes = []
        if self.windows:
            #volumes = self.windows.run_powershell_command_with_fix_width_output("Get-Volume")
            volumes = self.windows.run_powershell_command_with_value_per_line("Get-Volume | Sort-Object -Property DriveLetter | Select-Object -Property * | Format-List")
            #all_volumes = self.windows.run_command_with_fix_width_output("wmic volume")
        if mount is None:
            return volumes
        elif mount:
            # Only return mounted volumes
            mounted_volumes = []
            for volume_dictionary in volumes:
                if len(volume_dictionary['DriveLetter'].strip()) != 0 and volume_dictionary['OperationalStatus'].strip() != "Unknown":
                    mounted_volumes.append(volume_dictionary)
            return mounted_volumes

    def get_disk_number_for_drive_letter(self, drive_letter: str):
        if self.windows:
            return self.windows.run_powershell_command('(Get-Partition -ErrorAction SilentlyContinue -DriveLetter (Get-Item "'+drive_letter+'").PSDrive.Name).DiskNumber').strip()
        else:
            return None

    def create_path_listing(self, path: str, listing_filename: str):
        if self.windows:
            #print(f"path: {path}")
            listing_powershell_command = f'Get-ChildItem -Path "{path}" -ErrorAction SilentlyContinue -Recurse -Force | Select-Object Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "{listing_filename}"'
            #listing_powershell_command = f'Get-ChildItem -Path \"{path}\" -Recurse -Force'
            #print(f"listing_powershell_command: {listing_powershell_command}")
            return self.windows.run_powershell_command(listing_powershell_command).strip()
        else:
            return None

    def does_path_listing_exit(self, listing_filename: str):
        if os.path.isfile(listing_filename):
            selection = self.select_option(f"Temporary listing file exits. Do you want to delete it and continue? ")
            print(f"selection: {selection}")




    @staticmethod
    def is_windows():
        return True if platform.system().lower() == "windows" else False

    @staticmethod
    def is_macos():
        return True if platform.system().lower() == "darwin" else False

    @staticmethod
    def is_linux():
        return True if platform.system().lower() == "linux" else False

    @staticmethod
    def is_java():
        return True if platform.system().lower() == "java" else False

    @staticmethod
    def is_android():
        return True if platform.system().lower() == "android" else False

    @staticmethod
    def is_ios():
        return True if platform.system().lower() == "ios" else False

    @staticmethod
    def is_ipados():
        return True if platform.system().lower() == "ipados" else False

    @staticmethod
    def is_unix_like():
        return True if os.name == "posix" else False

    @staticmethod
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

    @staticmethod
    def get_system_information_examples():
        # Examples:
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

    @staticmethod
    def select_option(message: str, options=None, options_descriptions=None, options_results=None):
        # print(f"length options: {len(options)}")
        # print(f"length options_descriptions: {len(options_descriptions)}")

        if options is None:
            options = ['Y', 'N']
        if options_descriptions is None:
            options_descriptions = []
        if options_results is None:
            options_results = []
        print(f"{message}")
        internal_selection = ""
        while internal_selection not in options or internal_selection.lower() not in options:
            if options_descriptions is not None and len(options_descriptions) > 0:
                if len(options) != len(options_descriptions):
                    print("the size of the options and the options descriptions don't match")
                    print("Exiting...")
                    exit(2)
                else:
                    for index, option in enumerate(options):
                        print(f"{option}) - {options_descriptions[index]}")
            internal_selection = input(f"Options: {options}? ")
            if options_results is not None and len(options_results) > 0:
                # If we have been provided results, return the result matching the internal_selection
                if len(options) != len(options_results):
                    print("the size of the options and the options results don't match")
                    print("Exiting...")
                    exit(2)
                else:
                    for index, option in enumerate(options):
                        # print(f"{internal_selection.lower()} ?? {option.lower()}")
                        if internal_selection.lower() == option.lower():
                            return options_results[index]
        return internal_selection

if __name__ == "__main__":

    sys_info = System.get_system_information()
    print(f"system_information: {sys_info}")

