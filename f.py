# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
# Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

"""
input_filename = "C:\\Data\\ws1,e.fwf"
output_filename = "C:\\Data\\ws1,e.csv.txt"
database_filename = "I:\\FileProcessorDatabase\\database.sqlite"
"""
import sys

from file_system_processors import PowerShellFilesystemListing
from database import Database
import tracemalloc
import argparse
import os.path
from system import System
from file_types import FileTypes
import time
import socket
import logging
from data import Data
from format import Format
from datetime import datetime
import json
from print import Print

class F:

    EXIT_OK: int = 0 #
    EXIT_ERROR: int = 1 #

    DEFAULT_DATABASE_FILENAME: str = 'database.sqlite'
    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf'

    SUBCMD_FILE_SEARCH: str = 'file_search'
    SUBCMD_REFRESH_VOLUMES: str = 'refresh_volumes'
    SUBCMD_ADD_VOLUME: str = 'add_volume'
    SUBCMD_IMPORT_VOLUME: str = 'import_volume'
    SUBCMD_CREATE_DATABASE: str = 'create_db'
    SUBCMD_SELECT_DATABASE: str = 'select_db'
    SUBCMD_UPGRADE_DATABASE: str = 'upgrade_db'
    SUBCMD_VACUUM_DATABASE: str = 'vacuum_db'
    SUBCMD_RESET_DATABASE: str = 'reset_db'

    VOL_ARG_DETAILS_CHOICES: str = 'choices'
    VOL_ARG_DETAILS_DEFAULT_CHOICE: str = 'default_choice'
    VOL_ARG_DETAILS_CREATED: str = 'created'
    VOL_ARG_DETAILS_VOLUMES: str = 'volumes'
    VOL_ARG_DETAILS_VOLUMES_VOLUME_DICT_IDX: int = 0
    VOL_ARG_DETAILS_VOLUMES_LOGICAL_DICT_IDX: int = 1
    VOL_ARG_DETAILS_VOLUMES_PHYSICAL_DICT_IDX: int = 2

    VOL_ARG_DETAILS_FILENAME: str = "volume_argument_details.json"

    PROGRESS_INSERT_FREQUENCY: int = 10000

    def __init__(self, parser):
        self.database = None
        self.memory_stats = False
        self.system = System()
        self.logical_disk_array = None
        self.physical_disk_array = None
        self.volumes_array = None
        self.parser = parser

        # Open the JSON file, or use an empty dictionary if it doesn't exist.
        try:
            with open(self.VOL_ARG_DETAILS_FILENAME) as read_file:
                self.volume_argument_details = json.load(read_file)
        except FileNotFoundError:
            self.volume_argument_details = {self.VOL_ARG_DETAILS_CHOICES: [], self.VOL_ARG_DETAILS_DEFAULT_CHOICE: None, self.VOL_ARG_DETAILS_VOLUMES: {}, self.VOL_ARG_DETAILS_CREATED: "" }

    def set_memory_stats(self, memory_stats):
        self.memory_stats = memory_stats

    @staticmethod
    def dumps(data):
        logging.debug(f"### dumps() ###")
        return json.dumps(data, indent=4, default=str)

    @staticmethod
    def start_logger(logging_level):
        logging.basicConfig(level=logging_level,
                            filename="app.log",
                            encoding="utf-8",
                            filemode="a",
                            format="{asctime} - {levelname} - {message}",
                            style="{",
                            datefmt="%Y-%m-%d %H:%M"
                            )
        logging.info("******************************************")
        logging.info(f"Application started: {os.path.basename(__file__)}")
        logging.info("******************************************")

    def get_message_based_on_parser(self, argumentparser_message, non_argumentparser_message):
        if type(self.parser) is argparse.ArgumentParser:
            return argumentparser_message
        else:
            return non_argumentparser_message

    def print_message_based_on_parser(self, argumentparser_message, non_argumentparser_message):
        message = self.get_message_based_on_parser(argumentparser_message, non_argumentparser_message)
        print(message)

    def clean_up(self):
        # Now that the subcommands have been run
        if self.memory_stats:
            # Stop tracing memory allocations
            tracemalloc.stop()

    def exit_cleanly(self, level, argumentparser_message: str = None, non_argumentparser_message: str = None):
        if non_argumentparser_message is None:
            non_argumentparser_message = argumentparser_message
        message = self.get_message_based_on_parser(argumentparser_message, non_argumentparser_message)
        if level == 0:
            logging.info("Application ended successfully")
            logging.info(message)
            print(message)
        else:
            logging.critical("Application ended with errors:")
            logging.critical(message)
            print(f"ERROR: {message}")
        self.clean_up()
        logging.info("******************************************")
        logging.info(f"Application ended: {os.path.basename(__file__)}")
        logging.info("******************************************")
        sys.exit(level)

    @staticmethod
    def does_database_directory_exist(database_filename):
        abspath_database_filename = os.path.abspath(database_filename)
        directory_name = os.path.dirname(abspath_database_filename)
        # Does the directory exist where we want to create the database?
        if not os.path.exists(directory_name):
            print(f"\"{directory_name}\" directory in your database filename path, does not exist!")
            print("The directory must exist before a new database can be created there.")
            exit(2)

    def create_database(self, database_filename, verbose: bool = False):
        logging.debug(f"### F.create_database() ###")
        self.database = Database(database_filename)
        self.database.set_verbose_mode(verbose)
        self.database.create_database_structure()

    def subcommand_file_search(self, args: []):
        logging.debug(f"### F.search() ###")
        self.print_message_based_on_parser(None, "Finding filenames:")
        self.print_message_based_on_parser(None, "")
        search = args.search # if "search" in args else None
        category = args.category if "category" in args else None
        label = args.label # if "label" in args else None
        if search is None and category is None and label is None:
            self.exit_cleanly(self.EXIT_ERROR, "No search terms provided")
        select_result = self.database.find_filenames_search(search, category, label)
        rows_found = 0
        for row in select_result:
            print(f"{row[1]}, {row[0]}")
            rows_found += 1
        # Print a blank row if we are in the GUI and rows were found
        if rows_found != 0:
            self.print_message_based_on_parser(None, "")
        # Print the number of row found in the GUI
        self.print_message_based_on_parser(None, f"{rows_found} results found")

    def subcommand_refresh_volumes(self, args: []):
        logging.debug("### F.refresh_volumes() ###")
        self.prepare_volume_details()
        #print(self.volume_argument_details )
        volume_default_choice = self.volume_argument_details[self.VOL_ARG_DETAILS_DEFAULT_CHOICE]
        volume_choices = self.volume_argument_details[self.VOL_ARG_DETAILS_CHOICES]
        print(f"")
        print(f"Volumes found:")
        for volume_choice in volume_choices:
            print(f"- {volume_choice}")
        print()
        print(f"Chosen Default Volume:")
        print(f"- {volume_default_choice}")

    @staticmethod
    def get_values_for_volume_array(result_array: []) -> {}:
        import_listing_values = {}
        result_array_length = len(result_array)
        # Get values from the volume dictionary
        volume_dictionary = result_array[F.VOL_ARG_DETAILS_VOLUMES_VOLUME_DICT_IDX]
        import_listing_values["drive_letter"] = volume_dictionary['DriveLetter']
        import_listing_values["label"] = volume_dictionary['FileSystemLabel']

        # Get values from the logical drive dictionary, but only if it exists
        if result_array_length > 1:
            logical_disk_dictionary = result_array[F.VOL_ARG_DETAILS_VOLUMES_LOGICAL_DICT_IDX]
            import_listing_values["make"] = logical_disk_dictionary['Manufacturer']
            import_listing_values["model"] = logical_disk_dictionary['Model']
            import_listing_values["serial_number"] = logical_disk_dictionary['SerialNumber']
        else:
            import_listing_values["make"] = ""
            import_listing_values["model"] = ""
            import_listing_values["serial_number"] = ""

        import_listing_values["hostname"] = socket.gethostname()
        return import_listing_values

    def subcommand_add_volumes(self, args: []):
        logging.debug("### F.subcommand_add_volumes() ###")
        print("Adding volume:")
        #if len(self.volume_argument_details) != 0:
        """
        print(f"self.volume_argument_details[\"{self.VOL_ARG_DETAILS_VOLUMES}\"]:")
        Print.print_dictionary(self.volume_argument_details[self.VOL_ARG_DETAILS_VOLUMES])
        print("")
        print(f"self.volume_argument_details[\"{self.VOL_ARG_DETAILS_CHOICES}\"]: {self.volume_argument_details[self.VOL_ARG_DETAILS_CHOICES]}")
        print("")
        print(f"self.volume_argument_details[\"{self.VOL_ARG_DETAILS_DEFAULT_CHOICE}\"]: {self.volume_argument_details[self.VOL_ARG_DETAILS_DEFAULT_CHOICE]}")
        print("")
        print(f"self.volume_argument_details[\"{self.VOL_ARG_DETAILS_CREATED}\"]: {self.volume_argument_details[self.VOL_ARG_DETAILS_CREATED]}")
        print(f"")
        """
        volume_choice = args.volume
        if volume_choice not in self.volume_argument_details[self.VOL_ARG_DETAILS_CHOICES]:
            message= f"Volume description \"{volume_choice}\" not found in the list of available volumes."
            self.exit_cleanly(self.EXIT_ERROR, message, message)
        else:
            """
            for volume_option, volume_dictionary in self.volume_argument_details[self.VOL_ARG_DETAILS_VOLUMES].items():
                print(f"{volume_option}: {volume_dictionary}")
                print(f"")
            """
            volume_array = self.volume_argument_details[self.VOL_ARG_DETAILS_VOLUMES][volume_choice]
            #print(f"Chosen volume_dictionary:")
            #Print.print_array_of_dictionaries(volume_array)
            print(f"")
            import_listing_values = self.get_values_for_volume_array(volume_array)
            #print(f"import_listing_values:")
            #Print.print_dictionary(import_listing_values)
            #print(f"")
            #print('Processing Volume:')
            label = import_listing_values["label"]
            if args.add_label is not None:
                label = args.add_label
            print(f'Drive: "{import_listing_values["drive_letter"]}:"')
            print(f'Label: "{label}"')
            print(f'Hostname: "{import_listing_values["hostname"]}"')
            print(f'Make: "{import_listing_values["make"]}"')
            print(f'Model: "{import_listing_values["model"]}"')
            print(f'Serial: "{import_listing_values["serial_number"]}"')

            print('')
            print('Generating the Volume Listing ...')
            output = self.system.create_path_listing(import_listing_values["drive_letter"] + ':\\',
                                                     self.DEFAULT_TEMP_LISTING_FILE)
            # print(f"create_path_listing output: {output}")
            print('Processing the Volume Listing ...')
            powershell_filesystem_listing = PowerShellFilesystemListing(self.database, label,
                                                                        self.DEFAULT_TEMP_LISTING_FILE)
            if args.verbose is not None:
                powershell_filesystem_listing.set_verbose(args.verbose)
            #if args.test is not None:
            #    powershell_filesystem_listing.set_test(args.test)

            powershell_filesystem_listing.set_make(import_listing_values["make"])
            powershell_filesystem_listing.set_model(import_listing_values["model"])
            powershell_filesystem_listing.set_serial_number(import_listing_values["serial_number"])
            # powershell_filesystem_listing.set_combined(args.combined)
            powershell_filesystem_listing.set_hostname(import_listing_values["hostname"])
            # powershell_filesystem_listing.set_prefix(args.prefix)
            powershell_filesystem_listing.set_memory_stats(self.memory_stats)
            powershell_filesystem_listing.save_to_database()
            import_listing_success = powershell_filesystem_listing.import_listing(self.PROGRESS_INSERT_FREQUENCY)
            if import_listing_success:
                print(f"Volume {import_listing_values["drive_letter"]}: Added Successfully...")

    def select_database(self, database_filename, verbose):
        F.does_database_directory_exist(database_filename)
        if not os.path.isfile(database_filename):
            print(f"Database file does not exists at location: \"{os.path.abspath(database_filename)}\"")
            print(f"Creating database file...")
            self.create_database(database_filename, verbose)
        else:
            self.database = Database(database_filename)

    def subcommand_select_database(self, args: []):
        logging.debug(f"### F.subcommand_select_database() ###")
        database_filename = args.db
        verbose = args.verbose if "verbose" in args else False
        self.select_database(database_filename, verbose)

    def subcommand_create_database(self, args: []):
        logging.debug(f"### F.subcommand_create_database() ###")
        database_filename = args.db
        F.does_database_directory_exist(database_filename)
        if os.path.isfile(database_filename):
            print(f"Database file already exists at location: \"{os.path.abspath(database_filename)}\"")
            print(f"To empty the database, use the \'{F.SUBCMD_RESET_DATABASE}\' subcommand.")
            exit(2)
        verbose = args.verbose if "verbose" in args else False
        self.create_database(database_filename, verbose)

    def subcommand_upgrade_database(self):
        logging.debug(f"### F.upgrade() ###")
        print(f"Upgrading database. This may take a while depending on the your database size.")
        self.database.upgrade_database()
        print(f"Upgrading finished.")

    def subcommand_vacuum_database(self):
        logging.debug(f"### F.vacuum() ###")
        print(f"Vacuuming database. This may take a while depending on the your database size.")
        self.database.vacuum()
        print(f"Vacuuming finished.")

    def subcommand_reset_database(self, args: []):
        logging.debug(f"### F.reset() ###")
        print(f"Not implemented yet")

    def subcommand_import_listing(self, args: []):
        logging.debug(f"### F.import_listing() ###")
        print(f"Import subcommand: Needs Further Testing !!!")
        powershell_filesystem_listing = PowerShellFilesystemListing(self.database, args.label, args.filename)

        if args.verbose is not None:
            powershell_filesystem_listing.set_verbose(args.verbose)
        #if args.test is not None:
        #    powershell_filesystem_listing.set_test(args.test)
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

    @staticmethod
    def add_argument(parser, *temp_args, **temp_kwargs): # : Optional[Union[Iterable, dict]]
        #logging.debug(f"### F.create_volume_options() ###")
        #parser.add_argument(temp_args, temp_kwargs)
        #logging.debug(f"type(parser): {type(parser)}")
        #logging.debug(f"BEFORE: temp_kwargs: {temp_kwargs}")
        if type(parser) is argparse.ArgumentParser or type(parser) is argparse._ArgumentGroup:
            # Remove GooeyParser parameters as they aren't compatible with the ArgumentParser
            #logging.debug(f"== argparse.ArgumentParser")
            temp_kwargs.pop("metavar", None)
            temp_kwargs.pop("widget", None)
            temp_kwargs.pop("gooey_options", None)
            temp_kwargs.pop("prog", None)
        #logging.debug(f"AFTER : temp_kwargs: {temp_kwargs}")
        parser.add_argument( *temp_args, **temp_kwargs )

    @staticmethod
    def add_db_argument_to_parser(parser, create: bool=False):
        #print(f"Parser type: {type(parser)}")
        """
        if type(parser) is argparse.ArgumentParser:
            F.add_argument(parser, "-d", "--db", dest='db', default=F.DEFAULT_DATABASE_FILENAME,
                            help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
        else:
        """
        if create:
            F.add_argument(parser, "--db", dest='db', default=F.DEFAULT_DATABASE_FILENAME,
                                widget = 'FileSaver',
                                metavar='Database Filename',
                                help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.", gooey_options = {'visible': False})
        else:
            F.add_argument(parser, "--db", dest='db', default=F.DEFAULT_DATABASE_FILENAME,
                                widget = 'FileChooser',
                                metavar='Database Filename',
                                help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.", gooey_options = {'visible': False})

    @staticmethod
    def add_verbose_argument_to_parser(parser, create: bool = False):
        F.add_argument(parser, "-v", "--verbose", dest='verbose', default=False,
                            action="store_true",
                            metavar='Verbose',
                            help="Verbose output")

    def load_volume_drive_details(self):
        logging.debug(f"### F.load_volume_drive_details() ###")
        logging.info("Finding Logical Drives ...")
        print(f"Finding Logical Drives ...")
        self.logical_disk_array = self.system.get_logical_drives_details()
        # display_array_of_dictionaries(self.logical_disk_array)
        # print(f"logical_disk_array: {self.logical_disk_array}")

        logging.info("Finding Physical Drives ...")
        print(f"Finding Physical Drives ...")
        self.physical_disk_array = self.system.get_physical_drives_details()
        # print(f"physical_disk_array: {self.physical_disk_array}")

        logging.info("Finding Volumes ...")
        print(f"Finding Volumes ...")
        self.volumes_array = self.system.get_volumes(True)
        # print(f"volumes: {self.volumes_array}")
        # display_array_of_dictionaries(self.volumes_array)
        # display_diff_dictionaries(volumes[0], volumes[1])

        # print("Finding Partitions ...")
        # self.partitions_array = self.system.get_partition_details()
        # print(f"physical_disk_array: {self.partitions_array}")

    def create_volume_options(self) -> []:
        logging.debug(f"### F.create_volume_options() ###")
        logging.info("Matching Volumes to Drives ...")
        print(f"Matching Volumes to Drives ...")
        option_number = 1
        options = []
        for volume_dictionary in self.volumes_array:
            # Initialise the volume_array_of_dicts with the volume_dictionary
            volume_array_of_dicts = [volume_dictionary]
            drive_letter = f'{volume_dictionary['DriveLetter']}:'
            disk_number = self.system.get_disk_number_for_drive_letter(drive_letter)
            # print(f"{drive_letter} is on drive {disk_number}")

            volume_info_line = f"{volume_dictionary['DriveLetter']}: \"{volume_dictionary['FileSystemLabel']}\" {Format.format_storage_size(int(volume_dictionary['Size']), True, 1)}, {volume_dictionary['FileSystemType']} ({volume_dictionary['HealthStatus']})"
            if len(disk_number.strip()) != 0:
                logical_disk_dictionary = Data.find_dictionary_in_array(self.logical_disk_array, "DiskNumber",
                                                                        disk_number)
                # Append to the volume_array_of_dicts the logical_disk_dictionary
                volume_array_of_dicts.append(logical_disk_dictionary)
                physical_disk_dictionary = Data.find_dictionary_in_array(self.physical_disk_array, "DeviceId",
                                                                         disk_number)
                # Append to the volume_array_of_dicts the physical_disk_dictionary
                volume_array_of_dicts.append(physical_disk_dictionary)
                if logical_disk_dictionary is not None:
                    volume_info_line += f" / {logical_disk_dictionary['BusType']} {physical_disk_dictionary['MediaType']}: {logical_disk_dictionary['Manufacturer']}, {logical_disk_dictionary['Model']}, SN: {logical_disk_dictionary['SerialNumber']} ({logical_disk_dictionary['HealthStatus']}))"
                else:
                    volume_info_line += ""
            option = [str(option_number), volume_info_line, volume_array_of_dicts]
            options.append(option)
            option_number += 1
        return options

    def prepare_volume_details(self) -> {}:
        logging.debug(f"### F.prepare_volume_details() ###")
        # Prepare the volume details to be populated into the GUI version of the program
        logging.info(f"prepare_volume_details()")
        # load the data required for the "add_volume" subcommand
        self.volume_argument_details.clear()

        # Load volume details
        self.load_volume_drive_details()
        # Create options for the command line version
        options = self.create_volume_options()
        # print(options)

        volumes = {}
        volume_choices = []
        volume_default_choice = None
        for option in options:
            volume_description = option[System.OPT_DESCRIPTION_IDX]
            # print(f"volume_description: {volume_description}")
            volume_result_array = option[System.OPT_RESULT_IDX]
            # print(f"volume_result: {volume_result_array}")

            # If the volume_result_array > 1 then as well as the Volume dictionary,
            # it must also contain the logical disk dictionary
            if len(volume_result_array) > 1:
                # Results contain Logical drive details
                logical_disk_dictionary = volume_result_array[F.VOL_ARG_DETAILS_VOLUMES_LOGICAL_DICT_IDX]
                bus_type = logical_disk_dictionary['BusType']
                if bus_type.lower() == 'usb':
                    volume_default_choice = volume_description

            volumes[volume_description] = volume_result_array
            volume_choices.append(volume_description)

        now = datetime.now()
        self.volume_argument_details[self.VOL_ARG_DETAILS_CREATED] = now.strftime('%Y-%m-%d %H:%M:%S')
        self.volume_argument_details[self.VOL_ARG_DETAILS_CHOICES] = volume_choices
        self.volume_argument_details[self.VOL_ARG_DETAILS_DEFAULT_CHOICE] = volume_default_choice
        self.volume_argument_details[self.VOL_ARG_DETAILS_VOLUMES] = volumes

        logging.info(f"self.volume_argument_details[\"created\"]: {self.volume_argument_details[self.VOL_ARG_DETAILS_CREATED]}")
        # Write data to a JSON file
        with open(self.VOL_ARG_DETAILS_FILENAME, 'w') as write_file:
            json.dump(self.volume_argument_details, write_file) # Warning seems to be a bug in PyCharm

    @staticmethod
    def add_subcommand_file_search_arguments_to_parser(subparsers):
        logging.debug(f"### F.add_subcommand_file_search_arguments_to_parser() ###")

        file_categories = FileTypes.get_file_categories()
        #print(f"file_categories: {file_categories}")

        subparser_search = subparsers.add_parser(F.SUBCMD_FILE_SEARCH,
                                            help=F.SUBCMD_FILE_SEARCH+' help', prog='File Search',
                                            description='Search for files based on search strings')
        subparser_search_group = subparser_search.add_argument_group(
            'Search for files',
            description='Search for files based on search strings'
        )
        help_text = '''Search string to be found within filenames
- if search doesn't include '%' or '_' characters, then it is a fast exact case-sensitive search
- if search includes '%' or '_' characters, then it is a slower pattern match case-insensitive search
- '%' wildcard matches any sequence of zero or more characters
- '_' wildcard matches exactly one character'''
        if type(subparsers) is argparse.ArgumentParser:
            help_text = help_text.replace(r"%", r"%%")
        F.add_argument(subparser_search_group, "-s", "--search", metavar='Search', default=None, help=help_text)
        # ADD BACK WHEN FUNCTIONALITY IMPLEMENTED
        #if type(subparsers) is not argparse.ArgumentParser:
        #    F.add_argument(subparser_search_group, "-c", "--category", dest='category', metavar='Category', choices=file_categories, nargs='?', help="Category of files to be considered")
        F.add_argument(subparser_search_group, "-l", "--label", dest='label', metavar='Label', default=None, help="Label of the drive listing")
        F.add_db_argument_to_parser(subparser_search_group)
        #F.add_verbose_argument_to_parser(subparser_search_group)

    def add_subcommand_add_volume_arguments_to_parser(self, subparsers):
        logging.debug(f"### F.add_subcommand_add_volume_arguments_to_parser() ###")
        # Only add the 'add' subcommand to the GUI
        if type(subparsers) is not argparse.ArgumentParser:
            # create the parser for the "add" subcommand
            subparser_add_volume = subparsers.add_parser(F.SUBCMD_ADD_VOLUME, help=F.SUBCMD_ADD_VOLUME+' help', prog='Add Volume Files', description='Add Files on a selected Volume to the Database')
            subparser_add_volume_group = subparser_add_volume.add_argument_group(
                'Add Volume Files to Database',
                description='Add Files on a selected Volume to the Database'
            )
            help_text = f'''Volume that you wish to add.
- If you don't see your volume, please use the {self.get_message_based_on_parser("'refresh_volumes' subcommand", "'Refresh Volumes List' action.")}
- Values last updated: {self.volume_argument_details[self.VOL_ARG_DETAILS_CREATED]}'''
            if type(subparsers) is argparse.ArgumentParser:
                help_text = help_text.replace(r"%", r"%%")
            F.add_argument(subparser_add_volume_group, "--volume", dest='volume', metavar='Volume', widget='Dropdown',
                                       nargs='?', default=None, help=help_text)
            #F.add_argument(subparser_add_volume_group, "-l", "--label", dest='label', metavar='Label', default=None, help="Label of the drive listing. If provided it will override the volume label.",
            F.add_argument(subparser_add_volume_group, "--add_label", dest='add_label', metavar='Label',
                                          default=None,
                                          help="Label of the drive listing. If provided it will override the volume label.",
                                          #gooey_options={ 'initial_value': "Hell" }
                           )
            hostname = socket.gethostname()
            F.add_argument(subparser_add_volume_group, "-n", "--hostname", dest='hostname', metavar='Hostname', default=hostname,
                                          help="Hostname of the machine containing the drive")
            F.add_db_argument_to_parser(subparser_add_volume_group)
            F.add_verbose_argument_to_parser(subparser_add_volume_group)

    @staticmethod
    def add_subcommand_refresh_volumes_arguments_to_parser(subparsers):
        logging.debug(f"### F.add_subcommand_refresh_volumes_arguments_to_parser() ###")
        # Only add the 'add' subcommand to the GUI
        if type(subparsers) is not argparse.ArgumentParser:
            # create the parser for the "add" subcommand
            subparser_refresh_volumes = subparsers.add_parser(F.SUBCMD_REFRESH_VOLUMES, help=F.SUBCMD_REFRESH_VOLUMES+' help', prog='Refresh Volumes List', description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.')
            subparser_refresh_volumes_group = subparser_refresh_volumes.add_argument_group(
                'Refresh Volumes List',
                description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.'
            )
            F.add_argument(subparser_refresh_volumes_group, "-i", "--invisible", dest='invisible', metavar='Invisible',
                           action='store_true', default=True,
                           help="Invisible checkbox", gooey_options = {'visible': False})

    @staticmethod
    def add_subcommand_create_database_arguments_to_parser(subparsers):
        logging.debug(f"### F.add_subcommand_create_database_arguments_to_parser() ###")
        subparser_create_database = subparsers.add_parser(F.SUBCMD_CREATE_DATABASE,
                                              help=F.SUBCMD_CREATE_DATABASE+' help', prog='Create Database',
                                              description='Create a new database')
        subparser_create_database_group = subparser_create_database.add_argument_group(
            'Create Database',
            description='Create a new database.'
        )
        F.add_db_argument_to_parser(subparser_create_database_group, True)
        #F.add_verbose_argument_to_parser(subparser_create_database_group)

    @staticmethod
    def add_subcommand_select_database_arguments_to_parser(subparsers):
        logging.debug(f"### F.add_subcommand_select_database_arguments_to_parser() ###")
        subparser_select_database = subparsers.add_parser(F.SUBCMD_SELECT_DATABASE,
                                              help=F.SUBCMD_SELECT_DATABASE+' help', prog='Select Database',
                                              description='Select the database you wish to use, including the path to the database file.')
        subparser_select_database_group = subparser_select_database.add_argument_group(
            'Select Database',
            description='Select the database you wish to use, including the path to the database file.'
        )
        F.add_argument(subparser_select_database_group, "db", default=F.DEFAULT_DATABASE_FILENAME,
                       widget='FileChooser',
                       metavar='Database Filename',
                       help="Database filename (including the path if not in the current directory). Default='database.sqlite' in the current directory.")
        #F.add_db_argument_to_parser(subparser_select_database_group, False)
        #F.add_verbose_argument_to_parser(subparser_create_database_group)

    def add_subcommands_to_parser(self, parser):
        logging.debug(f"### F.add_subcommands_to_parser() ###")

        subparsers = parser.add_subparsers(title='subcommands',
                                           description='valid subcommands',
                                           required=True,
                                           dest='subcommand',
                                           help='additional help')
        self.add_subcommand_file_search_arguments_to_parser(subparsers)
        self.add_subcommand_add_volume_arguments_to_parser(subparsers)
        self.add_subcommand_refresh_volumes_arguments_to_parser(subparsers)
        #self.add_subcommand_create_database_arguments_to_parser(subparsers)
        #self.add_subcommand_select_database_arguments_to_parser(subparsers)


        """
        # create the parser for the "import" subcommand
        parser_import = subparsers.add_parser(F.SUBCMD_IMPORT_VOLUME, help=F.SUBCMD_IMPORT_VOLUME+' help')
        F.add_db_argument_to_parser(parser_import)
        F.add_argument(parser_import, "-l", "--label", metavar='Label', help="Label of the drive listing")
        F.add_argument(parser_import, "-f", "--filename", metavar='Filename', widget='FileChooser',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example")
        #F.add_argument(parser_import, "-m", "--make", dest='make', metavar='Make', default=None, help="Make of the drive")
        F.add_argument(parser_import, "-m", "--make", dest='make', metavar='Make', help="Make of the drive")
        F.add_argument(parser_import, "-o", "--model", dest='model', metavar='Model', help="Model of the drive")
        F.add_argument(parser_import, "-s", "--serial", dest='serial', metavar='Serial Number', help="Serial number of the drive")
        F.add_argument(parser_import, "-c", "--combined", dest='combined', metavar='Combined',
                                   help="Combined drive information string, in format \"make,model,serial-number\"")
        F.add_argument(parser_import, "-n", "--hostname", dest='hostname', metavar='Hostname',
                                   help="Hostname of the machine containing the drive")
        F.add_argument(parser_import, "-p", "--prefix", dest='prefix', metavar='Prefix',
                                   help="Prefix to remove from the start of each file's path. e.g. \"C:\\Users\\username\"")
        F.add_argument(parser_import, "-t", "--test", dest='test', metavar='Test', action="store_true",
                                   help="Test input file without modifying the database")
        F.add_verbose_argument_to_parser(parser_import)



        # create the parser for the "vacuum" subcommand
        parser_upgrade = subparsers.add_parser(F.SUBCMD_UPGRADE_DATABASE,
                                              help=F.SUBCMD_UPGRADE_DATABASE+' help',
                                              description='The UPGRADE subcommand upgrades the database file to the latest structure needed for this program to work.')
        F.add_db_argument_to_parser(parser_upgrade)
        F.add_verbose_argument_to_parser(parser_upgrade)

        # create the parser for the "vacuum" subcommand
        parser_vacuum = subparsers.add_parser(F.SUBCMD_VACUUM_DATABASE,
                                              help=F.SUBCMD_VACUUM_DATABASE+' help',
                                              description='The VACUUM subcommand rebuilds the database file by reading the current file and writing the content into a new file. As a result it repacking it into a minimal amount of disk space and defragments it which ensures that each table and index is largely stored contiguously. Depending on the size of the database it can take some time to do perform.')
        F.add_db_argument_to_parser(parser_vacuum)
        F.add_verbose_argument_to_parser(parser_vacuum)

        parser_reset = subparsers.add_parser(F.SUBCMD_RESET_DATABASE,
                                             help=F.SUBCMD_RESET_DATABASE+' help',
                                             description='Warning: Using the "reset" subcommand will delete the specified database and replace it with an empty one.')
        F.add_db_argument_to_parser(parser_reset)
        F.add_verbose_argument_to_parser(parser_reset)
        """

    def connect_to_database(self, database_filename):
        if not os.path.isfile(database_filename):
            # Database file doesn't exist
            # Ask user if they want to create a new database file?
            print(f"Database file doesn't exist at location: \"{os.path.abspath(database_filename)}\"")
            self.print_message_based_on_parser("Please create the Database using the 'create' subcommand.",
                                               "Please create the Database using the 'Create Database' action.")
            exit(2)

        self.database = Database(database_filename)

    def process_args_and_call_subcommand(self, args):
        logging.debug(f"### F.process_args_and_call_subcommand() ###")
        # If 'create' and 'refresh_volumes' subcommands are specified, then we don't need to open the database
        if args.subcommand == F.SUBCMD_SELECT_DATABASE:
            self.subcommand_select_database(args)
        elif args.subcommand == F.SUBCMD_CREATE_DATABASE:
            self.subcommand_create_database(args)
        elif args.subcommand == F.SUBCMD_REFRESH_VOLUMES:
            self.subcommand_refresh_volumes(args)
        else:
            # These subcommands all need a working database connection
            # The following subcommands all require a database
            self.connect_to_database(args.db)

            if "verbose" in args:
                self.database.set_verbose_mode(args.verbose)
            start_time = time.time()

            if args.subcommand == F.SUBCMD_FILE_SEARCH:
                self.subcommand_file_search(args)
            elif args.subcommand == F.SUBCMD_ADD_VOLUME:
                self.subcommand_add_volumes(args)

            elif args.subcommand == F.SUBCMD_IMPORT_VOLUME:
                self.subcommand_import_listing(args)

            elif args.subcommand == F.SUBCMD_UPGRADE_DATABASE:
                self.subcommand_upgrade_database()

            elif args.subcommand == F.SUBCMD_VACUUM_DATABASE:
                self.subcommand_vacuum_database()

            elif args.subcommand == F.SUBCMD_RESET_DATABASE:
                self.subcommand_reset_database(args)

            end_time = time.time()

            #print(f"Time in seconds: {end_time - start_time}")

            # Close the database cleanly now that we have finished with it
            self.database.close_database()

        # Clean up and exit
        self.clean_up()

    def start(self):
        logging.debug(f"### F.start() ###")

        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

        f.add_subcommands_to_parser(self.parser)

        args=self.parser.parse_args()

        # Debug
        #print(f"args: '{args}'")
        #print(f"subcommand: '{args.subcommand}'")
        #quit()

        self.process_args_and_call_subcommand(args)
        # Command finished so program finished

if __name__ == "__main__":

    #my_logger = logging.getLogger(__name__)
    F.start_logger(logging.DEBUG)
    new_parser = argparse.ArgumentParser(
        description="Filer - File Cataloger"
    )
    f = F(new_parser)
    f.start()
