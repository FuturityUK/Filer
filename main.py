# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Windows PowerShell command to capture all files and their permissions: "-First 1000" limits search to first 1000 files found:
# Get-ChildItem -Path E:\ -ErrorAction SilentlyContinue -Recurse -Force | Select-Object -First 1000 Mode, LastWriteTime, Length, FullName | Format-Table -Wrap -AutoSize | Out-File -width 9999 -Encoding utf8 "C:\Users\Administrator.WS1\Documents\csv\ws1-e.csv"

from file_system_processors import PowerShellFilesystemListing
from queries import Queries
from database import Database
import tracemalloc

MEMORY_STATS = False

if MEMORY_STATS:
    # Start tracing memory allocations
    tracemalloc.start()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("!!! Starting !!!")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

'''
TO DO:
- Work out the size of a drive so that when it is being scanned, progress as a percentage can be shown.
- Time the different between using an array and a dictionary. The array should be a lot faster.
- Store sizes of directories
- add files to exclude from the directory size calculations like themnails, apple directory cache files (get list from other programs)

'''

input_filename = "C:\\Data\\ws1,e.fwf"
output_filename = "C:\\Data\\ws1,e.csv.txt"
database_filename = "I:\\FileProcessorDatabase\\database.sqlite"
database = Database()
database_connection = database.create_connection(database_filename)
#print(f"database_connection: {database_connection}")

powershell_filesystem_listing = PowerShellFilesystemListing(input_filename, MEMORY_STATS)
powershell_filesystem_listing.set_dry_run_mode(False)
# Now that data is loaded into the database DON'T run this again
#powershell_filesystem_listing.save_to_CSV(output_filename)
powershell_filesystem_listing.save_to_database(database_connection)
powershell_filesystem_listing.process_file()

queries = Queries(database_connection)

# Closing the connection
database_connection.close()

if MEMORY_STATS:
    # Stop tracing memory allocations
    tracemalloc.stop()

exit()
