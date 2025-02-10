from f import F
#from gooey import Gooey, GooeyParser
import json
from dyngooey import Gooey, GooeyParser, gooey_stdout, gooey_id

class Fgui:

    def __init__(self):
        self.parser = GooeyParser(
            description="Filer - File Cataloger"
        )

    @staticmethod
    def dumps(data):
        return json.dumps(data, indent=4, default=str)

    def init(self):
        #"""
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
        #"""
        #F.add_subcommands_to_parser(self.parser)

    def seed(self, clear=None):
        if clear is None:
            clear = []
        if gooey_stdout():
            # NOTE:
            #  - None     => Clear/Initial value
            #  - not None => Dynamic value
            #  - missing  => Left alone
            dynamic_values = {
                'make': "Hello World!",
                'label2': "Hello Neil!",
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
            }

            print(f"_actions: {self.parser._actions}")
            #self.parser._subparsers._actions[0].choices = {}
            print(f"_subparsers: {self.parser._subparsers}")
            if self.parser._subparsers is not None:
                print(f"_subparsers._actions: {self.parser._subparsers._actions}")

            seeds = {}
            for action in self.parser._actions:
                print(f"action: {action}")
                print(f"type(action): {type(action)}")
                # Get the widget_id
                widget_id = gooey_id(action)
                print(f"widget_id: {widget_id}")
                # Assign the dictionary value from the seeds array to the action_seeds dictionary if it exists, otherwise assign an empty dictionary
                # The setdefault() method returns the value of the item with the specified key. If the key does not exist, insert the key, with the specified value
                action_seeds = seeds.setdefault(widget_id, {})
                print(f"action_seeds: {action_seeds}")
                print(f"action_seeds: {action_seeds}", file=gooey_stdout())
                if action.dest in dynamic_values:
                    action_seeds["value"] = dynamic_values[action.dest]
                if action.dest in dynamic_items:
                    pass
                    # action_seeds["items"] = dynamic_items[action.dest]

                if widget_id == "subcommand":
                    print(f"action.choices: {action.choices}")
                    parser_search = action.choices["search"]
                    print(f"parser_search: {parser_search}")
                    parser_add_volume = action.choices["add_volume"]
                    parser_import = action.choices["import"]
                    parser_create = action.choices["create"]
                    parser_upgrade = action.choices["upgrade"]
                    parser_vacuum = action.choices["vacuum"]
                    parser_reset = action.choices["reset"]
                    print(f"Hello")

            print(self.dumps(seeds), file=gooey_stdout())

    @Gooey(
        program_name='Filer',
        required_cols=1,
        optional_cols=1,
        #navigation='TABBED',
        default_size=(1000, 1000),
        clear_before_run=False # Was True
    )
    def main(self):
        args = self.parser.parse_args()
        if not gooey_stdout():
            print(f"Program arguments:")
            print(f"{Fgui.dumps(vars(args))}")

        f = F()
        f.process_args_and_call_subcommand(args)

if __name__ == "__main__":
    fgui = Fgui()
    fgui.init()
    fgui.seed()
    fgui.main()

