from add_args import AddArgs
from f import F
import argparse
import logging
import tracemalloc

class Program:

    def __init__(self, argument_parser, memory_stats: bool, database_filename: str = None): # : argparse.ArgumentParser
        F.start_logger(logging.DEBUG)
        logging.debug(f"### __init__() ###")
        self.argument_parser = argument_parser
        self.memory_stats = memory_stats
        self.database_filename = database_filename
        self.f = None

        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

    def start(self):
        logging.debug(f"### F.start() ###")
        self.init()
        self.seed()
        self.main()

    def init(self):
        logging.debug(f"### init() ###")
        logging.info(f"Initialising Argument Parser Arguments...")
        AddArgs.add_subcommands_to_parser(self.argument_parser)
        self.f = F(self, self.argument_parser, self.memory_stats, self.database_filename)
        # self.parser.set_defaults(**self.stored_args)

    def seed(self, clear: []=None):
        logging.info(f"### seed() ###")

    def main(self):
        logging.info(f"### main() ###")
        # Get the arguments
        args = self.argument_parser.parse_args()
        # Now process the args
        self.f.process_args_and_call_subcommand(args)