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
from data import find_dictionary_in_array
from format import format_storage_size

def add_db_and_verbose_to_parser(parser):
    parser.add_argument("-d", "--db", default="database.sqlite",
                               help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
    parser.add_argument("-v", "--verbose", action="store_true", help="increase output verbosity")

def clean_up_and_quit():
    # Now that the subcommands have been run, close the database cleanly
    database.close_database()

    if MEMORY_STATS:
        # Stop tracing memory allocations
        tracemalloc.stop()

    # Exit normally
    exit()

MEMORY_STATS = False

if MEMORY_STATS:
    # Start tracing memory allocations
    tracemalloc.start()

# Press the green button in the gutter to run the script.
#if __name__ == '__main__':
#    print("!!! Starting !!!")

parser=argparse.ArgumentParser(
#    prog='Filer',
#    epilog='Text at the bottom of help',
    description="Filer - File System Manager")
#parser.add_argument("-t", "--test", action="store_true", help="test input file without modifying the database")

subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands',
                                   required=True,
                                   dest='subcommand',
                                   help='additional help')

parser_find = subparsers.add_parser('find',
                                    help='find help',
                                    description='Find files exactly matching (case sensitive) the provided filename. (Faster than "like")')
parser_find.add_argument("filename", help="filename to be found.")
add_db_and_verbose_to_parser(parser_find)

parser_like = subparsers.add_parser('like',
                                    help='like help',
                                    description='Find files with filenames like the provided search (case insensitive). "%xyz%" = filenames containing "xyz". "xyz%" = filenames starting with xyz. "%xyz" = filenames ending with xyz. (Slower than "find")')
parser_like.add_argument("search", help="search string to be found.")
add_db_and_verbose_to_parser(parser_like)

# create the parser for the "import" subcommand
parser_import = subparsers.add_parser('import', help='import help')
parser_import.add_argument("label", help="listings' unique label string")
parser_import.add_argument("listing_filename", help="filename (including path) of the listing in fixed width format to be processed. See PowerShell example.")
parser_import.add_argument("-m", "--make", default=None, help="drive's make")
parser_import.add_argument("-o", "--model", default=None, help="drive's model")
parser_import.add_argument("-s", "--serial", default=None, help="drive's serial number")
parser_import.add_argument("-c", "--combined", default=None, help="drive's combined string in format \"make,model,serial-number\"")
parser_import.add_argument("-n", "--hostname", default=None, help="hostname of the machine containing the drive")
parser_import.add_argument("-p", "--prefix", default=None, help="prefix to remove from the start of each file's path. e.g. \"C:\\Users\\username\"")
parser_import.add_argument("-t", "--test", action="store_true", help="test input file without modifying the database")
add_db_and_verbose_to_parser(parser_import)

# create the parser for the "interactive" subcommand
parser_interactive = subparsers.add_parser('interactive', help='interactive help')
parser_interactive.add_argument("-t", "--test", action="store_true", help="test input file without modifying the database")
add_db_and_verbose_to_parser(parser_interactive)

# create the parser for the "vacuum" subcommand
parser_vacuum = subparsers.add_parser('vacuum',
                                      help='vacuum help',
                                      description='The VACUUM subcommand rebuilds the database file by reading the current file and writing the content into a new file. As a result it repacking it into a minimal amount of disk space and defragments it which ensures that each table and index is largely stored contiguously. Depending on the size of the database it can take some time to do perform.')
add_db_and_verbose_to_parser(parser_vacuum)

parser_reset = subparsers.add_parser('reset',
                                      help='reset help',
                                      description='Warning: Using the "reset" subcommand will delete the specified database and replace it with an empty one.')
add_db_and_verbose_to_parser(parser_reset)

args=parser.parse_args()

# Debug
#print(f"args: '{args}'")
#print(f"subcommand: '{args.subcommand}'")
#quit()

# These subcommands don't require a database
if args.subcommand == "version":
    version = "0.1 Alpha"
    print(f"Version: {version}")
    quit()

# The following subcommands all require a database
database_filename = args.db

# Does the database file exit?
create_tables = False

directory_name = os.path.dirname(database_filename)

if not os.path.exists(directory_name):
    print(f"\"{directory_name}\" directory in your database filename path, does not exist!")
    print("The directory must exist before a new database can be created there. Exiting")
    exit(2)

if not os.path.isfile(database_filename):
    # Database file doesn't exist
    # Ask user if they want to create a new database file?
    print(f"Database file doesn't exist at location: \"{os.path.abspath(database_filename)}\"")
    create_database_answer = input("Do you want to create a new database there? ")
    if create_database_answer.lower() == "y" or create_database_answer.lower() == "yes":
        create_tables = True
    else:
        print("Database not created. Exiting")
        exit(2)

# If not, ask the user if they want to create a new database at the specified location (give the full path as well)

