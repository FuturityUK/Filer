import argparse
import logging
import socket
from file_types import FileTypes
#from f import F

class AddArgs:

    SHOW_DB_FILENAME_ARG_IN_GUI: bool = False
    SHOW_VERBOSE_ARG_IN_GUI: bool = False

    SUBCMD_FILE_SEARCH: str = 'file_search'
    SUBCMD_REFRESH_VOLUMES: str = 'refresh_volumes'
    SUBCMD_ADD_VOLUME: str = 'add_volume'
    SUBCMD_IMPORT_VOLUME: str = 'import_volume'
    SUBCMD_CREATE_DATABASE: str = 'create_db'
    SUBCMD_SELECT_DATABASE: str = 'select_db'
    SUBCMD_UPGRADE_DATABASE: str = 'upgrade_db'
    SUBCMD_VACUUM_DATABASE: str = 'vacuum_db'
    SUBCMD_RESET_DATABASE: str = 'reset_db'

    SUBCMD_FILE_SEARCH_LABEL_ALL_LABELS: str = ' '
    SUBCMD_FILE_SEARCH_RESULTS_DEFAULT_CHOICE: str = '100'
    SUBCMD_FILE_SEARCH_RESULTS_CHOICES: list = ['100', '250', '500', '1000', '10000', '100000']

    DEFAULT_DATABASE_FILENAME: str = 'AddArgs.DEFAULT_DATABASE_FILENAME'

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
        AddArgs.add_subcommand_file_search_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_add_volume_arguments_to_parser(subparsers)
        AddArgs.add_subcommand_refresh_volumes_arguments_to_parser(subparsers)
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
        AddArgs.add_argument(parser_import, "-c", "--combined", dest='combined', metavar='Combined',
                                   help="Combined drive information string, in format \"make,model,serial-number\"")
        AddArgs.add_argument(parser_import, "-n", "--hostname", dest='hostname', metavar='Hostname',
                                   help="Hostname of the machine containing the drive")
        AddArgs.add_argument(parser_import, "-p", "--prefix", dest='prefix', metavar='Prefix',
                                   help="Prefix to remove from the start of each file's path. e.g. \"C:\\Users\\username\"")
        AddArgs.add_argument(parser_import, "-t", "--test", dest='test', metavar='Test', action="store_true",
                                   help="Test input file without modifying the database")
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
    def add_subcommand_file_search_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_file_search_arguments_to_parser() ###")

        file_categories = FileTypes.get_file_categories()
        #print(f"file_categories: {file_categories}")

        subparser_search = subparsers.add_parser(AddArgs.SUBCMD_FILE_SEARCH,
                                            help=AddArgs.SUBCMD_FILE_SEARCH+' help', prog='File Search',
                                            description='Search for files based on search strings')
        subparser_search_group = subparser_search.add_argument_group(
            'Search for files',
            description='Search for files based on search strings'
        )
        help_text = '''Search string to be found within filenames
- if search doesn't include '%' or '_' characters, then it is a fast exact case-sensitive search
- if search includes '%' or '_' characters, then it is a slower pattern match case-insensitive search
- '%' wildcard character matches any sequence of zero or more characters.
- '_' wildcard character matches exactly one character
- To find all files, use a % by itself.'''
        if AddArgs.is_std_argument_parser(subparsers):
            help_text = help_text.replace(r"%", r"%%")
        AddArgs.add_argument(subparser_search_group, "-s", "--search", metavar='Search', default="%", help=help_text)
        # ADD BACK WHEN FUNCTIONALITY IMPLEMENTED
        #if not AddArgs.is_std_argument_parser(subparsers):
        #    AddArgs.add_argument(subparser_search_group, "-c", "--category", dest='category', metavar='Category', choices=file_categories, nargs='?', help="Category of files to be considered")
        AddArgs.add_argument(subparser_search_group, "-l", "--label", dest='label', metavar='Label',
                             widget = 'Dropdown', const='all', nargs = '?', default = None,
                             help="Label of the drive listing")
        AddArgs.add_argument(subparser_search_group, dest='results', metavar='Results',
                             widget = 'Dropdown', const='all', nargs = '?', default = AddArgs.SUBCMD_FILE_SEARCH_RESULTS_DEFAULT_CHOICE, choices=AddArgs.SUBCMD_FILE_SEARCH_RESULTS_CHOICES,
                             help="Max number of results to display.")
        AddArgs.add_db_argument_to_parser(subparser_search_group)
        #AddArgs.add_verbose_argument_to_parser(subparser_search_group)

    @staticmethod
    def add_subcommand_add_volume_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_add_volume_arguments_to_parser() ###")
        # Only add the 'add' subcommand to the GUI
        if not AddArgs.is_std_argument_parser(subparsers):
            # create the parser for the "add" subcommand
            subparser_add_volume = subparsers.add_parser(AddArgs.SUBCMD_ADD_VOLUME, help=AddArgs.SUBCMD_ADD_VOLUME+' help', prog='Add Volume Files', description='Add Files on a selected Volume to the Database')
            subparser_add_volume_group = subparser_add_volume.add_argument_group(
                'Add Volume Files to Database',
                description='Add Files on a selected Volume to the Database'
            )
            help_text = f'''Volume that you wish to add.
- If you don't see your volume, please use the {AddArgs.get_message_based_on_parser(subparsers, "'"+AddArgs.SUBCMD_REFRESH_VOLUMES+"' subcommand", "'Refresh Volumes List' action.")}'''
# - Values last updated: {self.configuration[self.CONFIG_VOL_DETAILS][self.VOL_ARG_DETAILS_CREATED]}

            if AddArgs.is_std_argument_parser(subparsers):
                help_text = help_text.replace(r"%", r"%%")
            AddArgs.add_argument(subparser_add_volume_group, "--volume", dest='volume', metavar='Volume',
                                 widget='Dropdown', nargs='?', default=None, help=help_text)
            #AddArgs.add_argument(subparser_add_volume_group, "-l", "--label", dest='label', metavar='Label', default=None, help="Label of the drive listing. If provided it will override the volume label.",
            AddArgs.add_argument(subparser_add_volume_group, "--label", dest='label', metavar='Label',
                                          widget = 'Dropdown', nargs = '?', default = None,
                                          help="Label of the drive listing. If left blank, the volume's label will be used instead.'"
                                          # gooey_options={ 'initial_value': "" }
                           )
            hostname = socket.gethostname()
            AddArgs.add_argument(subparser_add_volume_group, "-n", "--hostname", dest='hostname', metavar='Hostname', default=hostname,
                                          help="Hostname of the machine containing the drive")
            AddArgs.add_argument(subparser_add_volume_group, "-r", "--remove", dest='remove', default=False,
                                 action="store_true",
                                 metavar='Remove',
                                 help="WARNING: Remove this Label's old files before adding this volume's files.")
            AddArgs.add_db_argument_to_parser(subparser_add_volume_group)
            AddArgs.add_verbose_argument_to_parser(subparser_add_volume_group)

    @staticmethod
    def add_subcommand_refresh_volumes_arguments_to_parser(subparsers):
        logging.debug(f"### AddArgs.add_subcommand_refresh_volumes_arguments_to_parser() ###")
        # Only add the 'add' subcommand to the GUI
        if not AddArgs.is_std_argument_parser(subparsers):
            # create the parser for the "add" subcommand
            subparser_refresh_volumes = subparsers.add_parser(AddArgs.SUBCMD_REFRESH_VOLUMES, help=AddArgs.SUBCMD_REFRESH_VOLUMES+' help', prog='Refresh Volumes List', description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.')
            subparser_refresh_volumes_group = subparser_refresh_volumes.add_argument_group(
                'Refresh Volumes List',
                description='Refresh the List of Volumes that appear on the "Add_Volumes" action page.'
            )
            AddArgs.add_argument(subparser_refresh_volumes_group, "-i", "--invisible", dest='invisible', metavar='Invisible',
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
