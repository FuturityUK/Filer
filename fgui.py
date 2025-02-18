from f import F
import json
from dyngooey import Gooey, GooeyParser, gooey_stdout, gooey_id
import logging

class Fgui:

    def __init__(self):
        logging.debug(f"### __init__() ###")
        self.parser = GooeyParser(
            description="Filer - File Cataloger"
        )
        self.f = F()
        self.volume_argument_details = {}
        self.counter = 69

    @staticmethod
    def dumps(data):
        logging.debug(f"### dumps() ###")
        return json.dumps(data, indent=4, default=str)

    def init(self):
        logging.debug(f"### init() ###")
        logging.info(f"Initialising Argument Parser Arguments...")
        """
        self.parser.add_argument(
            'test_required_1',
            gooey_options={
                'initial_value': 'Initial values will be kept!'
            }
        )

        self.parser.add_argument(
            'test_required_2'
        )

        self.parser.add_argument(
            '-t', '--test-optional-1',
            dest='test_optional_1'
        )

        self.parser.add_argument(
            '--test-optional-2',
            dest='test_optional_2',
            widget='Dropdown'
        )

        self.parser.add_argument(
            '--test-optional-3',
            dest='test_optional_3'
        )

        self.parser.add_argument(
            '--test-store-true',
            dest='test_store_true',
            action='store_true'
        )

        self.parser.add_argument(
            '--test-store-false',
            dest='test_store_false',
            action='store_false'
        )

        self.parser.add_argument(
            '--test-store-const',
            dest='test_store_const',
            action='store_const',
            const=10
        )
        """
        self.f.add_subcommands_to_parser(self.parser)

    def seed(self, clear=None):
        logging.debug(f"### seed() ###")
        logging.info(f"Seeding Argument Parser Values...")
        self.counter += 1
        logging.info(f"self.counter: {self.counter}")
        if clear is None:
            clear = []
        if gooey_stdout():
            logging.debug(f"gooey_stdout detected")

            # NOTE:
            #  - None     => Clear/Initial value
            #  - not None => Dynamic value
            #  - missing  => Left alone
            volume_default_choice = None
            volume_choices = []
            if len(self.volume_argument_details) != 0:
                volume_default_choice = self.volume_argument_details["volume_default_choice"]
                logging.debug(f"self.f.volume_argument_details[\"volume_default_choice\"]: {volume_default_choice}")
                volume_choices = self.volume_argument_details["volume_choices"]
                logging.debug(f"self.f.volume_argument_details[\"volume_choices\"]: {volume_choices}")

            dynamic_values = {
                'volume': volume_default_choice,
                'make6': "Hello World!",
                'label': "Hello Neil!",
                'make': str(self.counter),
                'test_required_1': None,  # This will be replaced with the initial value
                # 'test_required_2' will be left alone
                'test_optional_1': None,
                'test_optional_2': None,
                'test_optional_3': "Hello World!",
                'test_store_true': None,
                # 'test_store_false' will be left alone
                'test_store_const': None
            }

            dynamic_items = {
                'test_optional_2': [
                    f'Random entry {i}' for i in range(__import__('random').randrange(30))
                ],
                'volume': volume_choices
            }

            logging.debug(f"_actions: {self.parser._actions}")

            seeds = {}
            seeds = self.process_actions(self.parser, seeds, dynamic_values, dynamic_items)
            logging.info(f"")

            """
            #self.parser._subparsers._actions[0].choices = {}
            logging.info(f"_SubParsersAction: {self.parser._actions._SubParsersAction}")
            #if self.parser._subparsers is not None:
            if self.parser._actions._SubParsersAction is not None:
                logging.info(f"_subparsers._actions: {self.parser._actions._SubParsersAction}")
                logging.info(f"_subparsers._actions: {self.parser._subparsers._actions}")
            """
            logging.debug(f"seeds: {seeds}")
            logging.debug(f"")
            logging.debug(f"self.dumps(seeds): {self.dumps(seeds)}")
            logging.debug(f"")

            print(self.dumps(seeds), file=gooey_stdout())

    @staticmethod
    def process_actions(parser, seeds: {}, dynamic_values: {}, dynamic_items: {}) -> {}:
        logging.debug(f"### process_actions() ###")

        for action in parser._actions:
            logging.debug(f"action: {action}")
            action_type_name = type(action).__name__
            #logging.info(f"type(action).__name__: {action_type_name}")
            if action_type_name != "_SubParsersAction":
                # Get the widget_id
                widget_id = gooey_id(action)
                logging.debug(f"widget_id: {widget_id}")
                # Assign the dictionary value from the seeds array to the action_seeds dictionary if it exists, otherwise assign an empty dictionary
                # The setdefault() method returns the value of the item with the specified key. If the key does not exist, insert the key, with the specified value
                action_seeds = seeds.setdefault(widget_id, {})
                #logging.info(f"action_seeds (before): {action_seeds}")
                #logging.info(f"seeds (before): {seeds}")
                # NOTE: Matches based on the dest value, but the 'seeds' dictionary uses:
                # for non-optional parameters: the dest value
                # for optional parameters: the first option string ('-h', when '-h' & '--help')
                if action.dest in dynamic_values:
                    action_seeds["value"] = dynamic_values[action.dest]
                if action.dest in dynamic_items:
                    pass
                    action_seeds["items"] = dynamic_items[action.dest]

                #logging.info(f"action_seeds (after): {action_seeds}")
                #logging.info(f"seeds (after): {seeds}")
                logging.debug(f"")
            else:
                subparser_id = gooey_id(action)
                logging.debug(f"subparser_id: {subparser_id}")
                subparser_choices = action.choices
                #logging.info(f"action.choices: {subparser_choices}")
                if subparser_choices is not None:
                    for subparser_choice_key, subparser_choice_value in subparser_choices.items():
                        logging.debug(f"subparser_choice_key: {subparser_choice_key}")
                        #logging.info(f"subparser_choice_value: {subparser_choice_value}")
                        seeds = Fgui.process_actions(subparser_choice_value, seeds, dynamic_values, dynamic_items)

        return seeds

    @Gooey(
            program_name='Filer',
            required_cols=1,
            optional_cols=1,
            #navigation='TABBED',
            default_size=(1000, 1000),
            clear_before_run=False,# Was True
            show_stop_warning=False, # From test.py
            show_success_modal=False, # From test.py
            show_failure_modal=False # From test.py
            #dump_build_config = True,  # Dump the JSON Gooey uses to configure itself
            #load_build_config = 'gooey_config.json'  # Loads a JSON Gooey-generated configuration
        )
    def main(self):
        logging.debug(f"### main() ###")
        print(f"START: len(f.volume_argument_details): {len(self.volume_argument_details)}")
        args = self.parser.parse_args()
        if not gooey_stdout():
            print(f"Program arguments:")
            print(f"{Fgui.dumps(vars(args))}")


        f = F()
        f.process_args_and_call_subcommand(args)
        self.volume_argument_details = f.volume_argument_details
        print(f"END  : len(f.volume_argument_details): {len(self.volume_argument_details)}")

if __name__ == "__main__":
    F.start_logger(logging.INFO)
    fgui = Fgui()
    fgui.init()
    fgui.seed()
    fgui.main()


