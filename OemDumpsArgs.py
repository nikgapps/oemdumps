import argparse

from NikGapps.helper.Args import Args


class OemDumpsArgs(Args):
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description="NikGapps build command help!")
        self.parser.add_argument(
            '-F', '--fileName', help="It is the name of the file we're working on",
            default="", type=str)
        self.parser.add_argument(
            '-D', '--download', help="It is the url of the file we wish to download",
            default="", type=str)
        # self.parser.add_argument(
        #     '-e', '--eliteOnlyMode', help="Use this to choose what to build in user, elite, both",
        #     default="0", type=int)
        # self.parser.add_argument('-e', '--eliteOnly', help="Use this to build elite only builds", action="store_true")
        super().__init__(self.parser)
        args = self.parser.parse_args()
        self.fileName = args.fileName
        self.download = args.download
        # self.elite_only_mode = args.eliteOnlyMode

