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
from system import System
from file_types import FileTypes
import time
from typing import (
    Iterable,
    Union,
    Optional,
)

class F:

    VOLUME_DICT_INDEX: int = 0
    LOGICAL_DICT_INDEX: int = 1
    PHYSICAL_DICT_INDEX: int = 2

    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf'

    SUBCOMMAND_SEARCH: str = 'search'
    SUBCOMMAND_IMPORT: str = 'import'
    SUBCOMMAND_CREATE: str = 'create'
    SUBCOMMAND_UPGRADE: str = 'upgrade'
    SUBCOMMAND_VACUUM: str = 'vacuum'
    SUBCOMMAND_RESET: str = 'reset'

    def __init__(self):
        self.database = None
        self.memory_stats = False

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

    def search(self, args: []):
        print(f"Finding filenames:")
        self.database.find_filenames_search(args.search, args.type, args.label)

    def create(self, args: []):
        database_filename = args.db
        abspath_database_filename = os.path.abspath(database_filename)
        directory_name = os.path.dirname(abspath_database_filename)
        # Does the directory exist where we want to create the database?
        if not os.path.exists(directory_name):
            print(f"\"{directory_name}\" directory in your database filename path, does not exist!")
            print("The directory must exist before a new database can be created there.")
            exit(2)

        if os.path.isfile(database_filename):
            # Database file doesn't exist
            # Ask user if they want to create a new database file?
            print(f"Database file already exists at location: \"{os.path.abspath(database_filename)}\"")
            print(f"To empty the database, use the \'{F.SUBCOMMAND_RESET}\' subcommand.")
            exit(2)

        self.database = Database(database_filename)
        if "verbose" in args:
            self.database.set_verbose_mode(args.verbose)

        self.database.create_database_structure()

    def upgrade(self):
        print(f"Upgrading database. This may take a while depending on the your database size.")
        self.database.upgrade_database()
        print(f"Upgrading finished.")

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

    @staticmethod
    def add_argument(parser, *temp_args, **temp_kwargs): # : Optional[Union[Iterable, dict]]
        #parser.add_argument(temp_args, temp_kwargs)
        if type(parser) is argparse.ArgumentParser:
            # Remove GooeyParser parameters as they aren't compatible with the ArgumentParser
            temp_kwargs.pop("metavar", None)
            temp_kwargs.pop("widget", None)
        #print(f"temp_args: {temp_args}")
        #print(f"temp_kwargs: {temp_kwargs}")
        parser.add_argument( *temp_args, **temp_kwargs )

    @staticmethod
    def add_db_to_parser(parser, create: bool=False):
        #print(f"Parser type: {type(parser)}")
        if type(parser) is argparse.ArgumentParser:
            F.add_argument(parser, "-d", "--db", default="database.sqlite",
                            help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
        else:
            if create:
                F.add_argument(parser, "-d", "--db", default="database.sqlite",
                                    widget = 'FileSaver',
                                    metavar='Database Filename',
                                    help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.")
            else:
                F.add_argument(parser, "-d", "--db", default="database.sqlite",
                                    widget = 'FileChooser',
                                    metavar='Database Filename',
                                    help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.")

    @staticmethod
    def add_verbose_to_parser(parser, create: bool = False):
        F.add_argument(parser, "-v", "--verbose",
                            action="store_true",
                            metavar='Verbose',
                            help="Verbose output")

    @staticmethod
    def add_subcommands_to_parser(parser):
        file_type_categories = FileTypes.get_file_types_categories()
        #print(f"file_type_categories: {file_type_categories}")

        subparsers = parser.add_subparsers(title='subcommands',
                                           description='valid subcommands',
                                           required=True,
                                           dest='subcommand',
                                           help='additional help')

        parser_search = subparsers.add_parser('search',
                                            help='search help',
                                            description='Search for files based on search strings (slower than "find")')
        parser_search.add_argument("-s", "--search", metavar='Search',
        help='''Search string to be found within filenames
         - if search doesn't include '%' or '_' characters, then it is a fast exact case-sensitive search
         - if search includes '%' or '_' characters, then it is a slower pattern match case-insensitive search
         - '%' wildcard matches any sequence of zero or more characters
         - '_' wildcard matches exactly one character
         ''')
        parser_search.add_argument("-t", "--type", metavar='Type', choices=file_type_categories, nargs='?', help="Type of files to be considered")
        parser_search.add_argument("-l", "--label", metavar='Label', default=None, help="Label of the drive listing")
        F.add_db_to_parser(parser_search)
        F.add_verbose_to_parser(parser_search)

        # create the parser for the "import" subcommand
        parser_import = subparsers.add_parser('import', help='import help')
        F.add_db_to_parser(parser_import)
        F.add_argument(parser_import, "label", metavar='Label', help="Label of the drive listing")
        """
        if type(parser) is argparse.ArgumentParser:
            parser_import.add_argument("filename", metavar='Filename',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
        else:
            parser_import.add_argument("filename", metavar='Filename', widget = 'FileChooser',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
        """
        F.add_argument(parser_import, "filename", metavar='Filename', widget='FileChooser',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
        F.add_argument(parser_import, "-m", "--make", metavar='Make', default=None, help="Make of the drive")
        F.add_argument(parser_import, "-o", "--model", metavar='Model', default=None, help="Model of the drive")
        F.add_argument(parser_import, "-s", "--serial", metavar='Serial Number', default=None, help="Serial number of the drive")
        F.add_argument(parser_import, "-c", "--combined", metavar='Combined', default=None,
                                   help="Combined drive information string, in format \"make,model,serial-number\"")
        F.add_argument(parser_import, "-n", "--hostname", metavar='Hostname', default=None,
                                   help="Hostname of the machine containing the drive")
        F.add_argument(parser_import, "-p", "--prefix", metavar='Prefix', default=None,
                                   help="Prefix to remove from the start of each file's path. e.g. \"C:\\Users\\username\"")
        F.add_argument(parser_import, "-t", "--test", metavar='Test', action="store_true",
                                   help="Test input file without modifying the database")
        F.add_verbose_to_parser(parser_import)

        parser_create = subparsers.add_parser('create',
                                              help='find help',
                                              description='Create an empty database')
        F.add_db_to_parser(parser_create, True)
        F.add_verbose_to_parser(parser_create)

        # create the parser for the "vacuum" subcommand
        parser_upgrade = subparsers.add_parser('upgrade',
                                              help='upgrade help',
                                              description='The UPGRADE subcommand upgrades the database file to the latest structure needed for this program to work.')
        F.add_db_to_parser(parser_upgrade)
        F.add_verbose_to_parser(parser_upgrade)

        # create the parser for the "vacuum" subcommand
        parser_vacuum = subparsers.add_parser('vacuum',
                                              help='vacuum help',
                                              description='The VACUUM subcommand rebuilds the database file by reading the current file and writing the content into a new file. As a result it repacking it into a minimal amount of disk space and defragments it which ensures that each table and index is largely stored contiguously. Depending on the size of the database it can take some time to do perform.')
        F.add_db_to_parser(parser_vacuum)
        F.add_verbose_to_parser(parser_vacuum)

        parser_reset = subparsers.add_parser('reset',
                                             help='reset help',
                                             description='Warning: Using the "reset" subcommand will delete the specified database and replace it with an empty one.')
        F.add_db_to_parser(parser_reset)
        F.add_verbose_to_parser(parser_reset)

    def process_args_and_call_subcommand(self, args):

        # If 'create' subcommand specified, then we don't need to open the database
        if args.subcommand == F.SUBCOMMAND_CREATE:
            self.create(args)

        else:
            # These subcommands all need a working database connection
            # The following subcommands all require a database
            database_filename = args.db

            if not os.path.isfile(database_filename):
                # Database file doesn't exist
                # Ask user if they want to create a new database file?
                print(f"Database file doesn't exist at location: \"{os.path.abspath(database_filename)}\"")
                print(f"Please create the Database using the \'create\' subcommand.")
                exit(2)

            self.database = Database(database_filename)

            if "verbose" in args:
                self.database.set_verbose_mode(args.verbose)

            start_time = time.time()

            if args.subcommand == F.SUBCOMMAND_SEARCH:
                self.search(args)

            elif args.subcommand == F.SUBCOMMAND_IMPORT:
                self.import_listing(args)

            elif args.subcommand == F.SUBCOMMAND_UPGRADE:
                self.upgrade()

            elif args.subcommand == F.SUBCOMMAND_VACUUM:
                self.vacuum()

            elif args.subcommand == F.SUBCOMMAND_RESET:
                self.reset(args)

            end_time = time.time()

            #print(f"Time in seconds: {end_time - start_time}")

        # Clean up and exit
        self.clean_up_and_quit()
        print("")

    def start(self):

        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

        parser=argparse.ArgumentParser(
            description="Filer - File Cataloger"
        )

        F.add_subcommands_to_parser(parser)

        args=parser.parse_args()

        # Debug
        #print(f"args: '{args}'")
        #print(f"subcommand: '{args.subcommand}'")
        #quit()

        self.process_args_and_call_subcommand(args)
        # Command finished so program finished

if __name__ == "__main__":
    f = F()
    f.start()

