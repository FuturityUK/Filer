from f import F
from dyngooey import Gooey, GooeyParser, gooey_stdout, gooey_id
import logging
import sys

class Fgui:

    def __init__(self, database_filename: str = None):
        logging.debug(f"### __init__() ###")
        self.parser = GooeyParser(
            #description="Filer - File Cataloger",
            description='Some words'#, formatter_class=CustomHelpFormatter
        )
        self.f = F(self.parser, database_filename)

    def init(self):
        logging.debug(f"### init() ###")
        self.f.init()

    def seed(self, clear=None):
        logging.debug(f"### seed() ###")
        logging.info(f"Seeding Argument Parser Values...")

        if clear is None:
            clear = []
        if gooey_stdout():
            logging.debug(f"gooey_stdout detected")

            # NOTE:
            #  - None     => Clear/Initial value
            #  - not None => Dynamic value
            #  - missing  => Left alone

            # Load labels
            label_choices = [""]
            label_choices = [*label_choices, *self.f.database.find_filesystem_labels()]
            logging.debug(f"label_choices: {label_choices}")
            label_choice = self.f.get_configuration_value(self.f.CONFIG_CHOSEN_LABEL, None)
            #label_choice = self.f.configuration[self.f.CONFIG_ARGS]["label"]
            logging.debug(f"label_choice: {label_choice}")

            volume_default_choice = None
            volume_choices = []
            vol_details = self.f.configuration[self.f.CONFIG_VOL_DETAILS]
            if len(vol_details) != 0:
                volume_default_choice = vol_details[self.f.VOL_ARG_DETAILS_DEFAULT_CHOICE]
                logging.info(f"vol_details[\"{self.f.VOL_ARG_DETAILS_DEFAULT_CHOICE}\"]: {volume_default_choice}")
                volume_choices = vol_details[self.f.VOL_ARG_DETAILS_CHOICES]
                logging.info(f"vol_details\"{self.f.VOL_ARG_DETAILS_CHOICES}\"]: {volume_choices}")

            dynamic_values = {
                'volume': volume_default_choice,
                'db': self.f.database_filename,
                'label': label_choice,
                'test_required_1': None,  # This will be replaced with the initial value
                # 'test_required_2' will be left alone
                'test_optional_1': None,
                'test_optional_2': None,
                'test_optional_3': "Hello World!",
                'test_store_true': None,
                # 'test_store_false' will be left alone
                'test_store_const': None
            }
            logging.info(f"dynamic_values: {dynamic_values}")

            dynamic_items = {
                #'test_optional_2': [
                #    f'Random entry {i}' for i in range(__import__('random').randrange(30))
                #],
                'volume': volume_choices,
                'label': label_choices
                #'volume': ["Neil", baker]
            }
            logging.info(f"dynamic_items: {dynamic_items}")

            logging.debug(f"_actions: {self.parser._actions}")

            seeds = {}
            seeds = self.process_actions(self.parser, seeds, dynamic_values, dynamic_items)
            logging.info(f"seeds: {seeds}")
            logging.info(f"")

            logging.info(f"self.dumps(seeds): {F.dumps(seeds)}")
            logging.info(f"")

            print(F.dumps(seeds), file=gooey_stdout())
            logging.info(f"Past the dump to gooey_stdout()")


    @staticmethod
    def process_actions(parser, seeds: {}, dynamic_values: {}, dynamic_items: {}) -> {}:
        logging.info(f"### process_actions() ###")

        for action in parser._actions:
            logging.debug(f"action: {action}")
            action_type_name = type(action).__name__
            #logging.info(f"type(action).__name__: {action_type_name}")
            if action_type_name != "_SubParsersAction":
                # Get the widget_id
                widget_id = gooey_id(action)
                logging.info(f"widget_id: {widget_id}")
                # Assign the dictionary value from the seeds array to the action_seeds dictionary if it exists, otherwise assign an empty dictionary
                # The setdefault() method returns the value of the item with the specified key. If the key does not exist, insert the key, with the specified value
                action_seeds = seeds.setdefault(widget_id, {})
                #logging.info(f"action_seeds (before): {action_seeds}")
                #logging.info(f"seeds (before): {seeds}")
                # NOTE: Matches based on the dest value, but the 'seeds' dictionary uses:
                # for non-optional parameters: the dest value
                # for optional parameters: the first option string ('-h', when '-h' & '--help')
                if action.dest in dynamic_items:
                    action_seeds["items"] = dynamic_items[action.dest]
                if action.dest in dynamic_values:
                    action_seeds["value"] = dynamic_values[action.dest]

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
            program_name='Filer', # Overrides name pulled from sys.argv[0]
            program_description = 'Filer - File Cataloger', # Overrides the description pulled from ArgumentParser
            required_cols=1,
            optional_cols=1,
            navigation='TABBED',
            default_size=(1024, 768),
            #fullscreen=True,
            show_restart_button=False,
            hide_progress_msg=True,
            clear_before_run=True,# Was True
            show_stop_warning=False, # From test.py
            show_success_modal=False, # From test.py
            show_failure_modal=False # From test.py
            #dump_build_config = True,  # Dump the JSON Gooey uses to configure itself
            #load_build_config = 'gooey_config.json'  # Loads a JSON Gooey-generated configuration
        )
    #@Gooey(optional_cols=2, program_name="Subparser Layout Demo")
    def main(self):
        logging.info(f"### main() ###")
        args = self.parser.parse_args()

        if not gooey_stdout():
            if F.SHOW_SUBMITTED_ARGS:
                # Debug to show arguments past to the program
                print(f"Program arguments:")
                print(f"{F.dumps(vars(args))}")
                print(f"")

        # Now process the args
        self.f.main()

def print_help_and_exit():
    print("Filer - File Cataloger")
    print("Usage: filer.py [options]")
    print("Options:")
    print("  -h, --help                    show this help message and exit")
    print("  -d, --db <database_filename>  specify the database filename")
    sys.exit(0)

if __name__ == "__main__":
    #my_logger = logging.getLogger(__name__)
    F.start_logger(logging.DEBUG)
    logging.info(f"### __main__ ###")

    # total arguments
    n = len(sys.argv)
    logging.debug(f"Total arguments passed: {n}")

    # Arguments passed
    logging.debug(f"Name of Python script: {sys.argv[0]}")

    logging.debug("Arguments passed:")
    for i in range(1, n):
        logging.debug(f"- {sys.argv[i]}")

    db_filename = None
    if len(sys.argv) >= 2:
        if sys.argv[1].startswith("-"):
            option = sys.argv[1]
            if option == "-h" or option == "--help":
                print_help_and_exit()
            elif option == "-d" or option == "--db":
                #print("'--db' option detected")
                if len(sys.argv) >= 3:
                    db_filename = sys.argv[2]
                    print(f"db_filename: {db_filename}")
                else:
                    print("<database_filename> not specified.")
                    print("")
                    print_help_and_exit()
            else:
                print("Unrecognised option.")
                print("")
                print_help_and_exit()

    fgui = Fgui(db_filename)
    fgui.init()
    fgui.seed()
    fgui.main()




