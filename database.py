import sqlite3
import traceback
import sys
import logging
from typing import (
    Iterable,
    Union,
    Optional,
)
from sql import SQLDictionary
from add_args import AddArgs

class Database:
    """ Class to handle SQlite operations """
    __verbose = False

    ENTRY_TYPE_FILES: int = 0
    ENTRY_TYPE_DIRECTORIES: int = 1
    SET_TRACE_CALLBACK = True

    def __init__(self, path: str):
        logging.debug(f"### Database.__init__() ###")
        self.__connection = self.create_connection(path)
        self.__cursor = self.create_cursor()
        self.__sql_dictionary = SQLDictionary().sql_dictionary
        self.__sql_versions = SQLDictionary().sql_versions
        self.__dry_run_mode = False
        self.set_verbose_mode(False)
        return

    def set_test(self, test: bool):
        logging.debug(f"### Database.set_test() ###")
        self.__dry_run_mode = test

    def set_verbose_mode(self, verbose: bool):
        logging.debug(f"### Database.set_verbose_mode(verbose: {verbose}) ###")
        self.__verbose = verbose
        if self.__verbose:
            self.__connection.set_trace_callback(print)
        else:
            self.__connection.set_trace_callback(None)

    def close_database(self):
        logging.debug(f"### Database.close_database() ###")
        self.commit()
        self.close_cursor()
        self.close_connection()

    def create_connection(self, path: str):
        logging.debug(f"### Database.create_connection(path: {path}) ###")
        self.__connection = None
        try:
            sqlite3.enable_callback_tracebacks(True)
            # database_path_string = 'file:'+path+'?mode=rw'
            # logging.debug(f"database_path_string: {database_path_string}")
            self.__connection = sqlite3.connect(path)
            # if os.path.isfile(path):
            if self.__connection is not None:
                logging.debug("Connection to SQLite DB successful")
            else:
                logging.debug("Connection to SQLite DB failed")
                raise sqlite3.OperationalError("Connection to SQLite DB failed")
            self.__connection.set_trace_callback(print)
        except sqlite3.OperationalError as e:
            print(f"sqlite3.OperationalError: '{e}'")
            exit(2)  # Exit with system code 2 to indicate and error
        except Exception as e:
            print(f"Exception: '{e}'")
            exit(2)  # Exit with system code 2 to indicate and error
        return self.__connection

    def close_connection(self):
        logging.debug(f"### Database.close_connection() ###")
        self.__connection.close()

    def create_cursor(self):
        logging.debug(f"### Database.create_cursor() ###")
        self.__cursor = self.__connection.cursor()
        return self.__cursor

    def close_cursor(self):
        logging.debug(f"### Database.close_cursor() ###")
        self.__cursor.close()

    # Decorator function
    """
    def my_decorator(self, original_function):
        def wrapper(*args, **kwargs):
            if not self.__dry_run_mode:
                logging.debug(f"Calling {self.__cursor.execute.__name__} with args: {args}, kwargs: {kwargs}")
                # Call the original function
                result = original_function(*args, **kwargs)
                # Log the return value
                logging.debug(f"{original_function.__name__} returned: {result}")
                # Return the result
                return result
        return wrapper

    @my_decorator
    def execute(self, ):
    """

    def execute(self,
                sql: str,
                parameters: Optional[Union[Iterable, dict]] = None
                ):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.

        :param sql: SQL statement to execute
        :param parameters: Parameters to use in that statement - an iterable for ``where id = ?``
          parameters, or a dictionary for ``where id = :id``
        """
        logging.debug(f"### Database.execute() ###")
        logging.debug(f"- sql: {sql}")
        logging.debug(f"- parameters: {parameters}")
        try:
            if parameters is not None:
                return self.__cursor.execute(sql, parameters)
            else:
                return self.__cursor.execute(sql)
        except sqlite3.Error as err:
            """
            # print(f"Error in SQL execute: {err.sqlite_errorname}")
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            #print("Exiting.")
            #exit(2)
            """
            return err

    def executescript(self, sql: str):
        """
        Execute SQL statement and return a ``sqlite3.Cursor``.
        :param sql: SQL statement to execute
        """
        logging.debug(f"### Database.executescript() ###")
        logging.debug(f"- sql: {sql}")
        try:
            return self.__cursor.executescript(sql)
        except sqlite3.Error as err:
            """
            print(f"Error in SQL executescript: {err.sqlite_errorname}")
            print('SQLite traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
            #print("Exiting.")
            #exit(2)
            """
            return err

    def commit(self):
        if not self.__dry_run_mode:
            # Commit changes to the database
            self.__connection.commit()

    def get_last_row_id(self):
        # Provides the row id of the last inserted row
        # Not that for other statements, after executemany() or executescript(), or if the insertion failed,
        # the value of lastrowid is left unchanged. Therefore, always check and handle insert errors.
        # The initial value of lastrowid is None.
        if self.__dry_run_mode:
            return None
        else:
            return self.__cursor.lastrowid

    def rows_affected(self):
        return self.__cursor.rowcount

    def fetch_all_results(self):
        if self.__dry_run_mode:
            return None
        else:
            return self.__cursor.fetchall()

    def vacuum(self):
        # Shrink to database to reclaim unused space in the database file as well fix defragmentation.
        self.__connection.isolation_level = None
        self.execute("VACUUM")
        self.__connection.isolation_level = ''  # <- note that this is the default value of isolation_level
        # self.database_connection.commit()
        self.commit()

    def create_database_structure(self):
        logging.info(f"Creating database.")
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["create_database_tables_and_indexes"]}\"")
        self.executescript(self.__sql_dictionary["create_database_tables_and_indexes"])
        self.commit()
        print(f"Database created.")

    def upgrade_database(self):
        db_version = 0
        last_db_version = 0
        while True:
            # Loop until all upgrades have been applied
            '''
            logging.debug(f"SQL Query: \"{self.__sql_dictionary["does_database_information_table_exist"]}\"")
            self.execute(self.__sql_dictionary["does_database_information_table_exist"])
            rows_found = 0
            select_result = self.fetch_all_results()
            for row in select_result:
                #logging.debug(f"{row[0]}")
                rows_found += 1
            logging.debug(f"{rows_found} results found")
            if rows_found == 0:
                # DatabaseVersion table doesn't exist, so this must be the initial version 1 database
                db_version = 1
            else:
            '''
            # DatabaseVersion table does exist, so load the version of the database
            #logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_db_version"]}\"")
            result = self.execute(self.__sql_dictionary["find_db_version"])
            #logging.debug(f"type(result): {type(result)}")
            if type(result) is sqlite3.OperationalError:
                print("DatabaseInformation table doesn't exist, so this must be database version 1")
                db_version = 1
            else:
                rows_found = 0
                select_result = self.fetch_all_results()
                for row in select_result:
                    db_version = int(row[0])
                    #logging.debug(f"db_version: {db_version}")
                    rows_found += 1
                #logging.debug(f"{rows_found} results found")

                if rows_found == 0:
                    # DBVersion not found
                    print("DBVersion not found in the DatabaseInformation table")
                    exit(2)
                elif rows_found > 1:
                    # More than one DBVersion found
                    print("More than one DBVersion found in the DatabaseInformation table. Can't continue.")
                    exit(2)
            # If we are here, then db_version have been loaded correctly

            sql_versions_length = len(self.__sql_versions)
            if db_version >= sql_versions_length:
                # Database is up to date
                #print(f"Database version {db_version} is the latest version. No upgrade needed.")
                break
            else:
                print(f"Database version {db_version} detected.")
                # Database needs upgrading
                new_db_version = db_version + 1
                if last_db_version >= new_db_version:
                    print("We seem to be caught in an update loop. Can't continue.")
                    exit(2)
                if str(new_db_version) not in self.__sql_versions:
                    print(f"No dictionary key found for upgrade version {new_db_version}")
                    exit(2)
                else:
                    sql_dictionary_key = self.__sql_versions[str(new_db_version)]
                    if sql_dictionary_key not in self.__sql_dictionary:
                        print(f"No upgrade SQL found for dictionary key {sql_dictionary_key} in the SQL dictionary")
                        exit(2)
                    else:
                        upgrade_sql = self.__sql_dictionary[sql_dictionary_key]
                        print(f"Upgrading database to version {new_db_version}.")
                        logging.debug(f"SQL Query: \"{upgrade_sql}\"")
                        result = self.executescript(upgrade_sql)
                        if type(result) is sqlite3.OperationalError:
                            print(f"Error executing SQL upgrade to version {new_db_version}: {result}")
                            exit(2)
                        else:
                            self.commit()
                            print(f"Database upgraded to version {new_db_version} complete.")
                            last_db_version = new_db_version
        self.commit()

    """
    def find_filenames_exact_match(self, filename: str, file_type: str, label: str = None, max_results: int = None, order_by: str = None, order_desc: bool = False):

        if label is None:
            self.find_filenames(
                self.__sql_dictionary["find_filename_exact_match"],
                [filename]
            )
        else:
            self.find_filenames(
                self.__sql_dictionary["find_filename_exact_match_with_label"],
                [filename, label]
            )
        return self.filesystem_search(filename, file_type, label, max_results, order_by, order_desc, False)
    """

    def create_entry_search_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, entry_search: str, like: bool):
        if entry_search is not None:
            if entry_search.count("%") == 0 and entry_search.count("_") == 0:
                # We can replace this SQL "like" with an exact match '=' as it doesn't contain "like" special characters
                like = False
            # Filename clause
            if like:
                sql_string += " " + self.__sql_dictionary["find_filename_like_filename_clause"]
                if entry_search is not None and entry_search != "":
                    sql_argument_array.append(entry_search)
                else:
                    sql_argument_array.append("%")
            else:
                sql_string += " " + self.__sql_dictionary["find_filename_exact_match_filename_clause"]
                if entry_search is not None and entry_search != "":
                    sql_argument_array.append(entry_search)
                else:
                    print("Filename can't be empty for an exact match search")
                    exit()
            clause_added = True
        return sql_string, sql_argument_array, clause_added

    def create_volume_label_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, volume_label: str):
        # Label clause
        if volume_label is not None and volume_label != "" :
            print(f'volume_label: "{volume_label}"')
            if clause_added:
                sql_string += " AND "
            sql_string += self.__sql_dictionary["find_filename_label_clause"]
            sql_argument_array.append(volume_label)
            clause_added = True
        return sql_string, sql_argument_array, clause_added

    def create_entry_type_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, entry_type: int):
        # Entry type clause
        if entry_type is not None and (entry_type == self.ENTRY_TYPE_FILES or entry_type == self.ENTRY_TYPE_DIRECTORIES):
            if clause_added:
                sql_string += " AND "
            sql_string += self.__sql_dictionary["find_filename_directory_clause"]
            sql_argument_array.append(entry_type)
            clause_added = True
        return sql_string, sql_argument_array, clause_added

    def create_gt_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, entry_size_gt: int):
        # >= clause
        if entry_size_gt is not None:
            if clause_added:
                sql_string += " AND "
            sql_string += self.__sql_dictionary["find_filename_ByteSize_greater_than_equal_to_clause"]
            sql_argument_array.append(entry_size_gt)
            clause_added = True
        return sql_string, sql_argument_array, clause_added

    def create_lt_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, entry_size_lt: int):
        # <= clause
        if entry_size_lt is not None:
            if clause_added:
                sql_string += " AND "
            sql_string += self.__sql_dictionary["find_filename_ByteSize_less_than_equal_to_clause"]
            sql_argument_array.append(entry_size_lt)
            clause_added = True
        return sql_string, sql_argument_array, clause_added

    def create_join_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool):
        # Add table join
        if clause_added:
            sql_string += " AND "
        sql_string += " " + self.__sql_dictionary["find_filename_join"]
        return sql_string, sql_argument_array, clause_added

    def create_order_by_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, order_by: str):
        # Order By
        if order_by is not None:
            if order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_ASCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_full_path"]
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_FULL_PATH_DESCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_full_path"] + " DESC "
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_FILENAME_ASCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_entry_name"]
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_FILENAME_DESCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_entry_name"] + " DESC "
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_SIZE_ASCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_size"]
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_SIZE_DESCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_size"] + " DESC "
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_ASCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_last_modified"]
            elif order_by == AddArgs.SUBCMD_FILE_SEARCH_ORDER_LAST_MODIFIED_DESCENDING: sql_string += " " + self.__sql_dictionary["find_filename_order_by_last_modified"] + " DESC "
            elif order_by == AddArgs.SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_ASCENDING: sql_string += " " + self.__sql_dictionary["find_duplicates_order_by_duplicates"]
            elif order_by == AddArgs.SUBCMD_DUPLICATES_SEARCH_ORDER_DUPLICATES_DESCENDING: sql_string += " " + self.__sql_dictionary["find_duplicates_order_by_duplicates"] + " DESC "
        return sql_string, sql_argument_array, clause_added

    def create_limit_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool, max_results: int):
        # Limit results clause
        if max_results is not None:
            sql_string += self.__sql_dictionary["find_filename_limit_clause"]
            sql_argument_array.append(max_results)
        return sql_string, sql_argument_array, clause_added

    @staticmethod
    def create_close_sql_string(sql_string: str, sql_argument_array: list, clause_added: bool):
        sql_string += ";"
        return sql_string, sql_argument_array, clause_added

    def create_group_by_sql_string(self, sql_string: str, sql_argument_array: list, clause_added: bool):
        # Add table join
        # Note: AND not needed before GROUP BY
        sql_string += " " + self.__sql_dictionary["find_duplicates_group_by"]
        return sql_string, sql_argument_array, clause_added

    def run_find_sql(self, sql_string: str, sql_argument_array: list = None):
        # Run the SQL
        logging.debug(f"sql_string: {sql_string}")
        logging.debug(f"sql_argument_array: {sql_argument_array}")
        return self.find_filenames( sql_string, sql_argument_array )

    def filesystem_shared_code(self, sql_string, sql_argument_array, clause_added, entry_search: str = None, volume_label: str = None, entry_type: int = None, entry_size_gt: int = None, entry_size_lt: int = None, like: bool = True):
        sql_string, sql_argument_array, clause_added = self.create_entry_search_sql_string(sql_string, sql_argument_array, clause_added, entry_search, like)
        sql_string, sql_argument_array, clause_added = self.create_volume_label_sql_string(sql_string, sql_argument_array, clause_added, volume_label)
        sql_string, sql_argument_array, clause_added = self.create_entry_type_sql_string(sql_string, sql_argument_array, clause_added, entry_type)
        sql_string, sql_argument_array, clause_added = self.create_gt_sql_string(sql_string, sql_argument_array, clause_added, entry_size_gt)
        sql_string, sql_argument_array, clause_added = self.create_lt_sql_string(sql_string, sql_argument_array, clause_added, entry_size_lt)
        return sql_string, sql_argument_array, clause_added

    def filesystem_shared_code2(self, sql_string, sql_argument_array, clause_added, order_by: str = None, max_results: int = 100):
        sql_string, sql_argument_array, clause_added = self.create_order_by_sql_string(sql_string, sql_argument_array, clause_added, order_by)
        sql_string, sql_argument_array, clause_added = self.create_limit_sql_string(sql_string, sql_argument_array, clause_added, max_results)
        sql_string, sql_argument_array, clause_added = self.create_close_sql_string(sql_string, sql_argument_array, clause_added)
        return self.run_find_sql( sql_string, sql_argument_array )

    def filesystem_duplicates_search(self, entry_search: str = None, volume_label: str = None, entry_type: int = None, entry_category: str = None, entry_size_gt: int = None, entry_size_lt: int = None, order_by: str = None, max_results: int = 100, like: bool = True):
        # If entry_type is None: Any, 1: Directory, 0: Non-Directory
        sql_string = self.__sql_dictionary["find_duplicates_base"]
        sql_argument_array = []
        clause_added = False
        sql_string, sql_argument_array, clause_added = self.filesystem_shared_code(sql_string, sql_argument_array, clause_added, entry_search, volume_label, entry_type, entry_size_gt, entry_size_lt, like)
        sql_string, sql_argument_array, clause_added = self.create_group_by_sql_string(sql_string, sql_argument_array, clause_added)
        return self.filesystem_shared_code2(sql_string, sql_argument_array, clause_added, order_by, max_results)

    def filesystem_search(self, entry_search: str = None, volume_label: str = None, entry_type: int = None, entry_category: str = None, entry_size_gt: int = None, entry_size_lt: int = None, order_by: str = None, max_results: int = 100, like: bool = True):
        # If entry_type is None: Any, 1: Directory, 0: Non-Directory
        sql_string = self.__sql_dictionary["find_filename_base"]
        sql_argument_array = []
        clause_added = False
        sql_string, sql_argument_array, clause_added = self.filesystem_shared_code(sql_string, sql_argument_array, clause_added, entry_search, volume_label, entry_type, entry_size_gt, entry_size_lt, like)
        sql_string, sql_argument_array, clause_added = self.create_join_sql_string(sql_string, sql_argument_array, clause_added)
        return self.filesystem_shared_code2(sql_string, sql_argument_array, clause_added, order_by, max_results)

    def find_filenames(self,
                       sql: str,
                       parameters: Optional[Union[Iterable, dict]] = None):
        logging.debug(f"SQL Query: \"{sql}\"")
        logging.debug(f"filename: \"{parameters}\"")
        self.execute(sql,
                     parameters
                     )
        #rows_found = 0
        select_result = self.fetch_all_results()
        """
        for row in select_result:
            print(f"{row[1]}, {row[0]}")
            rows_found += 1
        logging.debug(f"{rows_found} results found")
        """
        return select_result

    def find_drive_id(self, make: str, model: str, serial_number: str):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_drive_id"]}\"")
        logging.debug(f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\"")
        self.execute(self.__sql_dictionary["find_drive_id"],
                     (make, model, serial_number)
                     )
        drive_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            #print(row[0])
            drive_ids.append(row[0])
            rows_found += 1
        logging.debug(f"{rows_found} results found")
        return drive_ids

    def insert_drive(self, make: str, model: str, serial_number: str, hostname: str):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["insert_drive"]}\"")
        logging.debug(
            f"make: \"{make}\", model: \"{model}\", serial_number: \"{serial_number}\", hostname: \"{hostname}\"")
        self.execute(self.__sql_dictionary["insert_drive"],
                     (make, model, serial_number, hostname)
                     )
        drive_id = self.get_last_row_id()
        logging.debug(f"New row driveid: \"{drive_id}\"")
        return drive_id

    def does_label_exists(self, label: str):
        filesystem_ids = self.find_filesystem_id(label)
        if len(filesystem_ids) > 0:
            return True
        else:
            return False

    def find_filesystem_labels(self):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_filesystem_ids"]}\"")
        self.execute(self.__sql_dictionary["find_filesystem_ids"])
        filesystem_labels = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            #print(row[0])
            filesystem_labels.append(row[0])
            rows_found += 1
        logging.debug(f"{rows_found} results found")
        return filesystem_labels

    def find_filesystem_id(self, label: str):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_filesystem_id"]}\"")
        logging.debug(f"label: \"{label}\"")
        self.execute(self.__sql_dictionary["find_filesystem_id"],
                     [label]  # Use [] as a single parameter
                     )
        filesystem_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            #print(row[0])
            filesystem_ids.append(row[0])
            rows_found += 1
        logging.debug(f"{rows_found} results found")
        return filesystem_ids

    def find_directory_direct_children(self, parent_file_system_entry_id: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_directory_direct_children"]}\"")
        logging.debug(f"parent_file_system_entry_id: \"{parent_file_system_entry_id}\"")
        self.execute(self.__sql_dictionary["find_directory_direct_children"],
                     [parent_file_system_entry_id]  # Use [] as a single parameter
                     )
        return self.build_array_of_results()

    def find_directories_with_only_child_entries_with_sizes(self, file_system_id: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["find_directories_with_only_child_entries_with_sizes"]}\"")
        logging.debug(f"file_system_id: \"{file_system_id}\"")
        self.execute(self.__sql_dictionary["find_directories_with_only_child_entries_with_sizes"],
                     [file_system_id]  # Use [] as a single parameter
                     )
        return self.build_array_of_results()

    def build_array_of_results(self):
        filesystem_entries_ids = []
        rows_found = 0
        select_result = self.fetch_all_results()
        for row in select_result:
            #print(row[0])
            tmp_row = [row[0], row[1], row[2], row[3], row[4]]
            filesystem_entries_ids.append(tmp_row)
            rows_found += 1
        logging.debug(f"{rows_found} results found")
        return filesystem_entries_ids

    def insert_filesystem(self, label: str, drive_id: int, date: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["insert_filesystem"]}\"")
        logging.debug(f"label: \"{label}\", drive_id: \"{drive_id}\", date: \"{date}\"")
        self.execute(self.__sql_dictionary["insert_filesystem"],
                     (label, drive_id, date)
                     )
        filesystem_id = self.get_last_row_id()
        logging.debug(f"New row filesystem_id: \"{filesystem_id}\"")
        return filesystem_id

    def delete_filesystem(self, label: str = None):
        if label is None:
            result = "The label must be specified. Can't delete label entries without one."
        else:
            filesystem_ids = self.find_filesystem_id(label)
            if len(filesystem_ids) == 1:
                filesystem_id = filesystem_ids[0]
                # First Delete the filesystem entries
                self.delete_filesystem_listing_entries(filesystem_id)
                # Next Check if the Drive is being used by any other Volume Labels
                # If not, delete the Drive as it's no longer required
                # Finally delete the filesystem listing itself
                self.delete_filesystem_listing(filesystem_id)
                result = True
            else:
                result = "Too many filesystem entries found for the label specified."
        return result

    def delete_filesystem_listing(self, filesystem_id: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["delete_filesystem"]}\"")
        logging.debug(f"filesystem_id: \"{filesystem_id}\"")
        self.execute(self.__sql_dictionary["delete_filesystem"],
                     [filesystem_id]  # [] as a single parameter
                     )

    def delete_filesystem_listing_entries(self, filesystem_id: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["delete_filesystem_entries"]}\"")
        logging.debug(f"filesystem_id: \"{filesystem_id}\"")
        self.execute(self.__sql_dictionary["delete_filesystem_entries"],
                     [filesystem_id]  # [] as a single parameter
                     )

    def update_filesystem_date(self, filesystem_id: int, date: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["update_filesystem"]}\"")
        logging.debug(f"filesystem_id: \"{filesystem_id}\", date: \"{date}\"")
        self.execute(self.__sql_dictionary["update_filesystem"],
                     (date, filesystem_id)  # () as multiple parameters
                     )

    def update_dir_size(self, filesystem_entry_id: int, total_byte_size: int):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["update_filesystem_entry_size"]}\"")
        logging.debug(f"filesystem_entry_id: \"{filesystem_entry_id}\", total_byte_size: \"{total_byte_size}\"")
        self.execute(self.__sql_dictionary["update_filesystem_entry_size"],
                     (total_byte_size, filesystem_entry_id)  # () as multiple parameters
                     )

    def reset_dir_sizes(self, filesystem_id: int = None):
        logging.debug(f"SQL Query: \"{self.__sql_dictionary["reset_filesystem_entries_directory_sizes"]}\"")
        logging.debug(f"filesystem_id: \"{filesystem_id}\"")
        result = self.execute(self.__sql_dictionary["reset_filesystem_entries_directory_sizes"],
                     [filesystem_id]  # [] as a single parameter
                     )
        if isinstance(result, sqlite3.Error):
            return result
        else:
            return self.rows_affected()

    def empty_table(self, table_name: str):
        ## FIX ##
        # self.execute("DELETE FROM ?;", [table_name]) # As a single parameter, we have to wrap it in []
        # self.execute("DELETE FROM SQLITE_SEQUENCE WHERE name=?;", [table_name] )
        # Commit changes to the database
        # self.commit()
        return

### Class Test ###
# database = Database("I:\\FileProcessorDatabase\\database.sqlite")
# logging.debug(f"sql_dictionary: {database.sql_dictionary}")
