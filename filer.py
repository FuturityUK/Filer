# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
# Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

'''
input_filename = "C:\\Data\\ws1,e.fwf"
output_filename = "C:\\Data\\ws1,e.csv.txt"
database_filename = "I:\\FileProcessorDatabase\\database.sqlite"
'''

from file_system_processors import PowerShellFilesystemListing
from database import Database
import tracemalloc
import argparse
import os.path
import collections.abc
from system import System
from data import Data
from format import Format
import socket
import logging

class Filer:

    VOLUME_DICT_INDEX: int = 0
    LOGICAL_DICT_INDEX: int = 1
    PHYSICAL_DICT_INDEX: int = 2

    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf'

    def __init__(self):
        self.database = None
        self.memory_stats = False
        self.logical_disk_array = None
        self.physical_disk_array = None
        self.volumes_array = None
        self.partitions_array = None
        self.system = System()

    def set_memory_stats(self, memory_stats):
        self.memory_stats = memory_stats

    def clean_up_and_quit(self):
        # Now that the subcommands have been run, close the database cleanly
        self.database.close_database()
        if self.memory_stats:
            # Stop tracing memory allocations
            tracemalloc.stop()
        # Exit normally
        exit()

    def find(self, args: []):
        print(f"Finding filenames matching \"{args.filename}\"", end="")
        if args.label is not None:
            print(f" with label \"{args.label}\"")
        else:
            print(":")
        self.database.find_filenames_exact_match(args.filename, args.label)

    def like(self, args: []):
        print(f"Finding filenames like \"{args.search}\"", end="")
        if args.label is not None:
            print(f" with label \"{args.label}\"")
        else:
            print(":")
        self.database.find_filenames_like(args.search, args.label)

    def vacuum(self):
        print(f"Vacuuming database. This may take a while depending on the your database size.")
        self.database.vacuum()
        print(f"Vacuuming finished.")

    def reset(self, args: []):
        print(f"Not implemented yet")

    def import_listing(self, args: []):
        print(f"Import subcommand: Needs Further Testing !!!")
        powershell_filesystem_listing = PowerShellFilesystemListing(self.database, args.label, args.filename)

        if args.verbose is not None:
            powershell_filesystem_listing.set_verbose(args.verbose)
        if args.test is not None:
            powershell_filesystem_listing.set_test(args.test)
        if args.make is not None:
            powershell_filesystem_listing.set_make(args.make)
        if args.model is not None:
            powershell_filesystem_listing.set_model(args.model)
        if args.serial is not None:
            powershell_filesystem_listing.set_serial_number(args.serial)
        if args.combined is not None:
            powershell_filesystem_listing.set_combined(args.combined)
        if args.hostname is not None:
            powershell_filesystem_listing.set_hostname(args.hostname)
        if args.prefix is not None:
            powershell_filesystem_listing.set_prefix(args.prefix)

        powershell_filesystem_listing.set_memory_stats(self.memory_stats)
        powershell_filesystem_listing.save_to_database()

        powershell_filesystem_listing.import_listing()

    def interactive(self, args: []):
        print(f"Entering Interactive Mode ...")
        self.process_drive(args)

    def load_volume_drive_details(self):
        logging.info("Finding Logical Drives ...")
        self.logical_disk_array = self.system.get_logical_drives_details()
        # display_array_of_dictionaries(self.logical_disk_array)
        # print(f"logical_disk_array: {self.logical_disk_array}")

        logging.info("Finding Physical Drives ...")
        self.physical_disk_array = self.system.get_physical_drives_details()
        # print(f"physical_disk_array: {self.physical_disk_array}")

        logging.info("Finding Volumes ...")
        self.volumes_array = self.system.get_volumes(True)
        # print(f"volumes: {self.volumes_array}")
        # display_array_of_dictionaries(self.volumes_array)
        # display_diff_dictionaries(volumes[0], volumes[1])

        # print("Finding Partitions ...")
        # self.partitions_array = self.system.get_partition_details()
        # print(f"physical_disk_array: {self.partitions_array}")

    def create_volume_options(self) -> []:
        logging.info("Matching Volumes to Drives ...")
        option_number = 1
        options = []
        for volume_dictionary in self.volumes_array:
            volume_array_of_dicts = []
            volume_array_of_dicts.append(volume_dictionary)
            drive_letter = f'{volume_dictionary['DriveLetter']}:'
            disk_number = self.system.get_disk_number_for_drive_letter(drive_letter)
            # print(f"{drive_letter} is on drive {disk_number}")

            volume_info_line = f"{volume_dictionary['DriveLetter']}: \"{volume_dictionary['FileSystemLabel']}\" {Format.format_storage_size(int(volume_dictionary['Size']), True, 1)}, {volume_dictionary['FileSystemType']} ({volume_dictionary['HealthStatus']})"
            if len(disk_number.strip()) != 0:
                logical_disk_dictionary = Data.find_dictionary_in_array(self.logical_disk_array, "DiskNumber",
                                                                        disk_number)
                volume_array_of_dicts.append(logical_disk_dictionary)
                physical_disk_dictionary = Data.find_dictionary_in_array(self.physical_disk_array, "DeviceId",
                                                                         disk_number)
                volume_array_of_dicts.append(physical_disk_dictionary)
                if logical_disk_dictionary is not None:
                    volume_info_line += f" / {logical_disk_dictionary['BusType']} {physical_disk_dictionary['MediaType']}: {logical_disk_dictionary['Manufacturer']}, {logical_disk_dictionary['Model']}, SN: {logical_disk_dictionary['SerialNumber']} ({logical_disk_dictionary['HealthStatus']}))"
                else:
                    volume_info_line += ""
            option = [str(option_number), volume_info_line, volume_array_of_dicts]
            options.append(option)
            option_number += 1
        return options

    def get_values_for_import_listing(self, result_array: []) -> {}:
        import_listing_values = {}
        result_array_length = len(result_array)

        # Get values from the volume dictionary
        volume_dictionary = result_array[self.VOLUME_DICT_INDEX]
        import_listing_values["drive_letter"] = volume_dictionary['DriveLetter']
        import_listing_values["label"] = volume_dictionary['FileSystemLabel']

        # Get values from the logical drive dictionary, but only if it exists
        if result_array_length > 1:
            logical_disk_dictionary = result_array[self.LOGICAL_DICT_INDEX]
            import_listing_values["make"] = logical_disk_dictionary['Manufacturer']
            import_listing_values["model"] = logical_disk_dictionary['Model']
            import_listing_values["serial_number"] = logical_disk_dictionary['SerialNumber']
        else:
            import_listing_values["make"] = ""
            import_listing_values["model"] = ""
            import_listing_values["serial_number"] = ""

        import_listing_values["hostname"] = socket.gethostname()
        return import_listing_values

    @staticmethod
    def display_import_listing_values(import_listing_values: {}):
        print("Information to be saved into the database:")
        print(f"  Drive : {import_listing_values["drive_letter"]}:")
        print(f"  Label : {import_listing_values["label"]}")
        print(f"  Make  : {import_listing_values["make"]}")
        print(f"  Model : {import_listing_values["model"]}")
        print(f"  S / N : {import_listing_values["serial_number"]}")
        print(f"  Host  : {import_listing_values["hostname"]}")

    def process_drive(self, args: []):
        temp_listing_filename = args.filename

        while True:
            self.load_volume_drive_details()

            options = self.create_volume_options()

            # Add Rescan option
            options.append(System.OPTION_RESCAN)
            # Add Exit option
            options.append(System.OPTION_EXIT)

            result_array = System.select_option("Please select a volume to process?", options)
            # Detect result_array type as we may have an exit command, or a data structure we've been asked to process
            if isinstance(result_array, str):
                # Test if result is a string first as strings are technically arrays as well
                # print(f"String result: {result_array}")
                if result_array == System.OPTION_RESCAN_CHAR:
                    continue  # Skip the rest of the code and rescan at the beginning of the WHILE loop
                elif result_array == System.OPTION_EXIT_CHAR:
                    print("Exiting ...")
                    exit()
                else:
                    print("Invalid result")
                    print("Exiting ...")
                    break  # Leave the interactive loop
            elif isinstance(result_array, collections.abc.Sequence):
                # display_array_of_dictionaries(result_array)

                import_listing_values = self.get_values_for_import_listing(result_array)

                while True:
                    self.display_import_listing_values(import_listing_values)

                    result = System.select_option("Please select one of the following options:", [System.OPTION_PROCEED, System.OPTION_CHANGE_LABEL, System.OPTION_RESCAN, System.OPTION_EXIT])
                    if result == System.OPTION_PROCEED_CHAR:
                        print(f"Processing Volume {import_listing_values["drive_letter"]}: ...")
                        output = self.system.create_path_listing(import_listing_values["drive_letter"] + ':\\', temp_listing_filename)
                        # print(f"create_path_listing output: {output}")
                        powershell_filesystem_listing = PowerShellFilesystemListing(self.database, import_listing_values["label"],
                                                                                    temp_listing_filename)
                        if args.verbose is not None:
                            powershell_filesystem_listing.set_verbose(args.verbose)
                        if args.test is not None:
                            powershell_filesystem_listing.set_test(args.test)

                        powershell_filesystem_listing.set_make(import_listing_values["make"])
                        powershell_filesystem_listing.set_model(import_listing_values["model"])
                        powershell_filesystem_listing.set_serial_number(import_listing_values["serial_number"])
                        # powershell_filesystem_listing.set_combined(args.combined)
                        powershell_filesystem_listing.set_hostname(import_listing_values["hostname"])
                        # powershell_filesystem_listing.set_prefix(args.prefix)
                        powershell_filesystem_listing.set_memory_stats(self.memory_stats)
                        powershell_filesystem_listing.save_to_database()
                        import_listing_success = powershell_filesystem_listing.import_listing()
                        if import_listing_success:
                            print(f"Volume {import_listing_values["drive_letter"]}: Processed Successfully...")
                        break

                    elif result == System.OPTION_CHANGE_LABEL_CHAR:
                        print(f"Current Label: {import_listing_values["label"]}")
                        label = input("Please enter a new label: ")
                    elif result == System.OPTION_RESCAN_CHAR:
                        continue  # Skip the rest of the code and rescan at the beginning of the WHILE loop
                    elif result == System.OPTION_EXIT_CHAR:
                        print("Exiting ...")
                        break
                    else:
                        print("Invalid result")

            print("Rescanning ...")

    @staticmethod
    def add_db_and_verbose_to_parser(parser):
        parser.add_argument("-d", "--db", default="database.sqlite",
                                   help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
        parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")

    def start(self):

        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

        parser=argparse.ArgumentParser(
        #    prog='Filer',
        #    epilog='Text at the bottom of help',
            description="Filer - File Cataloger")
        parser.add_argument("-f", "--filename", default="tmp_listing.fwf", help="filename (including path) that will be used when creating temporary listing files. Default: '"+self.DEFAULT_TEMP_LISTING_FILE+"'")
        parser.add_argument("-t", "--test", action="store_true", help="test input file without modifying the database")
        self.add_db_and_verbose_to_parser(parser)

        args=parser.parse_args()

        # Debug
        #print(f"args: '{args}'")
        #print(f"subcommand: '{args.subcommand}'")
        #quit()

        # The following subcommands all require a database
        database_filename = args.db

        # Does the database file exit?
        create_tables = False
        abspath_database_filename = os.path.abspath(database_filename)
        directory_name = os.path.dirname(abspath_database_filename)
        if not os.path.exists(directory_name):
            print(f"\"{directory_name}\" directory in your database filename path, does not exist!")
            print("The directory must exist before a new database can be created there. Exiting")
            exit(2)

        if not os.path.isfile(database_filename):
            # Database file doesn't exist
            # Ask user if they want to create a new database file?
            print(f"Database file doesn't exist at location: \"{os.path.abspath(database_filename)}\"")
            #create_database_answer = input("Do you want to create a new database there? ")
            create_database_answer = System.select_option("Do you want to create a new database there? ")
            #if create_database_answer.lower() == "y" or create_database_answer.lower() == "yes":
            if create_database_answer:
                create_tables = True
            else:
                print("Database not created. Exiting")
                exit(2)

        # If not, ask the user if they want to create a new database at the specified location (give the full path as well)

        self.database = Database(database_filename, create_tables)
        self.database.set_verbose_mode(args.verbose)
        if create_tables:
            self.database.create_database_structure()

        self.interactive(args)

        # Clean up and exit
        self.clean_up_and_quit()

if __name__ == "__main__":
    filer = Filer()
    filer.start()

