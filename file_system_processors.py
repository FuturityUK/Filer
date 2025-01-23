import csv
import os
import datetime
import os.path
import sqlite3
import time
import tracemalloc
from typing import (
    cast,
    Any,
    Callable,
    Dict,
    Generator,
    Iterable,
    Union,
    Optional,
    List,
    Tuple,
)
from datetime import datetime
from database import Database

class PowerShellFilesystemListing:
    """ Class to convert the output from the PowerShell Get-ChildItem command into a CSV database form """

    # Below is the Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
    # Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

    # Constants
    PROCESSING_MODE_NOT_SET = 0
    PROCESSING_MODE_CSV = 1
    PROCESSING_MODE_DB = 2

    def __init__(self, database: Database, label: str, input_filename: str):
        self.__label = label
        self.__input_filename = input_filename
        self.__processing_mode = self.PROCESSING_MODE_NOT_SET
        self.__database = database
        self.__output_csv_filename = None
        self.__test = False
        self.__verbose = False
        self.__memory_stats = False
        self.__make = None
        self.__model = None
        self.__serial_number = None
        self.__hostname = None
        self.__prefix = None
        self.__date = None
        if not os.path.isfile(input_filename):
            # Input file doesn't exist
            print(f"Listing file doesn't exist at location: \"{os.path.abspath(input_filename)}\"")
            print("Exiting")
            exit(2)

    def __vprint(self, string: str):
        if self.__verbose:
            print(string)

    def set_test(self, test: bool):
        self.__test = test

    def set_verbose(self, verbose: bool):
        self.__verbose = verbose
            
    def set_memory_stats(self, memory_stats: bool):
        self.__memory_stats = memory_stats

    def set_make(self, make: str):
        self.__make = make

    def set_model(self, model: str):
        self.__model = model

    def set_serial_number(self, serial_number: str):
        self.__serial_number = serial_number

    def set_combined(self, combined: str):
        combined_list = combined.split(",")
        if len(combined_list) == 3:
            self.set_make(combined_list[0])
            self.set_model(combined_list[1])
            self.set_serial_number(combined_list[2])
        else:
            print(f"Combined string doesn't contain \"make,model,serial_number\": {combined}")

    def set_hostname(self, hostname: str):
        self.__hostname = hostname

    def set_prefix(self, prefix: str):
        self.__prefix = prefix

    def set_date(self, date: int):
        self.__date = date

    def save_to_csv(self, output_csv_filename: str):
        self.__processing_mode = self.PROCESSING_MODE_CSV
        self.__output_csv_filename = output_csv_filename

    def save_to_database(self):
        # print(database_connection)
        self.__processing_mode = self.PROCESSING_MODE_DB
        self.__output_csv_filename = os.devnull

    def display_memory_stats(self):
        if self.__memory_stats:
            # Get the current memory usage
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current mem: {current / 1024} KB, Peak mem: {peak / 1024} KB")

    def __db_insert_filesystem_entry(self, filesystem_id, unix_timestamp, byte_size, parent_file_system_entry_id, mode_is_directory,
                                mode_is_archive, mode_is_read_only, mode_is_hidden, mode_is_system, mode_is_link, entity_name,
                                full_name):
            # Insert Entity
            if self.__test:
                return None
            else:
                self.__database.execute(
                    "INSERT INTO FileSystemEntries (FileSystemID, LastWriteTime, ByteSize, ParentFileSystemEntryID, IsDirectory, IsArchive, IsReadOnly, IsHidden, IsSystem, IsLink, Filename, FullName) VALUES (?,?,?,?,?,?,?,?,?,?,?,?);",
                        (filesystem_id, unix_timestamp, byte_size, parent_file_system_entry_id, mode_is_directory, mode_is_archive, mode_is_read_only,
                                    mode_is_hidden, mode_is_system, mode_is_link, entity_name, full_name) )
                # Retrieve the ID of the newly inserted row
                return self.__database.get_last_row_id()

    def __find_parent_directory_id(self, filesystem_id, last_saved_directory_id, last_saved_directory_name, entity_parent_directory, directory_dictionary):
        # Find Parent Directory ID
        parent_file_system_entry_id = None
        # Check if the last inserted directory is the parent directory
        if last_saved_directory_id != 0 and last_saved_directory_name == entity_parent_directory:
            parent_file_system_entry_id = last_saved_directory_id
            #hits_last_saved_directory += 1
        else:
            try:
                # If not, see if it's in the directory_dictionary cache
                parent_file_system_entry_id = directory_dictionary[entity_parent_directory]
                #hits_directory_dictionary += 1
                # print("Cache")
            except KeyError:
                # If not, see if it's in the database
                # print("Database")
                self.__database.execute(
                    "SELECT FileSystemEntryID FROM FileSystemEntries WHERE IsDirectory = 1 AND FullName = ?;",
                    [entity_parent_directory])
                select_result = self.__database.fetch_all_results()
                for x in select_result:
                    # print(x)
                    parent_file_system_entry_id = x[0]
                    #hits_database += 1
                    # print(parent_file_system_entry_id)
        return parent_file_system_entry_id

    def __choose_filesystem_date(self):
        file_modified_timestamp = int(os.path.getmtime(self.__input_filename))
        now_timestamp = int(time.time())
        selection = None
        while selection not in {"1", "2", "3"}:
            print("Filesystem listing creation date time options:")
            print(f"\t1) {datetime.fromtimestamp(file_modified_timestamp)} UTC - from filesystem listing file's last modified time")
            print(f"\t2) {datetime.fromtimestamp(now_timestamp)} UTC - the current time")
            print("\t3) Exit")
            selection = input("Please enter an option number from those listed above? ")
            if selection == "1":
                self.__date = file_modified_timestamp
            elif selection == "2":
                self.__date = now_timestamp
            elif selection == "3":
                print("Existing.")
                self.__database.close_database()
                exit()

    def get_drive_id(self):
        self.__vprint("get_drive_id()")
        if self.__make is None and self.__model is None and self.__serial_number is None:
            self.__vprint("Drive ignored as Make, Model and Serial Number aren't specified")
        else:
            drive_ids = self.__database.find_drive_id(self.__make, self.__model, self.__serial_number)
            if len(drive_ids) == 1:
                # drive_id found
                return drive_ids[0]
            elif len(drive_ids) == 0:
                # No drive_id found so create one
                return self.__database.insert_drive(self.__make, self.__model, self.__serial_number, self.__hostname)
            else:
                # More than 1 drive_id found so error
                print("Error: More than one drive_id found for the Make, Model and Serial Number specified.")
                print("Exiting.")
                self.__database.close_database()
                exit(2)

    def get_filesystem_id(self):
        self.__vprint("get_filesystem_id()")
        drive_id = self.get_drive_id()
        if self.__make is None and self.__model is None and self.__serial_number is None:
            self.__vprint("Drive ignored as Label isn't specified")
        else:
            filesystem_ids = self.__database.find_filesystem_id(self.__label)
            if len(filesystem_ids) == 1:
                # drive_id found
                filesystem_id = filesystem_ids[0]
                selection = None
                while selection not in {"1", "2"}:
                    print("Filesystem listing already existing in database:")
                    print("\t1) Replace the listing")
                    print("\t2) Exit")
                    selection = input("Please enter an option number from those listed above? ")
                    if selection == "1":
                        self.__database.delete_filesystem_listing_entries(filesystem_id)
                        # Now that the entries for the filesystem have been deleted, update the date
                        self.__choose_filesystem_date()
                        self.__database.update_filesystem_date(self.__date, filesystem_id)
                        return filesystem_id
                    elif selection == "2":
                        self.__database.close_database()
                        print("Existing.")
                        exit()
                return filesystem_ids[0]
            elif len(filesystem_ids) == 0:
                # No drive_id found so create one
                self.__choose_filesystem_date()
                return self.__database.insert_filesystem(self.__label, drive_id, self.__date)
            else:
                # More than 1 drive_id found so error
                print("Error: More than one filesystem_id found for the Label specified.")
                print("Exiting.")
                self.__database.close_database()
                exit(2)

    def import_listing(self):
        self.__vprint("Recording listing details.")
        # Check if records exist first and warn user if they do.
        filesystem_id = self.get_filesystem_id()
        self.__vprint(f"filesystem_id: {filesystem_id}")

        self.__vprint("Processing listing file.")
        header_line_processed = False
        next_line_field_widths = False
        next_line_process = False
        line_number = 0
        lines_processed = 0
        field_widths = []
        slices = []
        offset = 0
        root_entity_not_found = True
        directory_dictionary = {}
        last_saved_directory_name = "" # Shouldn't use None because we can't use string operations on a None type
        last_saved_directory_id = 0 # IDs start at 1 so this 0 will never be used.
        hits_last_saved_directory = 0
        hits_directory_dictionary = 0
        hits_database = 0

        with open(self.__output_csv_filename, 'w', newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE,
                                delimiter='|', quotechar='"', escapechar='\\')

            if self.__processing_mode == self.PROCESSING_MODE_DB:
                # Check is tables already exist.
                # If it exists, empty all the data and reset autoincrement counters
                ##### self.__database.empty_table()
                # Vacuum database to reclaim empty space
                self.__database.vacuum()

                # If not create them.
                # Create database tables
                # create_table_sql = """;"""
                # database_cursor.execute(create_table_sql)


            for width in field_widths:
                slices.append(slice(offset, offset + width))
                offset += width

            input_file_stats = os.stat(self.__input_filename)
            input_file_size_bytes = input_file_stats.st_size
            input_file_processed_bytes = 0

            for filelineno, line in enumerate(open(self.__input_filename, encoding="utf-8")):
                line_number += 1
                input_file_processed_bytes += len(line) +1 # +1 for \n line terminator (HANDLE \r\n in future)

                line_right_strip = line.rstrip()
                # print("Line loaded")
                # print(f"next_line_field_widths: {next_line_field_widths}")
                # print(f"{line_number}: '{line_right_strip}'")  # .strip()
                if not header_line_processed:
                    if line_right_strip.startswith("Mode"):
                        # Must be the first line containing text, so much be the header
                        field_headers = line_right_strip.split()
                        print(field_headers)
                        if self.__processing_mode == self.PROCESSING_MODE_CSV:
                            writer.writelines([field_headers]) # Wrap inside a list to stop writer delimiting each char
                            # csv_file.flush()

                        header_line_processed = True
                        next_line_field_widths = True
                        # exit()
                elif next_line_field_widths is True:
                    # print("Got Here")
                    """
                    if(not line_right_strip.startswith("---- ")):
                        print("Unexpected field width definition line similar to:")
                        print("'----   -------------       ------       --------'")
                        exit()
                    else:
                    """
                    # Calculate max column widths from line, as each path and hence line could be a different length.
                    char = '-'
                    last_char = '-'
                    char_offset = 0
                    line_length = len(line)
                    for i in range(line_length):
                        last_char = char
                        char = line[i]
                        print(char, end="")
                        if (last_char == ' ') and (char == '-'):
                            field_length = i - char_offset
                            char_offset = i
                            field_widths.append(field_length)
                    # Append Path field width
                    field_length = line_length - char_offset
                    # Check that the longest path doesn't get truncated
                    field_widths.append(field_length)
                    # print()
                    # print(field_widths)
                    # Create slices
                    offset = 0
                    for width in field_widths:
                        slices.append(slice(offset, offset + width))
                        offset += width
                    # print(slices)
                    next_line_field_widths = False
                    next_line_process = True
                    processing_data_lines_start_time = time.time()

                elif next_line_process:
                    pieces = [line_right_strip[slice] for slice in slices]
                    pieces_right_strip = [piece.rstrip() for piece in pieces]
                    if len(pieces_right_strip) > 0 and pieces_right_strip[0] != "":
                        # Only save lines with content in them. No mode = no valid row.
                        # print(f"{pieces_right_strip}: {len(pieces_right_strip)}")
                        if self.__processing_mode == self.PROCESSING_MODE_CSV:
                            writer.writelines([pieces_right_strip])  # Wrap inside a list to stop writer delimiting each char
                            # csv_file.flush()
                        elif self.__processing_mode == self.PROCESSING_MODE_DB:
                            modes_list = list(pieces_right_strip[0])
                            mode_is_directory = True if (modes_list[0] == 'd') else False # d - Directory
                            mode_is_archive = True if (modes_list[1] == 'a') else False   # a - Archive
                            mode_is_read_only = True if (modes_list[2] == 'r') else False # r - Read-only
                            mode_is_hidden = True if (modes_list[3] == 'h') else False    # h - Hidden
                            mode_is_system = True if (modes_list[4] == 's') else False    # s - System
                            mode_is_link = True if (modes_list[5] == 'l') else False      # l - Reparse point, symlink, etc.

                            # print(f"{pieces_right_strip[0]}{modes_list}{mode_is_directory}{mode_is_archive}{mode_is_read_only}{mode_is_hidden}{mode_is_system}{mode_is_link}")
                            # DateTime string
                            datetime_string = pieces_right_strip[1]
                            try:
                                self.__vprint(f"datetime_string: {datetime_string}")
                                # Parse the string into a datetime object
                                datetime_obj = datetime.strptime(datetime_string, "%d/%m/%Y %H:%M:%S")
                                self.__vprint(f"datetime_obj: {datetime_obj}")
                                # Convert to UNIX timestamp
                                unix_timestamp = datetime_obj.timestamp()
                            except OSError as err:
                                print(f"datetime_string: {datetime_string}, Timestamp() - OSError: {err}")
                                unix_timestamp = 0
                            # print(f"unix_timestamp: {unix_timestamp}")
                            byte_size = pieces_right_strip[2] # Windows refers to it as length, but this is a reserved word in Sqlite. I'm calling it byte_size
                            if len(byte_size) == 0:
                                byte_size = None
                            full_name = pieces_right_strip[3] # Windows refers to the "path" as "FullName" for some reason.
                            try:
                                # Find the entry name
                                entity_name = os.path.basename(full_name)
                                # Find the directory that this entity lives in
                                entity_parent_directory = os.path.dirname(full_name)
                                # print(f"full_name: {full_name}")
                                # print(f"entity_parent_directory: {entity_parent_directory}")
                            except OSError as err:
                                print(f"full_name: {full_name}")
                                print(f"os.path - OSError: {err}")
                                exit()

                            if root_entity_not_found and len(entity_parent_directory) == 3 and entity_parent_directory.endswith(":\\"):
                                # If the root entity hasn't already been found
                                # and the length of the parent entity directory == 3
                                # and the parent entity directory ends with ":\"
                                # then insert it into the database
                                id_of_inserted_row = self.__db_insert_filesystem_entry(filesystem_id, 1736028193, None,
                                                        None, 1, 0, 0,
                                                        1, 1, 0, entity_parent_directory, entity_parent_directory)
                                last_saved_directory_name = entity_parent_directory
                                last_saved_directory_id = id_of_inserted_row
                                directory_dictionary[entity_parent_directory] = id_of_inserted_row
                                root_entity_not_found = False

                            # Find Parent Directory ID
                            parent_file_system_entry_id = self.__find_parent_directory_id(filesystem_id, last_saved_directory_id, last_saved_directory_name, entity_parent_directory, directory_dictionary)

                            # Insert Entity
                            id_of_inserted_row = self.__db_insert_filesystem_entry(filesystem_id, unix_timestamp, byte_size, parent_file_system_entry_id,
                                                         mode_is_directory, mode_is_archive, mode_is_read_only, mode_is_hidden,
                                                         mode_is_system, mode_is_link, entity_name, full_name)
                            if mode_is_directory:
                                last_saved_directory_name = full_name
                                last_saved_directory_id = id_of_inserted_row
                                directory_dictionary[full_name] = id_of_inserted_row
                                # print(directory_dictionary)

                            #database_cursor.execute(
                            #    "INSERT INTO FileSystemEnties (LastWriteTime, ByteSize, ParentFileSystemEntryID, IsDirectory, IsArchive, IsReadOnly, IsHidden, IsSystem, IsLink, Filename, FullName) VALUES (?,?,NULL,?,?,?,?,?,?,?,?);",
                            #    (unix_timestamp, byte_size, mode_is_directory, mode_is_archive, mode_is_read_only, mode_is_hidden, mode_is_system, mode_is_link, entity_name, full_name) )


                        lines_processed += 1

                        #if(lines_processed > 1):
                        #    break

                        time_taken_ms = (time.time() - processing_data_lines_start_time)*1000

                    if (lines_processed % 10000 == 0):
                        #print(f"Processed: {lines_processed} lines, in {int(time_taken_ms)}ms = {int((lines_processed / time_taken_ms) * 1000)} lines/s, LS: {hits_last_saved_directory} {int(hits_last_saved_directory / (hits_last_saved_directory + hits_directory_dictionary + hits_database) * 100)}%, DD: {hits_directory_dictionary}, DB: {hits_database}")
                        #print(f"Processed: {int(input_file_processed_bytes*1000/input_file_size_bytes)/10}% {lines_processed} lines, in {int(time_taken_ms)}ms = {int((lines_processed / time_taken_ms) * 1000)} lines/s, LS: {hits_last_saved_directory}, DD: {hits_directory_dictionary}, DB: {hits_database}")
                        bytes_remaining_to_process = input_file_size_bytes - input_file_processed_bytes
                        bytes_processed_per_second = input_file_processed_bytes / time_taken_ms * 1000
                        eta_seconds = int(bytes_remaining_to_process * 10 / bytes_processed_per_second) / 10
                        print(f"Processed: {int(input_file_processed_bytes*1000/input_file_size_bytes)/10}%, ETA: {eta_seconds} seconds")
                        self.display_memory_stats()
                        # Commit changes to the database
                        self.__database.commit()

                    # if (lines_processed >= 10000):
                    #     print(f"Lines: Processed: {lines_processed}, in {time_taken_ms}ms = {(1000 / time_taken_ms) * 1000} lines per second")
                    #     # Commit changes to the database
                    #     self.__database_connection.commit()
                    #     # Closing the connection
                    #     self.__database_connection.close()
                    #     exit()

        print(f"Processed: {lines_processed} lines, in {int(time_taken_ms)}ms = {int((lines_processed / time_taken_ms)) * 1000} lines/s")
        self.display_memory_stats()
        # Commit changes to the database
        self.__database.commit()
        print("File Processed")

    def directory_sizes_clear(self):
        sql_directory_sizes_clear = """UPDATE FileSystemEntries SET ByteSize = NULL WHERE IsDirectory = 1;"""
        # Execute SQL
        self.__database.execute(sql_directory_sizes_clear)
        # Commit changes to the database
        self.__database.commit()

    def directory_sizes_calculate(self):
        sql_directory_sizes_calculate = """SELECT fse1.FileSystemEntryID, fse1.FullName, fse1.ByteSize,
SUM(fse2.IsDirectory) Sub_Dirs, SUM(CASE WHEN fse2.ByteSize IS NULL THEN 1 ELSE 0 END) Sub_Dirs_Nulls,
count(fse2.ByteSize) Sub_Dirs_Not_Nulls, SUM(fse2.ByteSize) Total_Size, COUNT(fse2.FullName) Entities_In_Dir
FROM FileSystemEntries fse1
INNER JOIN FileSystemEntries fse2
ON fse1.FileSystemEntryID = fse2.ParentFileSystemEntryID
GROUP BY fse1.FileSystemEntryID
HAVING fse1.ByteSize = NULL;"""
        # Execute SQL
        self.__database.execute(sql_directory_sizes_calculate)
        # Commit changes to the database
        self.__database.commit()

class FilesystemDatabase:
    """ Class to load and process the CSV database """

    # Below is the Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
    # Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

    def __init__(self, database_directory):
        print("__init__()")
        self.database_directory = database_directory

