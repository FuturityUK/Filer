import time

class Format:

    @staticmethod
    def print_local_timezone_info():
        local_time = time.localtime()
        print("Local Time Zones : ", time.tzname)
        print("Current Time Zone: ", time.strftime("%Z", local_time))

    @staticmethod
    def datetime_to_string(datetime_object: time = None):
        return time.strftime("%Y-%m-%d %H:%M:%S", datetime_object)
