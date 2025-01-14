import csv
import os
import datetime
import os.path
import time
from logging import NullHandler
import tracemalloc

# from fileinput import filename

class PowerShellFilesystemListing:
    """ Class to convert the output from the PowerShell Get-ChildItem command into a CSV database form """

    # Below is the Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
    # Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"
    cvs_mode = None
    input_filename = None
    output_filename = None
    database_connection = None
    memory_stats = False

    def __init__(self, input_filename, memory_stats):
        print("__init__()")
        self.input_filename = input_filename
        self.memory_stats = memory_stats

    def save_to_CSV(self, output_filename):
        self.cvs_mode = True
        self.output_filename = output_filename

    def save_to_database(self, database_connection):
        # print(database_connection)
        self.cvs_mode = False
        self.database_connection = database_connection
        self.output_filename = os.devnull

    def insert_filesystem_entry(self, database_cursor, unix_timestamp, byte_size, parent_file_system_entry_id, mode_directory, mode_archive, mode_read_only, mode_hidden, mode_system, mode_link, entity_name, full_name):
        # Insert Entity
        database_cursor.execute(
            "INSERT INTO FileSystemEntries (LastWriteTime, ByteSize, ParentFileSystemEntryID, IsDirectory, IsArchive, IsReadOnly, IsHidden, IsSystem, IsLink, Filename, FullName) VALUES (?,?,?,?,?,?,?,?,?,?,?);",
            (unix_timestamp, byte_size, parent_file_system_entry_id, mode_directory, mode_archive, mode_read_only, mode_hidden, mode_system, mode_link, entity_name, full_name) )
        # Retrieve the ID of the newly inserted row
        return database_cursor.lastrowid

    def display_memory_stats(self):
        if self.memory_stats:
            # Get the current memory usage
            current, peak = tracemalloc.get_traced_memory()
            print(f"Current mem: {current / 1024} KB, Peak mem: {peak / 1024} KB")

    def process_file(self):
        print("process_file()")
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

        with open(self.output_filename, 'w', newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE,
                                delimiter='|', quotechar='"', escapechar='\\')

            if not self.cvs_mode:
                # Create a cursor object using the cursor() method
                database_cursor = self.database_connection.cursor()

                # Check is tables already exist.
                # If it exists, empty all the data and reset autoincrement counters
                database_cursor.execute("DELETE FROM FileSystemEntries;")
                database_cursor.execute("DELETE FROM SQLITE_SEQUENCE WHERE name='FileSystemEntries';")
                # Commit changes to the database
                self.database_connection.commit()
                # Shrink to database to reclaim disk space
                self.database_connection.isolation_level = None
                database_cursor.execute('VACUUM')
                self.database_connection.isolation_level = ''  # <- note that this is the default value of isolation_level
                self.database_connection.commit()

                # If not create them.

                # Create database tables
                # create_table_sql = """;"""
                # database_cursor.execute(create_table_sql)


            for width in field_widths:
                slices.append(slice(offset, offset + width))
                offset += width

            for filelineno, line in enumerate(open(self.input_filename, encoding="utf-8")):
                line_number += 1
                line_right_strip = line.rstrip()
                # print("Line loaded")
                # print(f"next_line_field_widths: {next_line_field_widths}")
                # print(f"{line_number}: '{line_right_strip}'")  # .strip()
                if not header_line_processed:
                    if line_right_strip.startswith("Mode"):
                        # Must be the first line containing text, so much be the header
                        field_headers = line_right_strip.split()
                        print(field_headers)
                        if self.cvs_mode:
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
                        if self.cvs_mode:
                            writer.writelines([pieces_right_strip])  # Wrap inside a list to stop writer delimiting each char
                            # csv_file.flush()
                        else:

                            mode_directory = False # d - Directory
                            mode_archive = False   # a - Archive
                            mode_read_only = False # r - Read-only
                            mode_hidden = False    # h - Hidden
                            mode_system = False    # s - System
                            mode_link = False      # l - Reparse point, symlink, etc.
                            mode_list = list(pieces_right_strip[0])
                            if mode_list[0] == 'd':
                                mode_directory = True
                            if mode_list[1] == 'a':
                                mode_archive = True
                            if mode_list[2] == 'r':
                                mode_read_only = True
                            if mode_list[3] == 'h':
                                mode_hidden = True
                            if mode_list[4] == 's':
                                mode_system = True
                            if mode_list[5] == 'l':
                                mode_link = True
                            # print(f"{pieces_right_strip[0]}{mode_list}{mode_directory}{mode_archive}{mode_read_only}{mode_hidden}{mode_system}{mode_link}")
                            # DateTime string
                            datetime_string = pieces_right_strip[1]
                            # print(f"datetime_string: {datetime_string}")
                            # Parse the string into a datetime object
                            datetime_obj = datetime.datetime.strptime(datetime_string, "%d/%m/%Y %H:%M:%S")
                            # print(f"datetime_obj: {datetime_obj}")
                            try:
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
                                id_of_inserted_row = self.insert_filesystem_entry(database_cursor, 1736028193, None,
                                                        None, 1, 0, 0,
                                                        1, 1, 0, entity_parent_directory, entity_parent_directory)
                                last_saved_directory_name = entity_parent_directory
                                last_saved_directory_id = id_of_inserted_row
                                directory_dictionary[entity_parent_directory] = id_of_inserted_row
                                root_entity_not_found = False

                            # Find Parent Directory ID
                            # Check if the last inserted directory is the parent directory
                            if last_saved_directory_id != 0 and last_saved_directory_name == entity_parent_directory:
                                parent_file_system_entry_id = last_saved_directory_id
                                hits_last_saved_directory += 1
                            else:
                                try:
                                    # If not, see if it's in the directory_dictionary cache
                                    parent_file_system_entry_id = directory_dictionary[entity_parent_directory]
                                    hits_directory_dictionary += 1
                                    # print("Cache")
                                except KeyError:
                                    # If not, see if it's in the database
                                    # print("Database")
                                    parent_file_system_entry_id = None
                                    #database_cursor.execute("SELECT FileSystemEntryID, FullName FROM FileSystemEntries WHERE IsDirectory = 1 AND FullName = ?;", [entity_parent_directory])
                                    database_cursor.execute("SELECT FileSystemEntryID FROM FileSystemEntries WHERE IsDirectory = 1 AND FullName = ?;", [entity_parent_directory])
                                    select_result = database_cursor.fetchall()
                                    for x in select_result:
                                        # print(x)
                                        parent_file_system_entry_id = x[0]
                                        hits_database += 1
                                        # print(parent_file_system_entry_id)

                            # Insert Entity
                            id_of_inserted_row = self.insert_filesystem_entry(database_cursor, unix_timestamp, byte_size, parent_file_system_entry_id,
                                                         mode_directory, mode_archive, mode_read_only, mode_hidden,
                                                         mode_system, mode_link, entity_name, full_name)
                            if mode_directory:
                                last_saved_directory_name = full_name
                                last_saved_directory_id = id_of_inserted_row
                                directory_dictionary[full_name] = id_of_inserted_row
                                # print(directory_dictionary)

                            #database_cursor.execute(
                            #    "INSERT INTO FileSystemEnties (LastWriteTime, ByteSize, ParentFileSystemEntryID, IsDirectory, IsArchive, IsReadOnly, IsHidden, IsSystem, IsLink, Filename, FullName) VALUES (?,?,NULL,?,?,?,?,?,?,?,?);",
                            #    (unix_timestamp, byte_size, mode_directory, mode_archive, mode_read_only, mode_hidden, mode_system, mode_link, entity_name, full_name) )


                        lines_processed += 1
                        #if(lines_processed > 50):
                        #    break

                        time_taken_ms = (time.time() - processing_data_lines_start_time)*1000

                    if (lines_processed % 10000 == 0):
                        print(f"Processed: {lines_processed} lines, in {int(time_taken_ms)}ms = {int((lines_processed / time_taken_ms) * 1000)} lines/s, LS: {hits_last_saved_directory} {int(hits_last_saved_directory/(hits_last_saved_directory+hits_directory_dictionary+hits_database)*100)}%, DD: {hits_directory_dictionary}, DB: {hits_database}")
                        self.display_memory_stats()
                        # Commit changes to the database
                        self.database_connection.commit()

                    # if (lines_processed >= 10000):
                    #     print(f"Lines: Processed: {lines_processed}, in {time_taken_ms}ms = {(1000 / time_taken_ms) * 1000} lines per second")
                    #     # Commit changes to the database
                    #     self.database_connection.commit()
                    #     # Closing the connection
                    #     self.database_connection.close()
                    #     exit()

        print(f"Processed: {lines_processed} lines, in {int(time_taken_ms)}ms = {int((lines_processed / time_taken_ms)) * 1000} lines/s")
        self.display_memory_stats()
        # Commit changes to the database
        self.database_connection.commit()
        # Closing the connection
        self.database_connection.close()
        print("File Processed")



class FilesystemDatabase:
    """ Class to load and process the CSV database """

    # Below is the Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
    # Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

    def __init__(self, database_directory):
        print("__init__()")
        self.database_directory = database_directory

