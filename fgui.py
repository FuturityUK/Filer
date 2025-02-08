import argparse
from gooey import Gooey, GooeyParser
from f import F

class Fgui:

    def __init__(self):
        pass

    @Gooey(
        program_name='Filer',
        required_cols=1,
        optional_cols=1,
        #navigation='TABBED',
        default_size=(1000, 1000),
        clear_before_run=True
    )
    def start(self):
        parser=GooeyParser(
            description="Filer - File Cataloger"
        )

        F.add_subcommands_to_parser(parser)

        args=parser.parse_args()

        f = F()
        f.process_args_and_call_subcommand(args)

if __name__ == "__main__":
    fgui = Fgui()
    fgui.start()
