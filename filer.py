from add_args import AddArgs
from f import F
import logging
import sys
import argparse
from program import Program

class Filer(Program):
    pass

if __name__ == "__main__":
    # my_logger = logging.getLogger(__name__)
    F.start_logger(logging.DEBUG)
    logging.info(f"### __main__ ###")

    new_parser = argparse.ArgumentParser(
        description="Filer - File Cataloger"
    )
    filer = Filer(new_parser, False)
    filer.start()
