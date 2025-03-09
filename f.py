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
import time
import socket
import logging
from data import Data
from format import Format
from datetime import datetime
import json
#from print import Print
from add_args import AddArgs

class F:

    SHOW_SUBMITTED_ARGS: bool = False
    SHOW_DB_FILENAME_ARG_IN_GUI: bool = False
    SHOW_DB_SELECTION: bool = False
    PROGRESS_INSERT_FREQUENCY: int = 10000

    EXIT_OK: int = 0 #
    EXIT_ERROR: int = 1 #

    DEFAULT_DATABASE_FILENAME: str = 'database.sqlite'
    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf'

    VOL_ARG_DETAILS_CHOICES: str = 'choices'
    VOL_ARG_DETAILS_DEFAULT_CHOICE: str = 'default_choice'
    VOL_ARG_DETAILS_CREATED: str = 'created'
    VOL_ARG_DETAILS_VOLUMES: str = 'volumes'
    VOL_ARG_DETAILS_VOLUMES_VOLUME_DICT_IDX: int = 0
    VOL_ARG_DETAILS_VOLUMES_LOGICAL_DICT_IDX: int = 1
    VOL_ARG_DETAILS_VOLUMES_PHYSICAL_DICT_IDX: int = 2

    CONFIG_FILENAME: str = "filer.json"
    CONFIG_ARGS: str = "args"
    CONFIG_VOL_DETAILS: str = "volume_details"
    CONFIG_DATABASE_FILENAME: str = "database_filename"
    CONFIG_CHOSEN_LABEL: str = "chosen_label"

    FILE_SEARCH_RESULTS_LABEL = 0
    FILE_SEARCH_RESULTS_FILENAME = 1
    FILE_SEARCH_RESULTS_BYTE_SIZE = 2
    FILE_SEARCH_RESULTS_LAST_WRITE_TIME = 3
    FILE_SEARCH_RESULTS_IS_DIRECTORY = 4
    FILE_SEARCH_RESULTS_IS_ARCHIVE = 5
    FILE_SEARCH_RESULTS_IS_READONLY = 6
    FILE_SEARCH_RESULTS_IS_HIDDEN = 7
    FILE_SEARCH_RESULTS_IS_SYSTEM = 8
    FILE_SEARCH_RESULTS_IS_LINK = 9
    FILE_SEARCH_RESULTS_IS_FULL_PATH = 10

    def __init__(self, parser, database_filename_argument: str = None):
        self.database = self.logical_disk_array = self.physical_disk_array = self.volumes_array = None
        self.memory_stats = self.verbose = False
        self.parser = parser
        self.system = System()

        self.configuration = { self.CONFIG_ARGS: {} }
        self.load_configuration()
        # If the database parameter has been specified, then the user wishes has told use to create a database in a non default location
        if database_filename_argument is not None:
            self.set_configuration_value( self.CONFIG_DATABASE_FILENAME, database_filename_argument, self.DEFAULT_DATABASE_FILENAME )
        # Get the stored database filename. Note that if it isn't defined yet, it will be set to the default
        self.database_filename = self.get_configuration_value( self.CONFIG_DATABASE_FILENAME, self.DEFAULT_DATABASE_FILENAME )
        # The following subcommands all require a database
        self.select_database(self.database_filename, self.verbose)

    def load_configuration(self):
        # Read in the prior arguments as a dictionary
        if os.path.isfile( self.CONFIG_FILENAME ):
            with open( self.CONFIG_FILENAME ) as data_file:
                self.configuration = json.load(data_file)
        if self.CONFIG_ARGS not in self.configuration:
            self.configuration[self.CONFIG_ARGS] = {}
        if self.CONFIG_VOL_DETAILS not in self.configuration:
            self.configuration[self.CONFIG_VOL_DETAILS] = { self.VOL_ARG_DETAILS_CHOICES: [], self.VOL_ARG_DETAILS_DEFAULT_CHOICE: None,
                                        self.VOL_ARG_DETAILS_VOLUMES: {}, self.VOL_ARG_DETAILS_CREATED: ""}
    
    def get_configuration_value(self, key: str, default_value: str = None):
        if key not in self.configuration: self.set_configuration_value(key, default_value)
        return self.configuration[key]

    def set_configuration_value(self, key: str, value: str = None, default_value: str = None):
        self.configuration[key] = value if value is not None else default_value
        self.store_configuration()

    def store_configuration(self, args=None):
        logging.debug(f"### store_configuration() ###")
        logging.info(f"Storing configuration...")

        if args is not None:
            # A subcommand has been run so store its arguments
            subcommand = args.subcommand
            subcommand_args = vars(args).copy()
            # Remove the 'subcommand' key / value pair from the subcommand_args
            if "subcommand" in subcommand_args: del subcommand_args['subcommand']
            # Remove the old arguments last submitted for this subcommand
            if subcommand in self.configuration[self.CONFIG_ARGS]: del self.configuration[self.CONFIG_ARGS][subcommand]
            # Store the new arguments for this subcommand
            self.configuration[self.CONFIG_ARGS][subcommand] = subcommand_args

        # Store the values of the arguments so we have them next time we run
        with open(self.CONFIG_FILENAME, 'w') as data_file:
            json.dump(self.configuration, data_file) # Using vars(args) returns the data as a dictionary

    def set_memory_stats(self, memory_stats):
        self.memory_stats = memory_stats

    @staticmethod
    def dumps(data):
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

    def print_message_based_on_parser(self, argumentparser_message, non_argumentparser_message):
        message = AddArgs.get_message_based_on_parser(self.parser, argumentparser_message, non_argumentparser_message)
        print(message)

    def clean_up(self):
        # Now that the subcommands have been run
        if self.memory_stats:
            tracemalloc.stop() # Stop tracing memory allocations

    def exit_cleanly(self, level, argumentparser_message: str = None, non_argumentparser_message: str = None):
        if non_argumentparser_message is None:
            non_argumentparser_message = argumentparser_message

        message = AddArgs.get_message_based_on_parser(self.parser, argumentparser_message, non_argumentparser_message)
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

    def print_file_search_result(self, select_results, label, show_size, show_last_modified, show_attributes):

        if show_last_modified:
            Format.print_local_timezone_info()
            print("")

        if show_attributes:
            print("Info: " + AddArgs.SHOW_ATTRIBUTES_EXTRA_HELP)
            print("")

        # Calculate Max Widths
        field_widths = {'label': 0, 'size': 0, 'datetime': 19, 'attributes': 6}
        show_label = False
        if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS:
            show_label = True
        if show_label or show_size:
            for row in select_results:
                if show_label:
                    temp_field_string = "" if row[self.FILE_SEARCH_RESULTS_LABEL] is None else row[self.FILE_SEARCH_RESULTS_LABEL]
                    temp_field_width = len(temp_field_string)
                    if temp_field_width > field_widths['label']: field_widths['label'] = temp_field_width
                if show_size:
                    size_bytes = 0 if row[self.FILE_SEARCH_RESULTS_BYTE_SIZE] is None else row[self.FILE_SEARCH_RESULTS_BYTE_SIZE]
                    temp_field_string = Format.format_storage_size(size_bytes, False)
                    temp_field_width = len(temp_field_string)
                    if temp_field_width > field_widths['size']: field_widths['size'] = temp_field_width

        # Print Headers
        if show_label: print("Label".rjust(field_widths['label']), end=" ")
        if show_size: print("Size".rjust(field_widths['size']), end=" ")
        if show_last_modified: print("Last Modified".rjust(field_widths['datetime']), end=" ")
        if show_attributes: print("Info".rjust(field_widths['attributes']), end=" ")
        print("Full Path")
        if show_label: print("=" * field_widths['label'], end=" ")
        if show_size: print("=" * field_widths['size'], end=" ")
        if show_last_modified: print("=" * field_widths['datetime'], end=" ")
        if show_attributes: print("=" * field_widths['attributes'], end=" ")
        print("=" * len("Full Path"))

        # Print results
        rows_found = 0
        for row in select_results:
            attributes = ""
            for i in range(0, len(row)):
                # Justify and space pad the field based on the max field width
                temp_value = row[i]
                temp_string = str(temp_value)
                match i:
                    case self.FILE_SEARCH_RESULTS_LABEL:
                        if show_label:
                            # Label isn't specified so we need to show the label for each filesystem entity
                            print(temp_string.rjust(field_widths['label']), end=" ")
                    case self.FILE_SEARCH_RESULTS_BYTE_SIZE:
                        if show_size:
                            size_bytes = 0 if row[i] is None else row[i]
                            temp_string = Format.format_storage_size(size_bytes, False)
                            print(temp_string.rjust(field_widths['size']), end=" ")
                    case self.FILE_SEARCH_RESULTS_LAST_WRITE_TIME:
                        if show_last_modified:
                            temp_string = "" if row[i] is None else Format.datetime_to_string(time.gmtime(row[i]))
                            #print(temp_string.rjust(field_widths['datetime']), end=" ")
                            print(temp_string, end=" ")
                    case self.FILE_SEARCH_RESULTS_IS_DIRECTORY:
                        append_char = 'D' if temp_value == 1 else '-'
                        attributes += append_char
                    case self.FILE_SEARCH_RESULTS_IS_ARCHIVE:
                        append_char = 'A' if temp_value == 1 else '-'
                        attributes += append_char
                    case self.FILE_SEARCH_RESULTS_IS_READONLY:
                        append_char = 'R' if temp_value == 1 else '-'
                        attributes += append_char
                    case self.FILE_SEARCH_RESULTS_IS_HIDDEN:
                        append_char = 'H' if temp_value == 1 else '-'
                        attributes += append_char
                    case self.FILE_SEARCH_RESULTS_IS_SYSTEM:
                        append_char = 'S' if temp_value == 1 else '-'
                        attributes += append_char
                    case self.FILE_SEARCH_RESULTS_IS_LINK:
                        append_char = 'L' if temp_value == 1 else '-'
                        attributes += append_char
                        if show_attributes:
                            print(f"{attributes}", end=" ") # Not justifying or padding required as fixed width
                    case self.FILE_SEARCH_RESULTS_IS_FULL_PATH:
                        print(temp_string) # .ljust(field_widths[i]) - Not needed as last string and left justified anyway

            rows_found += 1
        # Print a blank row if we are in the GUI and rows were found
        if rows_found != 0:
            self.print_message_based_on_parser(None, "")
        # Print the number of row found in the GUI
        self.print_message_based_on_parser(None, f"{rows_found} results found")


    def subcommand_filesystem_search(self, args: []):
        logging.debug(f"### F.search() ###")
        entry_search = args.search if "search" in args else AddArgs.SUBCMD_FILE_SEARCH_DEFAULT
        label = args.label if "label" in args else AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS
        entry_type = args.type if "type" in args else AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICE
        entry_category = args.category if "category" in args else None
        entry_size_limit = args.size_limit if "size_limit" in args else AddArgs.SUBCMD_FILE_SEARCH_SIZE_LIMIT_ALL_FILES
        order_by = args.order_by if "order_by" in args else AddArgs.SUBCMD_FILE_SEARCH_ORDER_DEFAULT_CHOICE
        max_results = args.max_results if "max_results" in args else AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE
        show_size = args.show_size if "show_size" in args else False
        show_last_modified = args.show_last_modified if "show_last_modified" in args else False
        show_attributes = args.show_attributes if "show_attributes" in args else False

        volume_label = None if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS else label
        entry_type_int = None
        if entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING:
            entry_type_int = None
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_DIRECTORIES:
            entry_type_int = 1 # Directories
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES:
            entry_type_int = 0 # Files
        else:
            self.exit_cleanly(self.EXIT_ERROR, f'Entry Type "{entry_type}" is not one of the choices!')

        max_results_int = 0
        try:
            # Convert strings to int
            max_results_int = int(max_results)
        except ValueError:
            # Handle the exception
            self.exit_cleanly(self.EXIT_ERROR, f'Results value "{args.max_results}" is not an integer!')

        if entry_search is None and entry_category is None and volume_label is None:
            self.exit_cleanly(self.EXIT_ERROR, "No search terms provided")

        self.print_message_based_on_parser(None, f"Finding files & dirs matching:")
        if entry_search is not None and entry_search != "": self.print_message_based_on_parser(None, f" - search: '{entry_search}'")
        #if label is not None and label != "":
        self.print_message_based_on_parser(None, f" - volume label: '{label}'")
        if entry_type is not None and entry_type != "": self.print_message_based_on_parser(None, f" - type: '{entry_type}'")
        if entry_category is not None and entry_category != "": self.print_message_based_on_parser(None, f" - category: '{entry_category}'")
        if entry_size_limit is not None and entry_size_limit != "": self.print_message_based_on_parser(None, f" - size limit: '{entry_size_limit}'")
        self.print_message_based_on_parser(None, f" - order by: '{order_by}'")
        self.print_message_based_on_parser(None, f" - max results: '{max_results_int}'")
        self.print_message_based_on_parser(None, "")

        select_results = self.database.filesystem_search(entry_search, volume_label, entry_type_int, entry_category, entry_size_limit, order_by, max_results_int)

        self.print_file_search_result(select_results, label, show_size, show_last_modified, show_attributes)

    def subcommand_refresh_volumes(self, args: []):
        logging.debug("### F.refresh_volumes() ###")
        self.prepare_volume_details()
        #print(self.volume_argument_details )
        volume_default_choice = self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_DEFAULT_CHOICE]
        volume_choices = self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CHOICES]
        print(f"")
        print(f"Volumes found:")
        for volume_choice in volume_choices:
            print(f"- {volume_choice}")
        print()
        print(f"Chosen Default Volume:")
        print(f"- {volume_default_choice}")

    @staticmethod
    def get_values_from_volume_array(volume_array: []) -> {}:
        volume_summary_array = {}
        result_array_length = len(volume_array)
        # Get values from the volume dictionary
        volume_dictionary = volume_array[F.VOL_ARG_DETAILS_VOLUMES_VOLUME_DICT_IDX]
        volume_summary_array["drive_letter"] = volume_dictionary['DriveLetter']
        volume_summary_array["label"] = volume_dictionary['FileSystemLabel']

        # Get values from the logical drive dictionary, but only if it exists
        if result_array_length > 1:
            logical_disk_dictionary = volume_array[F.VOL_ARG_DETAILS_VOLUMES_LOGICAL_DICT_IDX]
            volume_summary_array["make"] = logical_disk_dictionary['Manufacturer']
            volume_summary_array["model"] = logical_disk_dictionary['Model']
            volume_summary_array["serial_number"] = logical_disk_dictionary['SerialNumber']
        else:
            volume_summary_array["make"] = ""
            volume_summary_array["model"] = ""
            volume_summary_array["serial_number"] = ""

        volume_summary_array["hostname"] = socket.gethostname()
        return volume_summary_array

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
        if volume_choice not in self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CHOICES]:
            message= f"Volume description \"{volume_choice}\" not found in the list of available volumes."
            self.exit_cleanly(self.EXIT_ERROR, message, message)
        else:
            """
            for volume_option, volume_dictionary in self.volume_argument_details[self.VOL_ARG_DETAILS_VOLUMES].items():
                print(f"{volume_option}: {volume_dictionary}")
                print(f"")
            """
            volume_array = self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_VOLUMES][volume_choice]
            #print(f"Chosen volume_dictionary:")
            #Print.print_array_of_dictionaries(volume_array)
            print(f"")
            volume_summary_array = self.get_values_from_volume_array(volume_array)
            #print(f"import_listing_values:")
            #Print.print_dictionary(import_listing_values)
            #print(f"")
            #print('Processing Volume:')
            label = volume_summary_array["label"]
            if args.vol_label is not None and args.vol_label != AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT:
                label = args.vol_label
            print(f'Drive: "{volume_summary_array["drive_letter"]}:"')
            print(f'Label: "{label}"')
            print(f'Hostname: "{volume_summary_array["hostname"]}"')
            print(f'Make: "{volume_summary_array["make"]}"')
            print(f'Model: "{volume_summary_array["model"]}"')
            print(f'Serial: "{volume_summary_array["serial_number"]}"')
            print('')

            # Check if Label exists in the Database
            if self.database.does_label_exists(label):
                self.exit_cleanly(self.EXIT_ERROR, f'Label "{label}" already exists in the Database!')

            print('Generating the Volume Listing ...')
            output = self.system.create_path_listing(volume_summary_array["drive_letter"] + ':\\',
                                                     self.DEFAULT_TEMP_LISTING_FILE)
            # print(f"create_path_listing output: {output}")
            print('Processing the Volume Listing ...')
            powershell_filesystem_listing = PowerShellFilesystemListing(self.database, label,
                                                                        self.DEFAULT_TEMP_LISTING_FILE)
            if args.verbose is not None:
                powershell_filesystem_listing.set_verbose(args.verbose)
            #if args.test is not None:
            #    powershell_filesystem_listing.set_test(args.test)

            powershell_filesystem_listing.set_make(volume_summary_array["make"])
            powershell_filesystem_listing.set_model(volume_summary_array["model"])
            powershell_filesystem_listing.set_serial_number(volume_summary_array["serial_number"])
            # powershell_filesystem_listing.set_combined(args.combined)
            powershell_filesystem_listing.set_hostname(volume_summary_array["hostname"])
            # powershell_filesystem_listing.set_prefix(args.prefix)
            powershell_filesystem_listing.set_memory_stats(self.memory_stats)
            powershell_filesystem_listing.save_to_database()
            import_listing_success = powershell_filesystem_listing.import_listing(self.PROGRESS_INSERT_FREQUENCY)
            if import_listing_success:
                print(f"Volume {volume_summary_array["drive_letter"]}: Added Successfully...")

    def subcommand_select_database(self, args: []):
        logging.debug(f"### F.subcommand_select_database() ###")
        database_filename = args.db
        verbose = args.verbose if "verbose" in args else False
        self.select_database(database_filename, verbose)

    def select_database(self, database_filename, verbose):
        if self.database is not None:
            # Close the current database connection if it is not None
            self.database.close_database()
        # Does database Directory exist? Exits automatically if it doesn't
        F.does_database_directory_exist(database_filename)
        if not os.path.isfile(database_filename):
            print(f"Database file does not exists at location: \"{os.path.abspath(database_filename)}\"")
            self.create_database(database_filename, verbose)
        else:
            #print(f"Selecting database: \"{database_filename}\"")
            self.database = Database(database_filename)
            self.database.set_verbose_mode(verbose)
            # Apply any database upgrades
            self.database.upgrade_database()

    def subcommand_create_database(self, args: []):
        logging.debug(f"### F.subcommand_create_database() ###")
        database_filename = args.db
        verbose = args.verbose if "verbose" in args else False
        self.create_database(database_filename, verbose)

    def create_database(self, database_filename, verbose: bool = False):
        if self.database is not None:
            # Close the current database connection if it is not None
            self.database.close_database()
        # Does database Directory exist? Exits automatically if it doesn't
        F.does_database_directory_exist(database_filename)
        if os.path.isfile(database_filename):
            print(f"Database file already exists at location: \"{os.path.abspath(database_filename)}\"")
            print(f"To empty the database, use the \'{AddArgs.SUBCMD_RESET_DATABASE}\' subcommand.")
            exit(2)
        print(f"Creating database file...")
        self.database = Database(database_filename)
        self.database.set_verbose_mode(verbose)
        # Create initial database structure
        self.database.create_database_structure()
        # Apply any database upgrades
        self.database.upgrade_database()

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
        self.configuration[self.CONFIG_VOL_DETAILS].clear()

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
        self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CREATED] = now.strftime('%Y-%m-%d %H:%M:%S')
        self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CHOICES] = volume_choices
        self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_DEFAULT_CHOICE] = volume_default_choice
        self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_VOLUMES] = volumes

        logging.info(f"self.volume_argument_details[\"created\"]: {self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CREATED]}")
        # Store Volume details
        self.store_configuration()

    def process_args_and_call_subcommand(self, args):
        logging.debug(f"### F.process_args_and_call_subcommand() ###")

        database_changed = False
        if 'db' in args:
            self.set_configuration_value(self.CONFIG_DATABASE_FILENAME, args.db, self.DEFAULT_DATABASE_FILENAME)
            database_changed = True
            logging.debug(f"database_filename: {args.db}'")

        if 'label' in args:
            self.set_configuration_value(self.CONFIG_CHOSEN_LABEL, args.label, AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS)
            logging.debug(f"label: {args.label}'")

        # Save the configuration first, as selecting the database or processing the arguments may result in an error
        self.store_configuration(args)

        if database_changed:
            # Open a connection to the selected database filename
            self.select_database(args.db, self.verbose)

        # If 'create' and 'refresh_volumes' subcommands are specified, then we don't need to open the database
        if args.subcommand == AddArgs.SUBCMD_SELECT_DATABASE:
            self.subcommand_select_database(args)
        elif args.subcommand == AddArgs.SUBCMD_CREATE_DATABASE:
            self.subcommand_create_database(args)
        elif args.subcommand == AddArgs.SUBCMD_REFRESH_VOLUMES:
            self.subcommand_refresh_volumes(args)
        else:
            # These subcommands all need a working database connection

            if "verbose" in args:
                self.database.set_verbose_mode(args.verbose)
            start_time = time.time()

            if args.subcommand == AddArgs.SUBCMD_FILE_SEARCH:
                self.subcommand_filesystem_search(args)
            elif args.subcommand == AddArgs.SUBCMD_ADD_VOLUME:
                self.subcommand_add_volumes(args)

            elif args.subcommand == AddArgs.SUBCMD_IMPORT_VOLUME:
                self.subcommand_import_listing(args)

            elif args.subcommand == AddArgs.SUBCMD_UPGRADE_DATABASE:
                self.subcommand_upgrade_database()

            elif args.subcommand == AddArgs.SUBCMD_VACUUM_DATABASE:
                self.subcommand_vacuum_database()

            elif args.subcommand == AddArgs.SUBCMD_RESET_DATABASE:
                self.subcommand_reset_database(args)

            end_time = time.time()

            #print(f"Time in seconds: {end_time - start_time}")

        # Close the database cleanly now that we have finished with it (even if it wasn't used)
        self.database.close_database()

        # Clean up and exit
        self.clean_up()

    def init(self):
        logging.debug(f"### init() ###")

        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

        logging.info(f"Initialising Argument Parser Arguments...")
        AddArgs.add_subcommands_to_parser(self.parser)

        # self.parser.set_defaults(**self.stored_args)

    def main(self):
        logging.info(f"### main() ###")
        args = self.parser.parse_args()
        self.process_args_and_call_subcommand(args)

    def start(self):
        logging.debug(f"### F.start() ###")
        self.init()
        self.main()

if __name__ == "__main__":

    #my_logger = logging.getLogger(__name__)
    F.start_logger(logging.DEBUG)
    new_parser = argparse.ArgumentParser(
        description="Filer - File Cataloger"
    )
    f = F(new_parser)
    f.start()
