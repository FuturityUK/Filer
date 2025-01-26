from subprocess import check_output
import subprocess
import platform
import os
import sys
import string

class System:
    """ Class to execute PowerShell commands """

    def __init__(self):
        self.power_shell_command = "powershell.exe"
        self.power_shell_command_args = "-ExecutionPolicy RemoteSigned -command"
        self.commands = {
            "dir_protected_directory": '"dir "C:\\Users\\Neil"',
            "list_disks": '"Get-Disk"'
        }

    def run_powershell_command(self, command_string: str):
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

    # Examples:
    def get_system_information(self):
        system_information = {}
        system_information['system'] = platform.system()
        system_information['os name'] = os.name
        system_information['system platform'] = sys.platform
        system_information['platform release'] = platform.release()
        system_information['platform version'] = platform.version()
        system_information['platform platform'] = platform.platform()
        system_information['platform platform terse'] = platform.platform(terse=True)
        system_information['platform platform aliased'] = platform.platform(aliased=True)
        if system_information.get('system') == "Windows":
            # Windows specific functions
            system_information['windows edition'] = platform.win32_edition()
            # Windows 11 Home = "Core"
            system_information['windows is iot'] = platform.win32_is_iot()
            # Windows 11 Home = False
        elif system_information.get('system') == "Darwin":
            # MacOS specific function
            system_information['mac version'] = platform.mac_ver()
        elif system_information.get('system') == "Linux":
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

    def is_windows(self):
        if platform.system() == "Windows":
            return True
        else:
            return False

    def is_macos(self):
        if platform.system() == "Darwin":
            return True
        else:
            return False

    def is_linux(self):
        if platform.system() == "Linux":
            return True
        else:
            return False

    def is_unix(self):
        if os.name == "posix":
            return True
        else:
            return False

    def get_system_information_examples(self):
        """
        MacOS Sonoma 14.0
        {
            'system': 'Darwin',
            'os name': 'posix',
            'system platform': 'darwin',
            'platform release': '23.0.0',
            'platform version': 'Darwin Kernel Version 23.0.0: Fri Sep 15 14:42:57 PDT 2023; root:xnu-10002.1.13~1/RELEASE_ARM64_T8112',
            'platform platform': 'macOS-14.0-arm64-arm-64bit',
            'mac version': ('14.0', ('', '', ''), 'arm64')
        }

        Windows 11 Pro
        {
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

        Ubuntu 22.04.3 LTS
        {
            'system': 'Linux',
            'os name': 'posix',
            'system platform': 'linux',
            'platform release': '5.15.0-86-generic',
            'platform version': '#96-Ubuntu SMP Wed Sep 20 08:23:49 UTC 2023',
            'platform platform': 'Linux-5.15.0-86-generic-x86_64-with-glibc2.35',
        }
        """

system = System()
system_information = system.get_system_information()
print(f"system_information: {system_information}")

available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
print(f"available_drives: {available_drives}")

#import psutil
#partitions = psutil.disk_partitions()
#for p in partitions:
#    print(p.mountpoint, psutil.disk_usage(p.mountpoint).percent)

#ps = PowerShell()

#ps.run_command(ps.commands["list_disks"])