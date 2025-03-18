import re

class Convert:

    BINARY_LABELS: [str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    METRIC_LABELS: [str] = ["iB", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    PRECISION_FORMATS: [str] = []

    def __init__(self):
        pass

    @staticmethod
    def bytesize2string(size: int, metric: bool=False, precision: int=1, spacer: str=" ") -> str:
        temp_size = size
        for i in range(0, 11):
            Convert.PRECISION_FORMATS.append("{}{:."+str(i)+"f}"+spacer+"{}")
            #"{}{:.0f} {}", "{}{:.1f} {}", "{}{:.2f} {}", "{}{:.3f} {}"]
        unit_labels = Convert.METRIC_LABELS if metric else Convert.BINARY_LABELS
        is_negative = temp_size < 0
        if is_negative:
            temp_size = abs(temp_size)
        size_type = 0
        divide_factor = 1024 if not metric else 1000
        while temp_size >= divide_factor:
            size_type += 1
            temp_size = temp_size / divide_factor
        if size_type == 0:
            # Under the first divide_factor so it doesn't make sense to show a decimal point
            precision = 0
        return Convert.PRECISION_FORMATS[precision].format("-" if is_negative else "", temp_size, unit_labels[size_type])

    @staticmethod
    def string2bytesize(size_string: str) -> int | None:
        #print("*** string2bytesize() ***")
        #print(f"- size_string: '{size_string}'")
        size_decimal_part_string_array = re.findall("([0-9.,-]+)", size_string)
        if size_decimal_part_string_array is None or len(size_decimal_part_string_array) == 0:
            return None
        else:
            size_decimal_string = str(size_decimal_part_string_array[0]).replace(",", "").strip() # Remove any commas and strip white space
            size_unit_string_array = re.findall("[a-zA-Z]+", size_string)
            if size_unit_string_array is None or len(size_unit_string_array) == 0:
                # No unit given so just return the size
                size_bytes = int(float(size_decimal_string))
                return size_bytes
            else:
                size_unit_string = str(size_unit_string_array[0]).upper().strip().replace('I','i') # Make UPPERCASE and strip white space
                #print(f"- size_decimal_part_string: '{size_decimal_string}'")
                #print(f"- size_unit_string: '{size_unit_string}'")
                if size_unit_string in Convert.BINARY_LABELS:
                    labels_array = Convert.BINARY_LABELS
                    k_size = 1024
                elif size_unit_string in Convert.METRIC_LABELS:
                    labels_array = Convert.METRIC_LABELS
                    k_size = 1000
                else:
                    return None
                size_unit_index = labels_array.index(size_unit_string)
                #print(f"- size_unit_index: '{size_unit_index}'")
                size_bytes = int(float(size_decimal_string) * (k_size ** size_unit_index))
                return size_bytes

    @staticmethod
    def print_string2bytesize(size_string: str):
        print(f"{size_string} = {Convert.string2bytesize(size_string)} bytes")

if __name__ == "__main__":
    print("*** TESTS ***")
    print("*** bytesize2string ***")
    print(Convert.bytesize2string(2251799813685247)) # 2 pebibytes
    print(Convert.bytesize2string(2000000000000000, True)) # 2 petabytes
    print(Convert.bytesize2string(1099511627776)) # 1 tebibyte
    print(Convert.bytesize2string(1000000000000, True)) # 1 terabyte
    print(Convert.bytesize2string(1000000000, True)) # 1 gigabyte
    print(Convert.bytesize2string(4318498233, precision=3)) # 4.022 gibibytes
    print(Convert.bytesize2string(4318498233, True, 3)) # 4.318 gigabytes
    print(Convert.bytesize2string(-4318498233, precision=2)) # -4.02 gibibytes
    print(Convert.bytesize2string(1024, precision=2))
    print(Convert.bytesize2string(-1024, precision=2))
    print(Convert.bytesize2string(1024, True, precision=2))
    print(Convert.bytesize2string(-1024, True, precision=2))
    print()
    print("*** string2bytesize ***")
    Convert.print_string2bytesize("1024")
    Convert.print_string2bytesize("1,000,000")
    Convert.print_string2bytesize("1kb")
    Convert.print_string2bytesize("1KB")
    Convert.print_string2bytesize("1 kb")
    Convert.print_string2bytesize("1 KB")
    Convert.print_string2bytesize("1kib")
    Convert.print_string2bytesize("1KiB")
    Convert.print_string2bytesize("1 kib")
    Convert.print_string2bytesize("1 KiB")
    Convert.print_string2bytesize("1.5 KB")
    Convert.print_string2bytesize("1.5 KiB")
    Convert.print_string2bytesize("1,000 mib")



