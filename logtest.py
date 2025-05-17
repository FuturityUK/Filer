import logging
from f import F

if __name__ == "__main__":
    #F.start_logger(logging.DEBUG)
    F.start_logger(logging.CRITICAL)
    logging.info(f"### __main__ ###")