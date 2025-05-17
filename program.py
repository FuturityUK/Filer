from add_args import AddArgs
from f import F
import argparse
import logging
import tracemalloc

class Program:

    PROGRAM_NAME: str = 'Filer'

    def __init__(self, argument_parser, memory_stats: bool, database_filename: str = None): # : argparse.ArgumentParser
        #F.start_logger(logging.DEBUG)
        F.start_logger(logging.CRITICAL)
        logging.debug(f"### Program.__init__() ###")
        self.argument_parser = argument_parser
        self.memory_stats = memory_stats
        self.database_filename = database_filename
        self.f = None
        self.program_name = "Filer"
        if self.memory_stats:
            # Start tracing memory allocations
            tracemalloc.start()

    def question_yes_no(self, question: str, title: str = None) -> bool:
        logging.debug(f"### Program.question_yes_no() ###")
        return False

    def display_progress_percentage(self, progress_percentage: float = None):
        logging.debug(f"### Program.display_progress_percentage() ###")
        # By default, we don't want to print the progress in the console, as it's purely to update GUI progress bars.
        pass

    def start(self):
        logging.debug(f"### Program.start() ###")
        self.init()
        self.seed()
        self.main()

    def init(self):
        logging.debug(f"### Program.init() ###")
        logging.info(f"Initialising Argument Parser Arguments...")
        AddArgs.add_subcommands_to_parser(self.argument_parser)
        self.f = F(self, self.argument_parser, self.memory_stats, self.database_filename)
        # self.parser.set_defaults(**self.stored_args)

    def seed(self, clear: []=None):
        logging.info(f"### Program.seed() ###")

    def main(self):
        logging.info(f"### Program.main() ###")
        # Get the arguments
        args = self.argument_parser.parse_args()
        # Now process the args
        self.f.process_args_and_call_subcommand(args)