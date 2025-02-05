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

class F:

    VOLUME_DICT_INDEX: int = 0
    LOGICAL_DICT_INDEX: int = 1
    PHYSICAL_DICT_INDEX: int = 2

    DEFAULT_TEMP_LISTING_FILE: str = 'filer.fwf'

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

    @staticmethod
    def add_db_to_parser(parser, create: bool=False):
        #print(f"Parser type: {type(parser)}")
        if type(parser) is argparse.ArgumentParser:
            parser.add_argument("-d", "--db", default="database.sqlite",
                            help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
        else:
            if create:
                parser.add_argument("-d", "--db", default="database.sqlite",
                                    widget = 'FileSaver',
                                    metavar='Database Filename',
                                    help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.")
            else:
                parser.add_argument("-d", "--db", default="database.sqlite",
                                    widget = 'FileChooser',
                                    metavar='Database Filename',
                                    help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.")

    @staticmethod
    def add_verbose_to_parser(parser, create: bool = False):
        parser.add_argument("-v", "--verbose",
                            action="store_true",
                            metavar='Verbose',
                            help="Verbose output")

    @staticmethod
    def add_subcommands_to_parser(parser):
        subparsers = parser.add_subparsers(title='subcommands',
                                           description='valid subcommands',
                                           required=True,
                                           dest='subcommand',
                                           help='additional help')

        parser_create = subparsers.add_parser('create',
                                            help='find help',
                                            description='Create an empty database')
        F.add_db_to_parser(parser_create, True)
        F.add_verbose_to_parser(parser_create)

        parser_find = subparsers.add_parser('find',
                                            help='find help',
                                            description='Find files exactly matching (case sensitive) the provided filename. (Faster than "like")')
        F.add_db_to_parser(parser_find)
        parser_find.add_argument("-l", "--label", default=None, metavar='Label', help="Label of the drive listing")
        parser_find.add_argument("filename", metavar='Filename', help="Exact name of the file to be found (case-sensitive)")
        #parser_find.add_argument("-t", "--type", metavar='Type', choices=['Any','Audio','Documents','Images','Video'], default='Any', nargs='?', help="Type of files to be considered")
        parser_find.add_argument("-t", "--type", metavar='Type', choices=['Audio','Document','Image','Video'], nargs='?', help="Type of files to be considered")
        F.add_verbose_to_parser(parser_find)

        parser_like = subparsers.add_parser('like',
                                            help='like help',
                                            description='Find files with filenames like the provided search (case insensitive). "%xyz%" = filenames containing "xyz". "xyz%" = filenames starting with xyz. "%xyz" = filenames ending with xyz. (Slower than "find")')
        F.add_db_to_parser(parser_like)
        parser_like.add_argument("-l", "--label", default=None, metavar='Label', help="Label of the drive listing")
        parser_like.add_argument("search", metavar='Search String', help="Search string to be found within filenames (case-insensitive)\nxyz% - find filenames starting with 'xyz'\n%xyz - find filenames ending with 'xyz'\nSee SQL LIKE command for further options")
        parser_find.add_argument("-t", "--type", metavar='Type', choices=['Audio','Document','Image','Video'], nargs='?', help="Type of files to be considered")
        F.add_verbose_to_parser(parser_like)

        # create the parser for the "import" subcommand
        parser_import = subparsers.add_parser('import', help='import help')
        F.add_db_to_parser(parser_import)
        parser_import.add_argument("label", metavar='Label', help="Label of the drive listing")
        if type(parser) is argparse.ArgumentParser:
            parser_import.add_argument("filename", metavar='Filename',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
        else:
            parser_import.add_argument("filename", metavar='Filename', widget = 'FileChooser',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
        parser_import.add_argument("-m", "--make", metavar='Make', default=None, help="Make of the drive")
        parser_import.add_argument("-o", "--model", metavar='Model', default=None, help="Model of the drive")
        parser_import.add_argument("-s", "--serial", metavar='Serial Number', default=None, help="Serial number of the drive")
        parser_import.add_argument("-c", "--combined", metavar='Combined', default=None,
                                   help="Combined drive information string, in format \"make,model,serial-number\"")
        parser_import.add_argument("-n", "--hostname", metavar='Hostname', default=None,
                                   help="Hostname of the machine containing the drive")
        parser_import.add_argument("-p", "--prefix", metavar='Prefix', default=None,
                                   help="Prefix to remove from the start of each file's path. e.g. \"C:\\Users\\username\"")
        parser_import.add_argument("-t", "--test", metavar='Test', action="store_true",
                                   help="Test input file without modifying the database")
        F.add_verbose_to_parser(parser_import)

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

        if args.subcommand == "find":
            self.find(args)

        elif args.subcommand == "like":
            self.like(args)

        elif args.subcommand == "vacuum":
            self.vacuum()

        elif args.subcommand == "reset":
            self.reset(args)

        elif args.subcommand == "import":
            self.import_listing(args)

        # Clean up and exit
        self.clean_up_and_quit()

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

