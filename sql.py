
class SQLDictionary:
    """ Class to SQL strings for various operations """

    def __init__(self):
        self.sql_dictionary = {}

        self.sql_dictionary["create_database_tables_and_indexes"] = '''
                -- FileSystemEntries definition
                
                CREATE TABLE "FileSystemEntries" (
                    FileSystemEntryID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Filename TEXT,
                    ByteSize INTEGER,
                    LastWriteTime INTEGER NOT NULL,
                    IsDirectory INTEGER NOT NULL,
                    IsArchive INTEGER NOT NULL,
                    IsReadOnly INTEGER NOT NULL,
                    IsHidden INTEGER NOT NULL,
                    IsSystem INTEGER NOT NULL,
                    IsLink INTEGER NOT NULL, 
                    FileSystemID INTEGER NOT NULL,
                    ParentFileSystemEntryID INTEGER,
                    "FullName" TEXT
                    );
                
                CREATE INDEX FileSystemEntries_Filename_IDX ON FileSystemEntries (Filename);
                CREATE INDEX FileSystemEntries_ByteSize_IDX ON FileSystemEntries (ByteSize);
                CREATE INDEX FileSystemEntries_LastWriteTime_IDX ON FileSystemEntries (LastWriteTime);
                CREATE INDEX FileSystemEntries_IsDirectory_IDX ON FileSystemEntries (IsDirectory);
                CREATE INDEX FileSystemEntries_FileSystemID_IDX ON FileSystemEntries (FileSystemID);
                
                -- FileSystems definition
                
                CREATE TABLE "FileSystems" (
                    FileSystemID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
                    Label TEXT NOT NULL, 
                    DriveID INTEGER, 
                    DateAdded INTEGER NOT NULL
                    );
                
                CREATE INDEX Drives_DateAdded_IDX ON "FileSystems" (DateAdded);
                CREATE UNIQUE INDEX FileSystems_Label_IDX ON FileSystems (Label);
                CREATE INDEX FileSystems_DriveID_IDX ON FileSystems (DriveID);
                
                -- Drives definition
                
                CREATE TABLE Drives (
                    DriveID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Make INTEGER,
                    Model INTEGER,
                    SerialNumber INTEGER
                );
            '''

        self.sql_dictionary["find_filename_exact_match"] = '''
                SELECT Fullname
                FROM FileSystemEntries
                WHERE Filename = ?
            '''

        self.sql_dictionary["find_filename_like"] = '''
                SELECT Fullname
                FROM FileSystemEntries
                WHERE Filename LIKE ?
            '''
### Class Test ###
#sql_dictionary = SQLDictionary()
#print(f"create_database: {sql_dictionary.sql_dictionary["create_database"]}")