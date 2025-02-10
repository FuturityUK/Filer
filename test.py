
import json

from dyngooey import Gooey, GooeyParser, gooey_stdout, gooey_id


# --------------------------------------------------------------------------- #

def dumps(data):
    return json.dumps(data, indent=4, default=str)

def init(parser):

    parser.add_argument(
        'test_required_1',
        gooey_options={
            'initial_value': 'Initial values will be kept!'
        }
    )

    parser.add_argument(
        'test_required_2'
    )

    parser.add_argument(
        '-t', '--test-optional-1',
        dest='test_optional_1'
    )

    parser.add_argument(
        '--test-optional-2',
        dest='test_optional_2',
        widget='Dropdown'
    )

    parser.add_argument(
        '--test-optional-3',
        dest='test_optional_3'
    )

    parser.add_argument(
        '--test-store-true',
        dest='test_store_true',
        action='store_true'
    )

    parser.add_argument(
        '--test-store-false',
        dest='test_store_false',
        action='store_false'
    )

    parser.add_argument(
        '--test-store-const',
        dest='test_store_const',
        action='store_const',
        const=10
    )


def seed(parser, clear=[]):
    if gooey_stdout():

        # NOTE:
        #  - None     => Clear/Initial value
        #  - not None => Dynamic value
        #  - missing  => Left alone
        dynamic_values = {
            'test_required_1': None, # This will be replaced with the initial value
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

        seeds = {}
        for action in parser._actions:
            action_seeds = seeds.setdefault(gooey_id(action), {})
            if action.dest in dynamic_values:
                action_seeds["value"] = dynamic_values[action.dest]
            if action.dest in dynamic_items:
                pass
                #action_seeds["items"] = dynamic_items[action.dest]

        print(dumps(seeds), file=gooey_stdout())

@Gooey(
    default_size=(680, 640),
    show_stop_warning=False,
    show_success_modal=False,
    show_failure_modal=False,
    clear_before_run=True
)
def main(parser):
    if not gooey_stdout():
        args = parser.parse_args()

        print(f"Program arguments:")
        print(f"{dumps(vars(args))}")


# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    parser = GooeyParser()
    init(parser)
    seed(parser)
    main(parser)
