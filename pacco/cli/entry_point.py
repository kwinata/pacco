import sys

from pacco.cli.commands.pacco import main


def run():
    """
    This method is being called by setup.py as the entry point.
    """
    main(sys.argv[1:])
