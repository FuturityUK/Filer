import argparse
import logging
import socket
from file_types import FileTypes
#from f import F

class AddArgs:

    SHOW_DB_FILENAME_ARG_IN_GUI: bool = False
    SHOW_VERBOSE_ARG_IN_GUI: bool = False
    SHOW_FILE_SEARCH_ARG_IN_GUI: bool = True

    SUBCMD_INSTRUCTIONS: str = 'instructions'
    SUBCMD_FILE_SEARCH: str = 'file_search'
    SUBCMD_DUPLICATES_SEARCH: str = 'duplicates_search'
    SUBCMD_CALC_DIR_SIZES: str = 'calc_dir_sizes'
    SUBCMD_REFRESH_VOLUMES: str = 'refresh_volumes'
    SUBCMD_ADD_VOLUME: str = 'add_volume'
    SUBCMD_DELETE_VOLUME: str = 'delete_volume'
    SUBCMD_IMPORT_VOLUME: str = 'import_volume'
    SUBCMD_CREATE_DATABASE: str = 'create_db'
    SUBCMD_SELECT_DATABASE: str = 'select_db'
    SUBCMD_UPGRADE_DATABASE: str = 'upgrade_db'
    SUBCMD_VACUUM_DATABASE: str = 'vacuum_db'
    SUBCMD_RESET_DATABASE: str = 'reset_db'

    #SUBCMD_FILE_SEARCH_DEFAULT: str = '%'
    SUBCMD_FILE_SEARCH_DEFAULT: str = None

    SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS: str = '- All Labels -'

    SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE: str = '100'
    SUBCMD_FILE_SEARCH_MAX_RESULTS_CHOICES: list = ['25', '50', '100', '250', '500', '1000', '10000', '100000']

    SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_ASCENDING: str = 'Full Path (A -> Z)'
    SUBCMD_FILE_SEARCH_ORDER_FILENAME_ASCENDING: str = 'Filename (A -> Z)'
    SUBCMD_FILE_SEARCH_ORDER_SIZE_ASCENDING: str = 'Size (Smallest -> Largest)'
    SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_ASCENDING: str = 'Last Modified (Oldest -> Newest)'
    SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_DESCENDING: str = 'Full Path (Z -> A)'
    SUBCMD_FILE_SEARCH_ORDER_FILENAME_DESCENDING: str = 'Filename (Z -> A)'
    SUBCMD_FILE_SEARCH_ORDER_SIZE_DESCENDING: str = 'Size (Largest -> Smallest)'
    SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_DESCENDING: str = 'Last Modified (Newest -> Oldest)'
    SUBCMD_FILE_SEARCH_ORDER_DEFAULT_CHOICE: str = SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_ASCENDING
    SUBCMD_FILE_SEARCH_ORDER_CHOICES: list = [SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_DESCENDING, SUBCMD_FILE_SEARCH_ORDER_FILENAME_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_FILENAME_DESCENDING,
                                                SUBCMD_FILE_SEARCH_ORDER_SIZE_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_SIZE_DESCENDING, SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_DESCENDING]


    SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_ASCENDING: str = 'Duplicates (Smallest -> Largest)'
    SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_DESCENDING: str = 'Duplicates (Largest -> Smallest)'
    SUBCMD_DUPLICATES_SEARCH_ORDER_DEFAULT_CHOICE: str = SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_DESCENDING
    SUBCMD_DUPLICATES_SEARCH_ORDER_CHOICES: list = [SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_DESCENDING, SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_ASCENDING,
                                                    SUBCMD_FILE_SEARCH_ORDER_SIZE_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_SIZE_DESCENDING,
                                                    SUBCMD_FILE_SEARCH_ORDER_FILENAME_ASCENDING, SUBCMD_FILE_SEARCH_ORDER_FILENAME_DESCENDING]

    SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES: str = 'Files'
    SUBCMD_FILE_SEARCH_SEARCH_FOR_DIRECTORIES: str = 'Directories'
    SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING: str = 'Everything'
    SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICES: list = [SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES, SUBCMD_FILE_SEARCH_SEARCH_FOR_DIRECTORIES, SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING]
    SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICE: str = SUBCMD_FILE_SEARCH_SEARCH_FOR_EVERYTHING
    SUBCMD_DUPLICATES_SEARCH_SEARCH_FOR_CHOICE: str = SUBCMD_FILE_SEARCH_SEARCH_FOR_FILES

    SUBCMD_FILE_SEARCH_SIZE_ALL_FILES: str = ""
    SUBCMD_FILE_SEARCH_SIZE_CHOICE: str = SUBCMD_FILE_SEARCH_SIZE_ALL_FILES
    # SUBCMD_FILE_SEARCH_SIZE_CHOICES: list = [SUBCMD_FILE_SEARCH_SIZE_ALL_FILES, '>= 1 MB', '>= 10 MB', '>= 100 MB', '>= 1 GB', '>= 10 GB', '>= 100 GB', '>= 1 TB', '< 1 MB', '< 10 MB', '< 100 MB', '< 1 GB', '< 10 GB', '< 100 GB', '< 1 TB']
    SUBCMD_FILE_SEARCH_SIZE_CHOICES: list = [SUBCMD_FILE_SEARCH_SIZE_ALL_FILES, '1 KB', '1 MB', '10 MB', '100 MB', '1 GB', '10 GB', '100 GB', '1 TB']

    SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT: str = ""

    DEFAULT_DATABASE_FILENAME: str = 'database.sqlite'

    SHOW_ATTRIBUTES_EXTRA_HELP: str = "'D' Directory, 'A' Archive, 'R' Read-only, 'H' Hidden, 'S' System, 'L' Link"

    def __init__(self, f):
        self.f = f

    @staticmethod
    def add_subcommands_to_parser(parser):
        logging.debug(f"### AddArgs.add_subcommands_to_parser() ###")

        subparsers = parser.add_subparsers(title='subcommands',
                                           description='valid subcommands',
                                           required=True,
                                           dest='subcommand',
                                           help='additional help')
        if not AddArgs.is_std_argument_parser(parser):
            AddArgs.add_subcommand_instructions_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_filesystem_search_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_filesystem_duplicates_search_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_filesystem_calc_dir_sizes_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_add_volume_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_refresh_volumes_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_delete_volume_arguments_to_parser(subparsers)

        #AddArgs.add_subcommand_create_database_arguments_to_parser(subparsers)
        #AddArgs.add_subcommand_select_database_arguments_to_parser(subparsers)


        """
        # create the parser for the "import" subcommand
        parser_import = subparsers.add_parser(AddArgs.SUBCMD_IMPORT_VOLUME, help=AddArgs.SUBCMD_IMPORT_VOLUME+' help')
        AddArgs.add_db_argument_to_parser(parser_import)
        AddArgs.add_argument(parser_import, "-l", "--label", metavar='Label', help="Label of the drive listing")
        AddArgs.add_argument(parser_import, "-f", "--filename", metavar='Filename', widget='FileChooser',
                                   help="Filename (including path) of the listing in fixed width format to be processed. See PowerShell example")
        #AddArgs.add_argument(parser_import, "-m", "--make", dest='make', metavar='Make', default=None, help="Make of the drive")
        AddArgs.add_argument(parser_import, "-m", "--make", dest='make', metavar='Make', help="Make of the drive")
        AddArgs.add_argument(parser_import, "-o", "--model", dest='model', metavar='Model', help="Model of the drive")
        AddArgs.add_argument(parser_import, "-s", "--serial", dest='serial', metavar='Serial Number', help="Serial number of the drive")
        AddArgs.add_argument(parser_import, "-n", "--hostname", dest='hostname', metavar='Hostname',
                                   help="Hostname of the machine containing the drive")
        AddArgs.add_verbose_argument_to_parser(parser_import)



        # create the parser for the "vacuum" subcommand
        parser_upgrade = subparsers.add_parser(AddArgs.SUBCMD_UPGRADE_DATABASE,
                                              help=AddArgs.SUBCMD_UPGRADE_DATABASE+' help',
                                              description='The UPGRADE subcommand upgrades the database file to the latest structure needed for this program to work.')
        AddArgs.add_db_argument_to_parser(parser_upgrade)
        AddArgs.add_verbose_argument_to_parser(parser_upgrade)

        # create the parser for the "vacuum" subcommand
        parser_vacuum = subparsers.add_parser(AddArgs.SUBCMD_VACUUM_DATABASE,
                                              help=AddArgs.SUBCMD_VACUUM_DATABASE+' help',
                                              description='The VACUUM subcommand rebuilds the database file by reading the current file and writing the content into a new file. As a result it repacking it into a minimal amount of disk space and defragments it which ensures that each table and index is largely stored contiguously. Depending on the size of the database it can take some time to do perform.')
        AddArgs.add_db_argument_to_parser(parser_vacuum)
        AddArgs.add_verbose_argument_to_parser(parser_vacuum)

        parser_reset = subparsers.add_parser(AddArgs.SUBCMD_RESET_DATABASE,
                                             help=AddArgs.SUBCMD_RESET_DATABASE+' help',
                                             description='Warning: Using the "reset" subcommand will delete the specified database and replace it with an empty one.')
        AddArgs.add_db_argument_to_parser(parser_reset)
        AddArgs.add_verbose_argument_to_parser(parser_reset)
        """

    @staticmethod
    def is_std_argument_parser(parser):
        if type(parser) is argparse.ArgumentParser or type(parser) is argparse._ArgumentGroup:
            return True
        else:
            return False

    @staticmethod
    def get_message_based_on_parser(parser, argumentparser_message, non_argumentparser_message):
        if AddArgs.is_std_argument_parser(parser):
            return argumentparser_message
        else:
            return non_argumentparser_message

    @staticmethod
    def add_argument(parser, *temp_args, **temp_kwargs):  # : Optional[Union[Iterable, dict]]
        # logging.debug(f"### AddArgs.create_volume_options() ###")
        # parser.add_argument(temp_args, temp_kwargs)
        # logging.debug(f"type(parser): {type(parser)}")
        # logging.debug(f"BEFORE: temp_kwargs: {temp_kwargs}")
        if AddArgs.is_std_argument_parser(parser):
            # Remove GooeyParser parameters as they aren't compatible with the ArgumentParser
            # logging.debug(f"== argparse.ArgumentParser")
            temp_kwargs.pop("metavar", None)
            temp_kwargs.pop("widget", None)
            temp_kwargs.pop("gooey_options", None)
            temp_kwargs.pop("prog", None)
        # logging.debug(f"AFTER : temp_kwargs: {temp_kwargs}")
        parser.add_argument(*temp_args, **temp_kwargs)

    @staticmethod
    def add_db_argument_to_parser(parser, create: bool = False):
        # print(f"Parser type: {type(parser)}")
        """
        if AddArgs.is_std_argument_parser(parser):
            AddArgs.add_argument(parser, "-d", "--db", dest='db', default=AddArgs.DEFAULT_DATABASE_FILENAME,
                            help="database filename (including path if necessary). Default='database.sqlite' in the current directory.")
        else:
        """
        if create:
            AddArgs.add_argument(parser, "--db", dest='db', default=AddArgs.DEFAULT_DATABASE_FILENAME,
                           widget='FileSaver',
                           metavar='Database Filename',
                           help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.",
                           gooey_options={'visible': AddArgs.SHOW_DB_FILENAME_ARG_IN_GUI})
        else:
            AddArgs.add_argument(parser, "--db", dest='db', default=AddArgs.DEFAULT_DATABASE_FILENAME,
                           widget='FileChooser',
                           metavar='Database Filename',
                           help="Database filename (including path if necessary). Default='database.sqlite' in the current directory.",
                           gooey_options={'visible': AddArgs.SHOW_DB_FILENAME_ARG_IN_GUI})

    @staticmethod
    def add_verbose_argument_to_parser(parser, create: bool = False):
        AddArgs.add_argument(parser, "-v", "--verbose", dest='verbose', default=False,
                            action="store_true",
                            metavar='Verbose',
                            help="Verbose output",
                            gooey_options={'visible': AddArgs.SHOW_VERBOSE_ARG_IN_GUI})

    @staticmethod
    def add_subcommand_instructions_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_instructions_arguments_to_parser() ###")

        subparser_instructions = subparsers.add_parser(AddArgs.SUBCMD_INSTRUCTIONS,
                                                 help=AddArgs.SUBCMD_INSTRUCTIONS + ' help',
                                                 prog='Instructions',
                                                 description='Filer Instructions')
        description_text = '''
        Filer's main functionality is to store information about filesystems within its inbuilt database. 
        The user can search for filesystem entries or duplicate entries stored in it using search strings and other criteria.
        
        Terms:
        - Drive: Physical drive such as a hard disk, USB drive, SD card or DVD disc.
        - Volume: A volume is a mountable partition and associated with an independent filesystem.
        - Filesystem: A filesystem contains the file system structure and data stored on a Volume.
        - Filesystem entry: A file or directory within a filesystem.
        
        Each filesystem has a unique label and this label is used for all operations involving that filesystem. 

        All filesystem entries for a filesystem are stored in the database, including hidden entries, together with their attributes.
        
        Filer is separated into various functions that you can perform on the database: 
        - Filesystem Search
        - Filesystem Duplicates Search.
        - Add to Filesystem
        - Refresh Volume List
        - Delete Filesystem
        
        Before you can search for files, at least one filesystem needs to be added to the database.
        The process of adding a new filesystem is as follows:
        1) Refresh Volume List:
             This scans the computer for all drives and volumes and makes this information available for use.
        2) Add to Filesystem:
             This currently adds all the files from a filesystem to the database. 
             In the future it will be able to add only selected files and directories.
        3) Delete Filesystem:
             Should a mistake be made, this will allow the deletion of a filesystem from the database.

        The START BUTTON in the bottom right corner of the window is used to start the selected function.
        '''
        subparser_instructions_group = subparser_instructions.add_argument_group(
            'Filer Instructions',
            description=description_text
        )
        AddArgs.add_argument(subparser_instructions_group, "--invisible_instructions", dest='invisible_instructions', metavar='Invisible Instructions',
                             action='store_true', default=True,
                             help="Invisible checkbox", gooey_options={'visible': False})


    @staticmethod
    def add_subcommand_filesystem_search_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_file_search_arguments_to_parser() ###")

        file_categories = FileTypes.get_file_categories()
        #print(f"file_categories: {file_categories}")

        subparser_search = subparsers.add_parser(AddArgs.SUBCMD_FILE_SEARCH,
                                            help=AddArgs.SUBCMD_FILE_SEARCH+' help', prog='Filesystem Search',
                                            description='Search for filesystem entries based on search strings')
        subparser_search_group = subparser_search.add_argument_group(
            'Filesystem Search',
            description='Search for filesystem entries'
        )

        help_text = '''Search string to be found within filenames
- if search doesn't include '%' or '_' characters, then it is a fast exact case-sensitive search
- if search includes '%' or '_' characters, then it is a slower pattern match case-insensitive search
- '%' wildcard character matches any sequence of zero or more characters.
- '_' wildcard character matches exactly one character
- To find all files, use a % by itself.'''
        help_text = "Search string. Wildcards: '%' = many chars, '_' = one char."
        if AddArgs.is_std_argument_parser(subparsers):
            help_text = help_text.replace(r"%", r"%%")
        AddArgs.add_argument(subparser_search_group, "-s", "--search", dest='search', metavar='Search', default=AddArgs.SUBCMD_FILE_SEARCH_DEFAULT, help=help_text)
        AddArgs.add_argument(subparser_search_group, "-l", "--label", dest='label', metavar='Volume Label',
                             widget = 'Dropdown', nargs = '?', default = None,
                             help="Label of the drive listing")

        AddArgs.add_argument(subparser_search_group, "--type", dest='type', metavar='Entry Type',
                             widget = 'Dropdown', nargs = '?', default = AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICE, choices=AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICES,
                             help="What do you want to search for?")
        AddArgs.add_argument(subparser_search_group, "-c", "--category", dest='category', metavar='File Category (NOT IMPLEMENTED YET)',
                             choices=file_categories, nargs='?', help="Category of files to be considered. Removes Directories from results if selected.")

        AddArgs.add_argument(subparser_search_group, "--size_gt", dest='size_gt', metavar='Size >=', default = AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICE,
                             # widget = 'Dropdown', nargs = '?', choices=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICES,
                             help="Size greater than or equal to value used to limit the results.")
        AddArgs.add_argument(subparser_search_group, "--size_lt", dest='size_lt', metavar='Size <=', default = AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICE,
                             # widget = 'Dropdown', nargs = '?', choices=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICES,
                             help="Size less than or equal to value used to limit the results.")

        # Invisible GUI Argument purely for widget arrangement
        #AddArgs.add_argument(subparser_search_group, "--invisible", dest='invisible', metavar='Invisible',
        #                     action='store_true', default=True, help="Invisible checkbox", gooey_options={'visible': False})

        # ADD BACK WHEN FUNCTIONALITY IMPLEMENTED
        #if not AddArgs.is_std_argument_parser(subparsers):

        """
        subparser_results_group = subparser_search.add_argument_group(
            'Results Display Options',
            description='Search for files based on search strings'
        )
        """
        AddArgs.add_argument(subparser_search_group, "--order_by", dest='order_by', metavar='Order By',
                             widget = 'Dropdown', nargs = '?', default = AddArgs.SUBCMD_FILE_SEARCH_ORDER_DEFAULT_CHOICE, choices=AddArgs.SUBCMD_FILE_SEARCH_ORDER_CHOICES,
                             help="Use this Field to Order the results.")
        #AddArgs.add_argument(subparser_results_group, "--order_desc", dest='order_desc', metavar='\n\nOrder Descending', help="Show results in Descending Order.", default=False,
        #                    action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})
        AddArgs.add_argument(subparser_search_group, "--max_results", dest='max_results', metavar='Max Results',
                             widget = 'Dropdown', nargs = '?', default = AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE, choices=AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_CHOICES,
                             help="Max number of results to display.")

        AddArgs.add_argument(subparser_search_group, "--show_size", dest='show_size', metavar='Show Size', help="Show 'Size' in results.", default=False,
                            action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})
        AddArgs.add_argument(subparser_search_group, "--show_last_modified", dest='show_last_modified', metavar='Show Last Modified Time', help="Show 'Time Last Modified' in results.", default=False,
                            action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})

        AddArgs.add_argument(subparser_search_group, "--show_attributes", dest='show_attributes', metavar='Show Information / Attributes',
                             help="Show 'Information / Attributes' in results. " + AddArgs.SHOW_ATTRIBUTES_EXTRA_HELP, default=False,
                             action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})

        AddArgs.add_db_argument_to_parser(subparser_search_group)
        #AddArgs.add_verbose_argument_to_parser(subparser_search_group)

    @staticmethod
    def add_subcommand_filesystem_duplicates_search_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_filesystem_duplicates_arguments_to_parser() ###")

        file_categories = FileTypes.get_file_categories()
        # print(f"file_categories: {file_categories}")

        subparser_duplicates = subparsers.add_parser(AddArgs.SUBCMD_DUPLICATES_SEARCH,
                                                 help=AddArgs.SUBCMD_DUPLICATES_SEARCH + ' help',
                                                 prog='Duplicates Search',
                                                 description='Search for duplicate filesystem entries based on search strings')
        subparser_search_group = subparser_duplicates.add_argument_group(
            'Duplicates Search',
            description="Search for duplicate filesystem entries where the their names and sizes match."
        )

        help_text = '''Search string to be found within filenames
        - if search doesn't include '%' or '_' characters, then it is a fast exact case-sensitive search
        - if search includes '%' or '_' characters, then it is a slower pattern match case-insensitive search
        - '%' wildcard character matches any sequence of zero or more characters.
        - '_' wildcard character matches exactly one character
        - To find all files, use a % by itself.'''
        help_text = "Search string. Wildcards: '%' = many chars, '_' = one char."
        if AddArgs.is_std_argument_parser(subparsers):
            help_text = help_text.replace(r"%", r"%%")
        AddArgs.add_argument(subparser_search_group, "-s", "--search", dest='search', metavar='Search',
                             default=AddArgs.SUBCMD_FILE_SEARCH_DEFAULT, help=help_text)
        AddArgs.add_argument(subparser_search_group, "-l", "--label", dest='label', metavar='Volume Label',
                             widget='Dropdown', nargs='?', default=None,
                             help="Label of the drive listing")

        AddArgs.add_argument(subparser_search_group, "--type", dest='type', metavar='Entry Type',
                             widget='Dropdown', nargs='?', default=AddArgs.SUBCMD_DUPLICATES_SEARCH_SEARCH_FOR_CHOICE,
                             choices=AddArgs.SUBCMD_FILE_SEARCH_SEARCH_FOR_CHOICES,
                             help="What do you want to search for?")
        AddArgs.add_argument(subparser_search_group, "-c", "--category", dest='category',
                             metavar='File Category (NOT IMPLEMENTED YET)',
                             choices=file_categories, nargs='?',
                             help="Category of files to be considered. Removes Directories from results if selected.")

        AddArgs.add_argument(subparser_search_group, "--size_gt", dest='size_gt', metavar='Size >=',
                             default=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICE,
                             # widget = 'Dropdown', nargs = '?', choices=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICES,
                             help="Size greater than or equal to value used to limit the results.")
        AddArgs.add_argument(subparser_search_group, "--size_lt", dest='size_lt', metavar='Size <=',
                             default=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICE,
                             # widget = 'Dropdown', nargs = '?', choices=AddArgs.SUBCMD_FILE_SEARCH_SIZE_CHOICES,
                             help="Size less than or equal to value used to limit the results.")

        # Invisible GUI Argument purely for widget arrangement
        # AddArgs.add_argument(subparser_search_group, "--invisible", dest='invisible', metavar='Invisible',
        #                     action='store_true', default=True, help="Invisible checkbox", gooey_options={'visible': False})

        # ADD BACK WHEN FUNCTIONALITY IMPLEMENTED
        # if not AddArgs.is_std_argument_parser(subparsers):

        """
        subparser_results_group = subparser_search.add_argument_group(
            'Results Display Options',
            description='Search for files based on search strings'
        )
        """
        AddArgs.add_argument(subparser_search_group, "--order_by", dest='order_by', metavar='Order By',
                             widget='Dropdown', nargs='?', default=AddArgs.SUBCMD_DUPLICATES_SEARCH_ORDER_DEFAULT_CHOICE,
                             choices=AddArgs.SUBCMD_DUPLICATES_SEARCH_ORDER_CHOICES,
                             help="Use this Field to Order the results.")
        # AddArgs.add_argument(subparser_results_group, "--order_desc", dest='order_desc', metavar='\n\nOrder Descending', help="Show results in Descending Order.", default=False,
        #                    action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})
        AddArgs.add_argument(subparser_search_group, "--max_results", dest='max_results', metavar='Max Results',
                             widget='Dropdown', nargs='?',
                             default=AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_DEFAULT_CHOICE,
                             choices=AddArgs.SUBCMD_FILE_SEARCH_MAX_RESULTS_CHOICES,
                             help="Max number of results to display.")
        """
        AddArgs.add_argument(subparser_search_group, "--show_size", dest='show_size', metavar='Show Size',
                             help="Show 'Size' in results.", default=False,
                             action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})
        AddArgs.add_argument(subparser_search_group, "--show_last_modified", dest='show_last_modified',
                             metavar='Show Last Modified Time', help="Show 'Time Last Modified' in results.",
                             default=False,
                             action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})

        AddArgs.add_argument(subparser_search_group, "--show_attributes", dest='show_attributes',
                             metavar='Show Information / Attributes',
                             help="Show 'Information / Attributes' in results. " + AddArgs.SHOW_ATTRIBUTES_EXTRA_HELP,
                             default=False,
                             action="store_true", gooey_options={'visible': AddArgs.SHOW_FILE_SEARCH_ARG_IN_GUI})
        """
        AddArgs.add_db_argument_to_parser(subparser_search_group)
        # AddArgs.add_verbose_argument_to_parser(subparser_search_group)

    @staticmethod
    def add_subcommand_filesystem_calc_dir_sizes_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_filesystem_calc_dir_sizes_arguments_to_parser() ###")

        subparser_calc_dir_sizes = subparsers.add_parser(AddArgs.SUBCMD_CALC_DIR_SIZES,
                                                 help=AddArgs.SUBCMD_CALC_DIR_SIZES + ' help',
                                                 prog='Calculate Directory Sizes',
                                                 description='Calculate directory sizes based on filesystem entries')
        subparser_calc_dir_sizes_group = subparser_calc_dir_sizes.add_argument_group(
            'Calculate Directory Sizes',
            description="Calculate directory sizes based on filesystem entries."
        )

        AddArgs.add_argument(subparser_calc_dir_sizes_group, "-l", "--label", dest='label', metavar='Volume Label',
                             widget='Dropdown', nargs='?', default=None,
                             help="Label of the drive listing to calculate directory sizes for.")

    @staticmethod
    def add_subcommand_add_volume_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_add_volume_arguments_to_parser() ###")
        if not AddArgs.is_std_argument_parser(subparsers):
            # create the parser for the "add" subcommand
            subparser_add_volume = subparsers.add_parser(AddArgs.SUBCMD_ADD_VOLUME, help=AddArgs.SUBCMD_ADD_VOLUME+' help', prog='Add to Filesystem', description='Add Filesystem Entries to a Filesystem in the Database')

            subparser_add_volume_group = subparser_add_volume.add_argument_group(
                'Add to Filesystem',
                description='Add Filesystem Entries: Files, Directories (and the files within them), or a Volume (and the directories and files within it) to a Filesystem in the database.'
            )

            AddArgs.add_argument(subparser_add_volume_group, "--vol_label", dest='vol_label', metavar='Label',
                                #default=AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT,
                                const='all', nargs = '?', # choices=[AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT],
                                help="For a new Filesystem, either enter your custom name here or the selected Volume's Filesystem Name will be used instead.\n"
                                     "To Add Entries to an existing Filesystem, select an existing Label.",
                                widget = 'Dropdown' #, gooey_options={ 'initial_value': AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT }
                           )
            AddArgs.add_argument(subparser_add_volume_group, "--invisible4", dest='invisible4', metavar='Invisible4',
                                 action='store_true', default=True, help="Invisible checkbox",
                                 gooey_options={'visible': False})

            help_text = f'''Volume from which you wish to add Filesystem Entries. If you don't use the options to add directories or files, then the Whole Volume's contents will be added to the filesystem, or replaced if the volume already exists. - If you don't see your volume, please use the {AddArgs.get_message_based_on_parser(subparsers, "'"+AddArgs.SUBCMD_REFRESH_VOLUMES+"' subcommand", "'Refresh Volumes List' action.")}'''
