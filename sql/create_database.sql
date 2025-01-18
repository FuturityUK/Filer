-- FileSystems definition

CREATE TABLE "FileSystems" (
	DrivesID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
, Label TEXT NOT NULL, DateAdded INTEGER NOT NULL);

CREATE INDEX Drives_DateAdded_IDX ON "FileSystems" (DateAdded);
CREATE UNIQUE INDEX FileSystems_Label_IDX ON FileSystems (Label);


-- FileSystemEntries definition

CREATE TABLE "FileSystemEntries" (
	FileSystemEntryID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	LastWriteTime INTEGER NOT NULL,
	ByteSize INTEGER,
	ParentFileSystemEntryID INTEGER,
	IsDirectory INTEGER NOT NULL,
	IsArchive INTEGER NOT NULL,
	IsReadOnly INTEGER NOT NULL,
	IsHidden INTEGER NOT NULL,
	IsSystem INTEGER NOT NULL,
	IsLink INTEGER NOT NULL
, Filename TEXT, "FullName" TEXT);

CREATE INDEX FileSystemEntries_Filename_IDX ON FileSystemEntries (Filename);
CREATE INDEX FileSystemEntries_ByteSize_IDX ON FileSystemEntries (ByteSize);
CREATE INDEX FileSystemEntries_LastWriteTime_IDX ON FileSystemEntries (LastWriteTime);
CREATE INDEX FileSystemEntries_IsDirectory_IDX ON FileSystemEntries (IsDirectory);
