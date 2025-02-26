
class SQLDictionary:
    """ Class to SQL strings for various operations """

    def __init__(self):
        self.sql_versions = {
            "1": "create_database_tables_and_indexes",
            "2": "modify_database_tables_and_indexes_v2"
        }

        self.sql_dictionary = {

            "does_database_information_table_exist": '''
                SELECT name FROM sqlite_master WHERE type='table' AND name='DatabaseInformation';        
            ''', "find_db_version": '''
                SELECT Value FROM DatabaseInformation WHERE KeyName = "DBVersion"; 
            ''',

            "create_database_tables_and_indexes": '''
                -- Drives definition
                CREATE TABLE Drives (
                                    DriveID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                                    Make TEXT,
                                    Model TEXT,
                                    SerialNumber TEXT, 
                                    Hostname TEXT
                                );
                CREATE INDEX Drives_Make_IDX ON Drives (Make);
                CREATE INDEX Drives_Model_IDX ON Drives (Model);
                CREATE INDEX Drives_SerialNumber_IDX ON Drives (SerialNumber);
                CREATE UNIQUE INDEX Drives_Make_Model_SerialNumber_IDX ON Drives (Make,Model,SerialNumber);
                CREATE INDEX Drives_hostname_IDX ON Drives (Hostname);
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
                CREATE UNIQUE INDEX FileSystemEntries_FileSystemID_FullName_IDX ON FileSystemEntries (FileSystemID,FullName);
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
            ''',

            "modify_database_tables_and_indexes_v2": '''
                -- Categories definition
                CREATE TABLE Categories (
                    CategoryID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Name TEXT
                );
                CREATE UNIQUE INDEX Categories_Name_IDX ON Categories (Name);
                -- SubCategories definition
                CREATE TABLE SubCategories (
                    SubCategoryID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Name TEXT
                );
                CREATE UNIQUE INDEX SubCategories_Name_IDX ON SubCategories (Name);
                -- SubCategories2 definition
                CREATE TABLE SubCategories2 (
                    SubCategory2ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    Name TEXT
                );
                CREATE UNIQUE INDEX SubCategories2_Name_IDX ON SubCategories2 (Name);
                -- FileTypes definition
                CREATE TABLE FileTypes (
                    FileTypeID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    CategoryID INTEGER,
                    SubCategoryID INTEGER,
                    SubCategory2ID INTEGER,
                    Extension TEXT,
                    Description TEXT
                );
                CREATE INDEX FileTypes_CategoryID_IDX ON FileTypes (CategoryID);
                CREATE INDEX FileTypes_SubCategoryID_IDX ON FileTypes (SubCategoryID);
                CREATE INDEX FileTypes_SubCategory2ID_IDX ON FileTypes (SubCategory2ID);
                CREATE UNIQUE INDEX FileTypes_Extension_IDX ON FileTypes (Extension);
                -- Update FileSystemEntries
                ALTER TABLE FileSystemEntries ADD FileTypeID INTEGER;
                CREATE INDEX FileSystemEntries_FileTypeID_IDX ON FileSystemEntries (FileTypeID);
                -- DatabaseInformation definition
                CREATE TABLE DatabaseInformation (
                    DatabaseInformationID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    KeyName TEXT NOT NULL,
                    Value TEXT
                );
                CREATE UNIQUE INDEX DatabaseInformation_Key_IDX ON DatabaseInformation ("Key");
                -- Set DBVersion to "2"
                INSERT OR REPLACE INTO DatabaseInformation (DatabaseInformationID, KeyName, Value) VALUES (
                    (SELECT DatabaseInformationID FROM DatabaseInformation WHERE KeyName = "DBVersion"),
                    "DBVersion", "2");   
            ''',

            "find_filename_base": '''
                SELECT fs.Label, fse.Filename, fse.ByteSize, fse.LastWriteTime, fse.IsDirectory, fse.IsArchive, fse.IsReadOnly, fse.IsHidden, fse.IsSystem, fse.IsLink, fse.FullName
                FROM FileSystemEntries AS fse, FileSystems AS fs
                WHERE 
            ''',

            "find_filename_like_filename_clause": '''
                fse.Filename LIKE ?
            ''',

            "find_filename_exact_match_filename_clause": '''
                fse.Filename = ?
            ''',

            "find_filename_label_clause": '''
                fs.Label = ?
            ''',

            "find_filename_join": '''
                AND fse.FileSystemID = fs.FileSystemID
            ''',

            "find_filename_limit_clause": '''
                LIMIT ?
            ''',

            "find_drive_id": '''
                SELECT DriveID 
                FROM Drives
                WHERE Make = ? AND Model = ? AND SerialNumber = ?;    
            ''',

            "insert_drive": '''
                INSERT INTO Drives
                (Make, Model, SerialNumber, Hostname)
                VALUES (?, ?, ?, ?);    
            ''',

            "find_filesystem_ids": '''
                SELECT Label 
                FROM FileSystems;    
            ''',

            "find_filesystem_id": '''
                SELECT FileSystemID 
                FROM FileSystems
                WHERE Label = ?;    
            ''',

            "insert_filesystem": '''
                INSERT INTO FileSystems
                (Label, DriveID, DateAdded)
                VALUES (?, ?, ?);    
            ''',

            "delete_filesystem": '''
                DELETE FROM FileSystems
                WHERE FileSystemID = ?; 
            ''',

            "delete_filesystem_entries": '''
                DELETE FROM FileSystemEntries
                WHERE FileSystemID = ?; 
            ''',

            "update_filesystem": '''
                UPDATE FileSystems
                SET DateAdded = ?
                WHERE FileSystemID = ?; 
            '''

        }

### Class Test ###
#sql_dictionary = SQLDictionary()
#print(f"create_database: {sql_dictionary.sql_dictionary["create_database"]}")