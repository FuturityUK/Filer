import argparse
from gooey import Gooey, GooeyParser
from f import F

class Fgui:

    def __init__(self):
        pass

    @Gooey
    def start(self):
        parser=argparse.ArgumentParser(
        #    prog='Filer',
        #    epilog='Text at the bottom of help',
            description="Filer - File Cataloger")

        F.add_subcommands_to_parser(parser)

        args=parser.parse_args()

        f = F()
        f.process_args_and_call_subcommand(args)

if __name__ == "__main__":
    fgui = Fgui()
    fgui.start()