database = Database(database_filename, create_tables)
database.set_verbose_mode(args.verbose)
if create_tables:
    database.create_database_structure()

if args.subcommand == "find":
    print(f"Finding filenames matching \"{args.filename}\" :")
    database.find_filename_exact_match(args.filename)

elif args.subcommand == "like":
    print(f"Finding filenames like \"{args.search}\" :")
    database.find_filename_like(args.search)

elif args.subcommand == "vacuum":
    print(f"Vacuuming database. This may take a while depending on the your database size.")
    database.vacuum()
    print(f"Vacuuming finished.")

elif args.subcommand == "reset":
    print(f"Not implemented yet")

elif args.subcommand == "import":
    print(f"Import subcommand: Not fully implemented yet!")
    powershell_filesystem_listing = PowerShellFilesystemListing(database, args.label, args.listing_filename)

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

    powershell_filesystem_listing.set_memory_stats(MEMORY_STATS)
    powershell_filesystem_listing.save_to_database()

    powershell_filesystem_listing.import_listing()

elif args.subcommand == 'interactive':
    system = System()

    while True:
        print("Finding Logical Drives ...")
        logical_disk_array = system.get_logical_drives_details()
        print("Finding Physical Drives ...")
        physical_disk_array = system.get_physical_drives_details()
        #print(f"physical_disk_array: {physical_disk_array}")
        #display_array_of_dictionaries(drives)
        print("Finding Volumes ...")
        volumes_array = system.get_volumes(True)
        #print(f"volumes: {volumes}")
        #display_array_of_dictionaries(volumes_array)
        #display_diff_dictionaries(volumes[0], volumes[1])
        print("Matching Volumes to Drives ...")
        RESCAN: str = 'Rescan'
        EXIT: str = 'Exit'
        VOLUME_DICT_INDEX: int = 0
        LOGICAL_DICT_INDEX: int = 1
        PHYSICAL_DICT_INDEX: int = 1
        option_number = 1
        options = []
        options_descriptions = []
        options_results = []
        for volume_dictionary in volumes_array:
            options.append(str(option_number))
            volume_array_of_dicts = []
            volume_array_of_dicts.append(volume_dictionary)
            drive_letter = f'{volume_dictionary['DriveLetter']}:'
            #print(f"{drive_letter} is on drive {system.get_disk_number_for_drive_letter(drive_letter)}")
            disk_number = system.get_disk_number_for_drive_letter(drive_letter)
            volume_info_line = f"{volume_dictionary['DriveLetter']}: \"{volume_dictionary['FileSystemLabel']}\" {format_storage_size(int(volume_dictionary['Size']), True, 1)}, {volume_dictionary['FileSystemType']} ({volume_dictionary['HealthStatus']})"
            if len(disk_number.strip()) != 0:
                logical_disk_dictionary = find_dictionary_in_array(logical_disk_array, "DiskNumber", disk_number)
                volume_array_of_dicts.append(logical_disk_dictionary)
                physical_disk_dictionary = find_dictionary_in_array(physical_disk_array, "DeviceId", disk_number)
                volume_array_of_dicts.append(physical_disk_dictionary)
                if logical_disk_dictionary is not None:
                    volume_info_line += f" / {logical_disk_dictionary['BusType']} {physical_disk_dictionary['MediaType']}: {logical_disk_dictionary['Manufacturer']}, {logical_disk_dictionary['Model']}, SN: {logical_disk_dictionary['SerialNumber']} ({logical_disk_dictionary['HealthStatus']}))"
                else:
                    volume_info_line += ""
            options_descriptions.append(volume_info_line)
            options_results.append(volume_array_of_dicts)
            option_number += 1

        # Add Rescan option
        options.append('R')
        options_descriptions.append(RESCAN)
        options_results.append(RESCAN)
        option_number += 1
        # Add Exit option
        options.append('E')
        options_descriptions.append(EXIT)
        options_results.append(EXIT)
        option_number += 1

        result_array = System.get_input("Please select a volume to process?", options, options_descriptions, options_results)
        if isinstance(result_array, str):
            # Test if result is a string first as strings are technically arrays as well
            #print(f"String result: {result_array}")
            if result_array == EXIT:
                print("Exiting ...")
                exit()
            elif result_array == RESCAN:
                pass # Rescanning happens anyway at the end of this loop. This option just skips processing a volume
            else:
                print("Invalid result")
                print("Exiting ...")
                break # Leave the interactive loop
        elif isinstance(result_array, collections.abc.Sequence):
            #display_array_of_dictionaries(result_array)
            drive_letter = result_array[VOLUME_DICT_INDEX]['DriveLetter']
            print(f"Processing Volume {drive_letter}:\\ ...")
            output = system.create_path_listing(drive_letter+':\\')

        print("Rescanning ...")

clean_up_and_quit()
