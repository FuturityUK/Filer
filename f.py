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

import tracemalloc
import os.path
import time
import socket
import logging
import json
import sqlite3
from file_system_processors import PowerShellFilesystemListing
from database import Database
from data import Data
from system import System
from format import Format
from convert import Convert
from datetime import datetime
#from print import Print
from add_args import AddArgs
#from program import Program

class F:

    SHOW_SUBMITTED_ARGS: bool = False
    SHOW_DB_FILENAME_ARG_IN_GUI: bool = False
    SHOW_DB_SELECTION: bool = False
    PROGRESS_INSERT_FREQUENCY: int = 10000
    REUSE_TEMP_LISTING_FILE: bool = False

    EXIT_OK: int = 0 #
    EXIT_ERROR: int = 1 #

    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf.test'

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

    FILE_SEARCH_RESULTS_LABEL: int = 0
    FILE_SEARCH_RESULTS_FILENAME: int = 1
    FILE_SEARCH_RESULTS_BYTE_SIZE: int = 2
    FILE_SEARCH_RESULTS_LAST_WRITE_TIME: int = 3
    FILE_SEARCH_RESULTS_IS_DIRECTORY: int = 4
    FILE_SEARCH_RESULTS_IS_ARCHIVE: int = 5
    FILE_SEARCH_RESULTS_IS_READONLY: int = 6
    FILE_SEARCH_RESULTS_IS_HIDDEN: int = 7
    FILE_SEARCH_RESULTS_IS_SYSTEM: int = 8
    FILE_SEARCH_RESULTS_IS_LINK: int = 9
    FILE_SEARCH_RESULTS_IS_FULL_PATH: int = 10

    DUPLICATES_SEARCH_RESULTS_DUPLICATES: int = 0
    DUPLICATES_SEARCH_RESULTS_IS_DIRECTORY: int = 1
    DUPLICATES_SEARCH_RESULTS_BYTE_SIZE: int = 2
    DUPLICATES_SEARCH_RESULTS_ENTRY_NAME: int = 3

    def __init__(self, program, parser, memory_stats: bool, database_filename_argument: str = None):
        self.__program = program
        self.parser = parser
        self.database = self.logical_disk_array = self.physical_disk_array = self.volumes_array = None
        self.memory_stats = memory_stats
        self.verbose = False
        self.system = System()

        self.configuration = { self.CONFIG_ARGS: {} }
        self.load_configuration()
        # If the database parameter has been specified, then the user wishes has told use to create a database in a non default location
        if database_filename_argument is not None:
            self.set_configuration_value( self.CONFIG_DATABASE_FILENAME, database_filename_argument, AddArgs.DEFAULT_DATABASE_FILENAME )
        # Get the stored database filename. Note that if it isn't defined yet, it will be set to the default
        self.database_filename = self.get_configuration_value( self.CONFIG_DATABASE_FILENAME, AddArgs.DEFAULT_DATABASE_FILENAME )
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
            subcommand = args.subcommand if "subcommand" in args else None
            # Create an array of all the arguments
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
        if message is not None:
            print(message)

    def display_progress_percentage(self, progress_percentage: int):
        self.__program.display_progress_percentage(progress_percentage)

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

    def print_duplicates_search_result(self, select_results):
        # Calculate Max Widths
        field_widths = {'duplicates': 10, 'type': 4, 'size': 4, 'entry_name': 10} # Start with Label widths: 'label': 5, 'size': 4, Fixed width columns: 'datetime': 19, 'attributes': 6
        if select_results is not None:
            for row in select_results:
                size_bytes = 0 if row[self.DUPLICATES_SEARCH_RESULTS_BYTE_SIZE] is None else row[self.DUPLICATES_SEARCH_RESULTS_BYTE_SIZE]
                temp_field_string = Convert.bytesize2string(size_bytes, False)
                temp_field_width = len(temp_field_string)
                if temp_field_width > field_widths['size']: field_widths['size'] = temp_field_width

        # Print Headers
        print("Duplicates".rjust(field_widths['duplicates']), end=" ")
        print("Type".rjust(field_widths['type']), end=" ")
        print("Size".rjust(field_widths['size']), end=" ")
        print("Entry Name")
        print("=" * field_widths['duplicates'], end=" ")
        print("=" * field_widths['type'], end=" ")
        print("=" * field_widths['size'], end=" ")
        print("=" * len("Entry Name"))

        # Print results
        rows_found = 0
        if select_results is not None:
            for row in select_results:
                for i in range(0, len(row)):
                    # Justify and space pad the field based on the max field width
                    temp_value = row[i]
                    temp_string = str(temp_value)
                    match i:
                        case self.DUPLICATES_SEARCH_RESULTS_DUPLICATES:
                            duplicates = 0 if row[i] is None else row[i]
                            print(temp_string.rjust(field_widths['duplicates']), end=" ")
                        case self.DUPLICATES_SEARCH_RESULTS_IS_DIRECTORY:
                            type_char = 'D' if temp_value == 1 else 'F'
                            print(type_char.rjust(field_widths['type']), end=" ")
                        case self.DUPLICATES_SEARCH_RESULTS_BYTE_SIZE:
                            size_bytes = 0 if row[i] is None else row[i]
                            temp_string = Convert.bytesize2string(size_bytes, False)
                            print(temp_string.rjust(field_widths['size']), end=" ")
                        case self.DUPLICATES_SEARCH_RESULTS_ENTRY_NAME:
                            print(temp_string) # .ljust(field_widths[i]) - Not needed as last string and left justified anyway
                rows_found += 1
        # Print a blank row if we are in the GUI and rows were found
        if rows_found != 0:
            self.print_message_based_on_parser(None, "")
        # Print the number of row found in the GUI
        self.print_message_based_on_parser(None, f"{rows_found} results found")

    def print_file_search_result(self, select_results, label, show_size, show_last_modified, show_attributes):

        if show_last_modified:
            Format.print_local_timezone_info()
            print("")

        if show_attributes:
            print("Info: " + AddArgs.SHOW_ATTRIBUTES_EXTRA_HELP)
            print("")

        # Calculate Max Widths
        field_widths = {'label': 5, 'size': 4, 'datetime': 19, 'attributes': 6} # Start with Label widths: 'label': 5, 'size': 4, Fixed width columns: 'datetime': 19, 'attributes': 6
        show_label = False
        if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS:
            show_label = True
        if show_label or show_size:
            if select_results is not None:
                for row in select_results:
                    if show_label:
                        temp_field_string = "" if row[self.FILE_SEARCH_RESULTS_LABEL] is None else row[self.FILE_SEARCH_RESULTS_LABEL]
                        temp_field_width = len(temp_field_string)
                        if temp_field_width > field_widths['label']: field_widths['label'] = temp_field_width
                    if show_size:
                        size_bytes = 0 if row[self.FILE_SEARCH_RESULTS_BYTE_SIZE] is None else row[self.FILE_SEARCH_RESULTS_BYTE_SIZE]
                        temp_field_string = Convert.bytesize2string(size_bytes, False)
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
        if select_results is not None:
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
                                temp_string = Convert.bytesize2string(size_bytes, False)
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
        logging.debug(f"### F.subcommand_filesystem_search() ###")
        # Gather argument values or their defaults
        entry_search = args.search if "search" in args else AddArgs.SUBCMD_FILE_SEARCH_DEFAULT
        label = args.label if "label" in args else AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS
        entry_type = args.type if "type" in args else AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICE
        entry_category = args.category if "category" in args else None
        entry_size_gt = args.size_gt if "size_gt" in args else AddArgs.SUBCMD_FILE_SEARCH_SIZE_ALL_FILES
        entry_size_lt = args.size_lt if "size_lt" in args else AddArgs.SUBCMD_FILE_SEARCH_SIZE_ALL_FILES
        order_by = args.order_by if "order_by" in args else AddArgs.SUBCMD_FILE_SEARCH_ORDER_DEFAULT_CHOICE
        max_results = args.max_results if "max_results" in args else AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE
        show_size = args.show_size if "show_size" in args else False
        show_last_modified = args.show_last_modified if "show_last_modified" in args else False
        show_attributes = args.show_attributes if "show_attributes" in args else False
        # volume_label = None if the default value has been selected
        volume_label = None if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS else label
        # Convert entry_type string into the entry_type_int number
        entry_type_int = None
        if entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING:
            entry_type_int = None
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_DIRECTORIES:
            entry_type_int = Database.ENTRY_TYPE_DIRECTORIES
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES:
            entry_type_int = Database.ENTRY_TYPE_FILES
        else:
            self.exit_cleanly(self.EXIT_ERROR, f'Entry Type "{entry_type}" is not one of the choices!')
        # Convert max_results into an integer
        max_results_int = 0
        try:
            max_results_int = int(max_results)
        except ValueError:
            self.exit_cleanly(self.EXIT_ERROR, f'Results value "{max_results}" is not an integer!') # Handle the exception
        # Convert entry_size_gt into an integer
        if entry_size_gt is not None and entry_size_gt != "":
            entry_size_gt_int = Convert.string2bytesize(entry_size_gt)
            if entry_size_gt is not None and entry_size_gt_int is None:
                self.exit_cleanly(self.EXIT_ERROR, f'Entry Size >= value "{entry_size_gt}" is not in a valid file size format!') # Handle the exception
        else:
            entry_size_gt_int = None
        # Convert entry_size_lt into an integer
        if entry_size_lt is not None and entry_size_lt != "":
            entry_size_lt_int = Convert.string2bytesize(entry_size_lt)
            if entry_size_lt is not None and entry_size_lt_int is None:
                self.exit_cleanly(self.EXIT_ERROR, f'Entry Size <= value "{entry_size_lt}" is not in a valid file size format!') # Handle the exception
        else:
            entry_size_lt_int = None

        # It doesn't matter if the none of these are filled in.
        # if (entry_search is None or entry_search == "") and entry_category is None and volume_label is None:
        #     self.exit_cleanly(self.EXIT_ERROR, "No search terms provided")

        self.print_message_based_on_parser(None, f"Finding files & dirs matching:")
        if entry_search is not None and entry_search != "": self.print_message_based_on_parser(None, f" - search: '{entry_search}'")
        #if label is not None and label != "":
        self.print_message_based_on_parser(None, f" - volume label: '{label}'")
        if entry_type is not None and entry_type != "": self.print_message_based_on_parser(None, f" - entry type: '{entry_type}'")
        if entry_category is not None and entry_category != "": self.print_message_based_on_parser(None, f" - category: '{entry_category}'")
        if entry_size_gt_int is not None and entry_size_gt_int != "": self.print_message_based_on_parser(None, f" - size limit >= : '{entry_size_gt}'")
        if entry_size_lt_int is not None and entry_size_lt_int != "": self.print_message_based_on_parser(None, f" - size limit <= : '{entry_size_lt}'")
        self.print_message_based_on_parser(None, f" - order by: '{order_by}'")
        self.print_message_based_on_parser(None, f" - max results: '{max_results_int}'")
        self.print_message_based_on_parser(None, "")

        select_results = self.database.filesystem_search(entry_search, volume_label, entry_type_int, entry_category, entry_size_gt_int, entry_size_lt_int, order_by, max_results_int)

        self.print_file_search_result(select_results, label, show_size, show_last_modified, show_attributes)

    def subcommand_filesystem_duplicates_search(self, args: []):
        logging.debug(f"### F.subcommand_filesystem_duplicates_search() ###")
        # Gather argument values or their defaults
        entry_search = args.search if "search" in args else AddArgs.SUBCMD_FILE_SEARCH_DEFAULT
        label = args.label if "label" in args else AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS
        entry_type = args.type if "type" in args else AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICE
        entry_category = args.category if "category" in args else None
        entry_size_gt = args.size_gt if "size_gt" in args else AddArgs.SUBCMD_FILE_SEARCH_SIZE_ALL_FILES
        entry_size_lt = args.size_lt if "size_lt" in args else AddArgs.SUBCMD_FILE_SEARCH_SIZE_ALL_FILES
        order_by = args.order_by if "order_by" in args else AddArgs.SUBCMD_FILE_SEARCH_ORDER_DEFAULT_CHOICE
        max_results = args.max_results if "max_results" in args else AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE
        show_size = args.show_size if "show_size" in args else False
        show_last_modified = args.show_last_modified if "show_last_modified" in args else False
        show_attributes = args.show_attributes if "show_attributes" in args else False
        # volume_label = None if the default value has been selected
        volume_label = None if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS else label
        # Convert entry_type string into the entry_type_int number
        entry_type_int = None
        if entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING:
            entry_type_int = None
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_DIRECTORIES:
            entry_type_int = Database.ENTRY_TYPE_DIRECTORIES
        elif entry_type == AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES:
            entry_type_int = Database.ENTRY_TYPE_FILES
        else:
            self.exit_cleanly(self.EXIT_ERROR, f'Entry Type "{entry_type}" is not one of the choices!')
        # Convert max_results into an integer
        max_results_int = 0
        try:
            max_results_int = int(max_results)
        except ValueError:
            self.exit_cleanly(self.EXIT_ERROR, f'Results value "{max_results}" is not an integer!') # Handle the exception
        # Convert entry_size_gt into an integer
        if entry_size_gt is not None and entry_size_gt != "":
            entry_size_gt_int = Convert.string2bytesize(entry_size_gt)
            if entry_size_gt is not None and entry_size_gt_int is None:
                self.exit_cleanly(self.EXIT_ERROR, f'Entry Size >= value "{entry_size_gt}" is not in a valid file size format!') # Handle the exception
        else:
            entry_size_gt_int = None
        # Convert entry_size_lt into an integer
        if entry_size_lt is not None and entry_size_lt != "":
            entry_size_lt_int = Convert.string2bytesize(entry_size_lt)
            if entry_size_lt is not None and entry_size_lt_int is None:
                self.exit_cleanly(self.EXIT_ERROR, f'Entry Size <= value "{entry_size_lt}" is not in a valid file size format!') # Handle the exception
        else:
            entry_size_lt_int = None

        # It doesn't matter if the none of these are filled in.
        # if (entry_search is None or entry_search == "") and entry_category is None and volume_label is None:
        #     self.exit_cleanly(self.EXIT_ERROR, "No search terms provided")

        self.print_message_based_on_parser(None, f"Finding duplicate files & dirs matching:")
        if entry_search is not None and entry_search != "": self.print_message_based_on_parser(None, f" - search: '{entry_search}'")
        #if label is not None and label != "":
        self.print_message_based_on_parser(None, f" - volume label: '{label}'")
        if entry_type is not None and entry_type != "": self.print_message_based_on_parser(None, f" - entry type: '{entry_type}'")
        if entry_category is not None and entry_category != "": self.print_message_based_on_parser(None, f" - category: '{entry_category}'")
        if entry_size_gt_int is not None and entry_size_gt_int != "": self.print_message_based_on_parser(None, f" - size limit >= : '{entry_size_gt}'")
        if entry_size_lt_int is not None and entry_size_lt_int != "": self.print_message_based_on_parser(None, f" - size limit <= : '{entry_size_lt}'")
        self.print_message_based_on_parser(None, f" - order by: '{order_by}'")
        self.print_message_based_on_parser(None, f" - max results: '{max_results_int}'")
        self.print_message_based_on_parser(None, "")

        select_results = self.database.filesystem_duplicates_search(entry_search, volume_label, entry_type_int, entry_category, entry_size_gt_int, entry_size_lt_int, order_by, max_results_int)

        self.print_duplicates_search_result(select_results)

    def subcommand_calculate_directory_sizes(self, args: []):
        logging.debug(f"### F.subcommand_calculate_directory_sizes() ###")
        label = args.label if "label" in args else AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS
        volume_label = None if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS else label

        results = None
        if label == AddArgs.SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS:
            results = self.database.find_filesystem_labels()
            if results is not None:
                for temp_volume_label in results:
                    print(f"Volume label: {temp_volume_label}")
                    self.calculate_volume_directory_sizes(temp_volume_label)
        else:
            self.calculate_volume_directory_sizes(volume_label)

    def calculate_volume_directory_sizes(self, volume_label: str):
        # Find FilesystemID
        results = self.database.find_filesystem_id(volume_label)
        if results is not None:
            results_len = len(results)
            if results_len == 0:
                self.print_message_based_on_parser(None,f"Error - No FilesystemID found for volume label: '{volume_label}'")
            elif results_len != 1:
                self.print_message_based_on_parser(None,f"Error - Found multi FilesystemIDs for volume label: '{volume_label}'")
                self.print_message_based_on_parser(None, f"Found {len(results)} FilesystemIDs:")
                for result in results:
                    self.print_message_based_on_parser(None, f" - {result[0]}")
            elif results_len == 1:
                filesystem_id = results[0]
                self.print_message_based_on_parser(None, f"'{volume_label}' has FilesystemID: '{filesystem_id}'")
                self.print_message_based_on_parser(None,f"Resetting directory file sizes for volume label: '{volume_label}'")
                result = self.database.reset_dir_sizes(filesystem_id)
                if isinstance(result, sqlite3.Error):
                    self.exit_cleanly(self.EXIT_ERROR, f"Error: {result}")
                else:
                    self.print_message_based_on_parser(None,
                                                       f"- '{result}' directories found and their file sizes reset: ")

                while True:
                    dirs_to_process_filesystem_entry_ids = self.database.find_directories_with_only_child_entries_with_sizes(filesystem_id)
                    if dirs_to_process_filesystem_entry_ids is None or len(dirs_to_process_filesystem_entry_ids) == 0:
                        break
                    else:
                        # Loop through dirs_to_process_filesystem_entry_ids:
                        for filesystem_entry in dirs_to_process_filesystem_entry_ids:
                            print(f"filesystem_entry: '{filesystem_entry}'")
                            filesystem_entry_id = filesystem_entry[0]
                            entry_name = filesystem_entry[1]
                            byte_size = filesystem_entry[2]
                            is_directory = filesystem_entry[3]
                            full_name = filesystem_entry[4]
                            if(is_directory == 1 and byte_size != -1):
                                self.print_message_based_on_parser(None,f" - FilesystemEntryID: '{filesystem_entry_id}'")
                                self.print_message_based_on_parser(None,f" - EntryName: '{entry_name}'")
                                self.print_message_based_on_parser(None,f" - ByteSize: '{byte_size}'")
                                self.print_message_based_on_parser(None,f" - IsDirectory: '{is_directory}'")
                                self.print_message_based_on_parser(None,f" - FullName: '{full_name}'")
                                """
                                result = self.database.calculate_directory_size(filesystem_entry_id, entry_name, byte_size)
                                if isinstance(result, sqlite3.Error):
                                    self.print_message_based_on_parser(None,f"Error: {result}")
                                else:
                                """
                                self.exit_cleanly(self.EXIT_ERROR, f"Error: Directory with size detected")
                            dir_child_filesystem_entry_ids = self.database.find_directory_direct_children(filesystem_entry_id)
                            self.print_message_based_on_parser(None, f"Found {len(dir_child_filesystem_entry_ids)} FilesystemEntryIDs:")
                            for result in dir_child_filesystem_entry_ids:
                                self.print_message_based_on_parser(None, f" - {result}")

                        self.print_message_based_on_parser(None,".")



    def subcommand_refresh_volumes(self, args: []):
        logging.debug("### F.subcommand_refresh_volumes() ###")
        """
        if not self.__program.question_yes_no("Do you want to refresh the volume list?"):
            # they selected No so don't refresh
            return
        """
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

    def delete_filesystem(self, label):
        print(f'Deleting old entries for label: "{label}"')
        result = self.database.delete_filesystem(label)
        if type(result) is not bool:
            # Must be an error message
            self.exit_cleanly(self.EXIT_ERROR, result)
        elif not result:
            # delete_filesystem(label) failed for some other reason
            self.exit_cleanly(self.EXIT_ERROR, f"Failed to delete volume with label: {label} for an unknown reason.")
        else:
            print(f'Deleted old entries for label: "{label}"')

    def subcommand_delete_volumes(self, args: []):
        logging.debug("### F.subcommand_delete_volumes() ###")
        vol_label = args.vol_label if "vol_label" in args else None
        confirm = args.confirm if "confirm" in args else None
        #verbose = args.verbose if "verbose" in args else False

        # Check if Label exists in the Database
        if self.database.does_label_exists(vol_label):
            print(f'Label "{vol_label}" exists in the Database.')
            if not confirm:
                self.exit_cleanly(self.EXIT_ERROR,
                                  f'Use the "--confirm" flag to confirm that you want to delete entries for this volume.',
                                  f'Use the "Confirm" checkbox to confirm that you want to delete entries for this volume.')
            else:
                print("Confirmation accepted")
                self.delete_filesystem(vol_label)
        else:
            self.exit_cleanly(self.EXIT_ERROR,
                              f'Label "{vol_label}" doesn\'t exist in the Database!',
                              f'Label "{vol_label}" doesn\'t exist in the Database!')

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
        volume_choice = args.volume if "volume" in args else None
        vol_label = args.vol_label if "vol_label" in args else None
        confirm = args.confirm if "confirm" in args else None
        verbose = args.verbose if "verbose" in args else False

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
            if vol_label is not None and vol_label != AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT:
                label = vol_label
            print(f'Drive: "{volume_summary_array["drive_letter"]}:"')
            print(f'Label: "{label}"')
            print(f'Hostname: "{volume_summary_array["hostname"]}"')
            print(f'Make: "{volume_summary_array["make"]}"')
            print(f'Model: "{volume_summary_array["model"]}"')
            print(f'Serial: "{volume_summary_array["serial_number"]}"')
            print('')

            # Check if Label exists in the Database
            if self.database.does_label_exists(label):
                if not confirm:
                    self.exit_cleanly(self.EXIT_ERROR, f'Label "{label}" already exists in the Database! Use the \'--confirm\' flag.', f'Label "{label}" already exists in the Database! Use the \'Confirm\' checkbox.')
                else:
                    print(f'Label "{label}" already exists in the Database.!')
                    print("Confirmation accepted")
                    self.delete_filesystem(label)

            if not self.REUSE_TEMP_LISTING_FILE:
                print('Generating the Volume Listing ...')
                output = self.system.create_path_listing(volume_summary_array["drive_letter"] + ':\\',
                                                         self.DEFAULT_TEMP_LISTING_FILE)
            else:
                print('Reusing the Volume Listing ...')

            # print(f"create_path_listing output: {output}")
            print('Processing the Volume Listing ...')
            powershell_filesystem_listing = PowerShellFilesystemListing(self, self.database, label, self.DEFAULT_TEMP_LISTING_FILE)

            # For testing
            #verbose = True

            if verbose is not None:
                powershell_filesystem_listing.set_verbose(verbose)

            powershell_filesystem_listing.set_make(volume_summary_array["make"])
            powershell_filesystem_listing.set_model(volume_summary_array["model"])
            powershell_filesystem_listing.set_serial_number(volume_summary_array["serial_number"])
            powershell_filesystem_listing.set_hostname(volume_summary_array["hostname"])
            powershell_filesystem_listing.set_memory_stats(self.memory_stats)
            #powershell_filesystem_listing.save_to_database()
            powershell_filesystem_listing.set_save_to_mode(PowerShellFilesystemListing.SAVE_TO_DATABASE)
            import_listing_success = powershell_filesystem_listing.import_listing(self.PROGRESS_INSERT_FREQUENCY)
            if import_listing_success:
                print(f"Volume {volume_summary_array["drive_letter"]}: Added Successfully...")

    def subcommand_select_database(self, args: []):
        logging.debug(f"### F.subcommand_select_database() ###")
        database_filename = args.db if "db" in args else None
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
        database_filename = args.db if "db" in args else None
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
        label = args.label if "label" in args else None
        filename = args.filename if "filename" in args else None
        powershell_filesystem_listing = PowerShellFilesystemListing(self, self.database, label, filename)

        verbose = args.verbose if "verbose" in args else False
        make = args.make if "make" in args else None
        model = args.model if "model" in args else None
        serial = args.serial if "serial" in args else None
        hostname = args.hostname if "hostname" in args else None

        if verbose is not None:
            powershell_filesystem_listing.set_verbose(verbose)
        if make is not None:
            powershell_filesystem_listing.set_make(make)
        if model is not None:
            powershell_filesystem_listing.set_model(model)
        if serial is not None:
            powershell_filesystem_listing.set_serial_number(serial)
        if hostname is not None:
            powershell_filesystem_listing.set_hostname(hostname)

        powershell_filesystem_listing.set_memory_stats(self.memory_stats)
        #powershell_filesystem_listing.save_to_database() # There is also an option to save to file, but this isn't being maintained.
        powershell_filesystem_listing.set_save_to_mode(PowerShellFilesystemListing.SAVE_TO_DATABASE)
        powershell_filesystem_listing.import_listing()

    def load_volume_drive_details(self):
        logging.debug(f"### F.load_volume_drive_details() ###")
        logging.info("Finding Logical Drives ...")
        print(f"Finding Logical Drives ...")
        self.logical_disk_array = self.system.get_logical_drives_details()
        self.display_progress_percentage(25)
        # display_array_of_dictionaries(self.logical_disk_array)
        # print(f"logical_disk_array: {self.logical_disk_array}")

        logging.info("Finding Physical Drives ...")
        print(f"Finding Physical Drives ...")
        self.physical_disk_array = self.system.get_physical_drives_details()
        #print(f'progress: 50/100')
        self.display_progress_percentage(50)
        # print(f"physical_disk_array: {self.physical_disk_array}")

        logging.info("Finding Volumes ...")
        print(f"Finding Volumes ...")
        self.volumes_array = self.system.get_volumes(True)
        #print(f'progress: 75/100')
        self.display_progress_percentage(75)
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
        progress_bar_starting_percentage = 75
        function_total_percentage = 100 - progress_bar_starting_percentage
        volume_array_length = len(self.volumes_array)
        for volume_dictionary in self.volumes_array:
            # Initialise the volume_array_of_dicts with the volume_dictionary
            volume_array_of_dicts = [volume_dictionary]
            drive_letter = f'{volume_dictionary['DriveLetter']}:'
            disk_number = self.system.get_disk_number_for_drive_letter(drive_letter)
            # print(f"{drive_letter} is on drive {disk_number}")

            volume_info_line = f"{volume_dictionary['DriveLetter']}: \"{volume_dictionary['FileSystemLabel']}\" {Convert.bytesize2string(int(volume_dictionary['Size']), True, 1)}, {volume_dictionary['FileSystemType']} ({volume_dictionary['HealthStatus']})"
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
            volume_array_progress_percentage = int((option_number / volume_array_length) * function_total_percentage)
            progress_percentage = progress_bar_starting_percentage + volume_array_progress_percentage
            #print(f'progress: {progress_percentage}/100')
            self.display_progress_percentage(progress_percentage)
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
        #print(f'progress: 0/100')
        self.display_progress_percentage(0)

        database_changed = False
        if 'db' in args:
            self.set_configuration_value(self.CONFIG_DATABASE_FILENAME, args.db, AddArgs.DEFAULT_DATABASE_FILENAME)
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
        subcommand = args.subcommand if "subcommand" in args else None
        if subcommand == AddArgs.SUBCMD_SELECT_DATABASE:
            self.subcommand_select_database(args)
        elif subcommand == AddArgs.SUBCMD_CREATE_DATABASE:
            self.subcommand_create_database(args)
        elif subcommand == AddArgs.SUBCMD_REFRESH_VOLUMES:
            self.subcommand_refresh_volumes(args)
        else:
            # These subcommands all need a working database connection
            verbose = args.verbose if "verbose" in args else False
            if verbose is not None:
                self.database.set_verbose_mode(verbose)
            start_time = time.time()

            if subcommand == AddArgs.SUBCMD_FILE_SEARCH:
                self.subcommand_filesystem_search(args)

            elif subcommand == AddArgs.SUBCMD_DUPLICATES_SEARCH:
                self.subcommand_filesystem_duplicates_search(args)

            elif subcommand == AddArgs.SUBCMD_CALC_DIR_SIZES:
                self.subcommand_calculate_directory_sizes(args)

            elif subcommand == AddArgs.SUBCMD_ADD_VOLUME:
                self.subcommand_add_volumes(args)

            elif subcommand == AddArgs.SUBCMD_DELETE_VOLUME:
                self.subcommand_delete_volumes(args)

            elif subcommand == AddArgs.SUBCMD_IMPORT_VOLUME:
                self.subcommand_import_listing(args)

            elif subcommand == AddArgs.SUBCMD_UPGRADE_DATABASE:
                self.subcommand_upgrade_database()

            elif subcommand == AddArgs.SUBCMD_VACUUM_DATABASE:
                self.subcommand_vacuum_database()

            elif subcommand == AddArgs.SUBCMD_RESET_DATABASE:
                self.subcommand_reset_database(args)

            end_time = time.time()

            #print(f"Time in seconds: {end_time - start_time}")

        # Close the database cleanly now that we have finished with it (even if it wasn't used)
        self.database.close_database()

        # Clean up and exit
        self.clean_up()
        #print(f'progress: 100/100')
        self.display_progress_percentage(100)

if __name__ == "__main__":
    pass