# - Values last updated: {self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CREATED]}
            if AddArgs.is_std_argument_parser(subparsers):
                help_text = help_text.replace(r"%", r"%%")
            AddArgs.add_argument(subparser_add_volume_group, "--volume", dest='volume', metavar='Volume',
                                 widget='Dropdown', nargs='?', default=None, help=help_text)
            # Invisible GUI Argument purely for widget arrangement
            AddArgs.add_argument(subparser_add_volume_group, "--invisible", dest='invisible', metavar='Invisible',
                                 action='store_true', default=True, help="Invisible checkbox",
                                 gooey_options={'visible': False})

            AddArgs.add_argument(subparser_add_volume_group, "--dir", dest='dir', default=None,
                           widget='MultiDirChooser',
                           metavar='Directories to Add (Not Implemented Yet)',
                           help="Add Directories (and their contents). The dialog box takes a while to open depending on the number of directories on your system. Don't click the button more than once !!!",
                           #gooey_options={'visible': AddArgs.SHOW_DB_FILENAME_ARG_IN_GUI}
                                 )
            # Invisible GUI Argument purely for widget arrangement
            AddArgs.add_argument(subparser_add_volume_group, "--invisible2", dest='invisible2', metavar='Invisible2',
                                 action='store_true', default=True, help="Invisible checkbox",
                                 gooey_options={'visible': False})

            AddArgs.add_argument(subparser_add_volume_group, "--files", dest='files', default=None,
                           widget='MultiFileChooser',
                           metavar='Files to Add (Not Implemented Yet)',
                           help="Add Files to Filesystem Label",
                           #gooey_options={'visible': AddArgs.SHOW_DB_FILENAME_ARG_IN_GUI}
                                 )
            # Invisible GUI Argument purely for widget arrangement
            AddArgs.add_argument(subparser_add_volume_group, "--invisible3", dest='invisible3', metavar='Invisible3',
                                 action='store_true', default=True, help="Invisible checkbox",
                                 gooey_options={'visible': False})

            hostname = socket.gethostname()
            AddArgs.add_argument(subparser_add_volume_group, "-n", "--hostname", dest='hostname', metavar='Hostname', default=hostname,
                                          help="Hostname of the machine containing the drive")
            AddArgs.add_argument(subparser_add_volume_group, "--invisible5", dest='invisible5', metavar='Invisible5',
                                 action='store_true', default=True, help="Invisible checkbox",
                                 gooey_options={'visible': False})

            AddArgs.add_argument(subparser_add_volume_group, "--confirm", dest='confirm', default=False,
                                 action="store_true",
                                 metavar='Confirm',
                                 help="CONFIRM: Replace Entries for this Filesystem if they already exist." )
            AddArgs.add_db_argument_to_parser(subparser_add_volume_group)
            AddArgs.add_verbose_argument_to_parser(subparser_add_volume_group)

    @staticmethod
    def add_subcommand_delete_volume_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_delete_volume_arguments_to_parser() ###")
        if not AddArgs.is_std_argument_parser(subparsers):
            subparser_delete_volume = subparsers.add_parser(AddArgs.SUBCMD_DELETE_VOLUME,
                                                         help=AddArgs.SUBCMD_DELETE_VOLUME + ' help',
                                                         prog='Delete Filesystem',
                                                         description='Delete Filesystem from the Database')
            subparser_delete_volume_group = subparser_delete_volume.add_argument_group(
                'Delete Filesystem',
                description='Delete Filesystem from the Database'
            )
            AddArgs.add_argument(subparser_delete_volume_group, "--vol_label", dest='vol_label',
                                 metavar='Label',
                                 # default=AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT,
                                 const='all', nargs='?',  # choices=[AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT],
                                 help="Label of the Filesystem that you wish to delete.",
                                 widget='Dropdown'
                                 # , gooey_options={ 'initial_value': AddArgs.SUBCMD_ADD_VOLUME_VOL_LABEL_DEFAULT                                                                      }
                                 )

            AddArgs.add_argument(subparser_delete_volume_group, "--invisible2", dest='invisible2',
                                 metavar='Invisible2',
                                 action='store_true', default=True, help="Invisible2 checkbox",
                                 gooey_options={'visible': False})
            AddArgs.add_argument(subparser_delete_volume_group, "--confirm", dest='confirm', default=False,
                                 action="store_true",
                                 metavar='Confirm',
                                 help="CONFIRM: Removal of this Label's filesystem from the database." )
            AddArgs.add_db_argument_to_parser(subparser_delete_volume_group)
            AddArgs.add_verbose_argument_to_parser(subparser_delete_volume_group)

    @staticmethod
    def add_subcommand_refresh_volumes_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_refresh_volumes_arguments_to_parser() ###")
        if not AddArgs.is_std_argument_parser(subparsers):
            # create the parser for the "add" subcommand
            subparser_refresh_volumes = subparsers.add_parser(AddArgs.SUBCMD_REFRESH_VOLUMES, help=AddArgs.SUBCMD_REFRESH_VOLUMES+' help', prog='Refresh Volumes List', description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.')
            subparser_refresh_volumes_group = subparser_refresh_volumes.add_argument_group(
                'Refresh Volumes List',
                description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.'
            )
            AddArgs.add_argument(subparser_refresh_volumes_group, "--invisible", dest='invisible', metavar='Invisible',
                           action='store_true', default=True,
                           help="Invisible checkbox", gooey_options = {'visible': False})

    @staticmethod
    def add_subcommand_create_database_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_create_database_arguments_to_parser() ###")
        subparser_create_database = subparsers.add_parser(AddArgs.SUBCMD_CREATE_DATABASE,
                                              help=AddArgs.SUBCMD_CREATE_DATABASE+' help', prog='Create Database',
                                              description='Create a new database')
        subparser_create_database_group = subparser_create_database.add_argument_group(
            'Create Database',
            description='Create a new database.'
        )
        AddArgs.add_db_argument_to_parser(subparser_create_database_group, True)
        #AddArgs.add_verbose_argument_to_parser(subparser_create_database_group)

    @staticmethod
    def add_subcommand_select_database_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_select_database_arguments_to_parser() ###")
        subparser_select_database = subparsers.add_parser(AddArgs.SUBCMD_SELECT_DATABASE,
                                              help=AddArgs.SUBCMD_SELECT_DATABASE+' help', prog='Select Database',
                                              description='Select the database you wish to use, including the path to the database file.')
        subparser_select_database_group = subparser_select_database.add_argument_group(
            'Select Database',
            description='Select the database you wish to use, including the path to the database file.'
        )
        AddArgs.add_argument(subparser_select_database_group, "db", default=AddArgs.DEFAULT_DATABASE_FILENAME,
                       widget='FileChooser',
                       metavar='Database Filename',
                       help="Database filename (including the path if not in the current directory). Default='database.sqlite' in the current directory.")
        #AddArgs.add_db_argument_to_parser(subparser_select_database_group, False)
        #AddArgs.add_verbose_argument_to_parser(subparser_create_database_group)
