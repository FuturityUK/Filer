class Format:

    METRIC_LABELS: [str] = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    BINARY_LABELS: [str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    PRECISION_FORMATS: [str] = []

    def __init__(self):
        pass

    @staticmethod
    def format_storage_size(size: int, metric: bool=False, precision: int=1, spacer: str=" ") -> str:
        temp_size = size
        for i in range(0, 11):
            Format.PRECISION_FORMATS.append("{}{:."+str(i)+"f}"+spacer+"{}")
            #"{}{:.0f} {}", "{}{:.1f} {}", "{}{:.2f} {}", "{}{:.3f} {}"]
        unit_labels = Format.METRIC_LABELS if metric else Format.BINARY_LABELS
        is_negative = temp_size < 0
        if is_negative:
            temp_size = abs(temp_size)
        size_type = 0
        divide_factor = 1024 if metric else 1000
        while temp_size > divide_factor:
            size_type += 1
            temp_size = temp_size / divide_factor
        return Format.PRECISION_FORMATS[precision].format("-" if is_negative else "", temp_size, unit_labels[size_type])

    """
    print(format_storage_size(2251799813685247)) # 2 pebibytes
    print(format_storage_size(2000000000000000, True)) # 2 petabytes
    print(format_storage_size(1099511627776)) # 1 tebibyte
    print(format_storage_size(1000000000000, True)) # 1 terabyte
    print(format_storage_size(1000000000, True)) # 1 gigabyte
    print(format_storage_size(4318498233, precision=3)) # 4.022 gibibytes
    print(format_storage_size(4318498233, True, 3)) # 4.318 gigabytes
    print(format_storage_size(-4318498233, precision=2)) # -4.02 gibibytes
    """
